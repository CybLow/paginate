//! Typed columns for a fast single-field filter and single-key sort path.
//!
//! The row engine resolves a `BTreeMap` lookup per item per field and dispatches
//! on `Value`; for a tight `age >= 500` / `name == "x"` / `price < 9.99` query
//! that overhead dominates. When a field holds the **same scalar type in every
//! row**, we keep it as a dense typed `Vec` (`i64`/`f64`/`String`) and scan it
//! directly — no map lookup, no `Value` dispatch.
//!
//! Correctness over cleverness. A column is built **only** if the field is that
//! exact scalar in every row (no missing, null, mixed, or — for floats — `NaN`),
//! and a fast path is taken **only** for operators whose typed comparison
//! provably equals the row engine's [`coerce`] semantics:
//!
//! * **Int** — exact `i64` order and equality (matches `coerce::compare`'s exact
//!   `(Int, Int)` arm and, after the matching fix, `coerce::eq`).
//! * **Float** — `f64` order/equality after coercing the needle through
//!   [`coerce::as_number`] (so `price > 5` works); a `NaN` needle or column is
//!   never fast-pathed (it would error/short-circuit in the row engine).
//! * **Str** — byte order (== Unicode code-point order for UTF-8, which is what
//!   `coerce::compare` uses) and exact equality.
//! * **Bool** — `false < true` (matches `coerce::compare`'s explicit
//!   `(Bool, Bool)` arm) and equality (bool `==` equals `coerce::eq`'s 0/1
//!   fold); only a `Bool` needle qualifies, so `active == 1` still falls back.
//!
//! Anything else — an unknown field, a string/regex operator, a value whose
//! coercion can't be proven equal — returns `None`, and the caller falls back to
//! the row engine. Silently correct beats cleverly wrong.
//!
//! [`coerce`]: crate::coerce

mod build;
mod filter;

use std::cmp::Ordering;
use std::collections::BTreeMap;

use crate::filter::FilterOp;
use crate::sort::SortDirection;
use crate::value::Value;

/// A dense, single-type column extracted from every row of a dataset.
pub(crate) enum Column {
    Int(Vec<i64>),
    Float(Vec<f64>),
    Str(Vec<String>),
    Bool(Vec<bool>),
}

/// Dense typed columns keyed by field name (only fully-typed, NaN-free fields).
pub struct Columns {
    columns: BTreeMap<String, Column>,
}

impl Columns {
    /// Build typed columns from `items`. A field qualifies only if it is the
    /// same scalar variant (`Int`/`Float`/`Str`) in every row — floats must also
    /// be non-`NaN`. The first row seeds the candidate type per field.
    #[must_use]
    pub fn build(items: &[Value]) -> Self {
        let mut columns = BTreeMap::new();
        let Some(Value::Map(first)) = items.first() else {
            return Self { columns };
        };
        for (field, seed) in first {
            if let Some(column) = build::build_column(items, field, seed) {
                columns.insert(field.clone(), column);
            }
        }
        Self { columns }
    }

    /// Fast filter for a single comparison/equality op on a typed column, or
    /// `None` when this path does not apply (unknown field, unsupported
    /// operator, or a value whose coercion can't be proven equal to the row
    /// engine). Returns matching indices in ascending order — identical to
    /// [`crate::filter::filter_indices`].
    #[must_use]
    pub fn filter(&self, field: &str, op: FilterOp, value: &Value) -> Option<Vec<usize>> {
        match self.columns.get(field)? {
            Column::Int(col) => filter::filter_int(col, op, value),
            Column::Float(col) => filter::filter_float(col, op, value),
            Column::Str(col) => filter::filter_str(col, op, value),
            Column::Bool(col) => filter::filter_bool(col, op, value),
        }
    }

    /// Sort an existing index list by one or more typed-column keys, preserving
    /// relative order for equal keys (stable). Returns `None` unless **every**
    /// key is a typed column. Keys are applied highest-priority first (matching
    /// [`crate::sort::sort_indices`]); typed columns have no nulls, so null
    /// placement is irrelevant.
    #[must_use]
    pub fn sort_subset(
        &self,
        order: &[usize],
        keys: &[(&str, SortDirection)],
    ) -> Option<Vec<usize>> {
        if keys.is_empty() {
            return None;
        }
        // Resolve every key first; if any field is not a typed column, fall back
        // (and avoid cloning `order`).
        let resolved: Vec<(&Column, bool)> = keys
            .iter()
            .map(|(field, direction)| {
                self.columns
                    .get(*field)
                    .map(|column| (column, *direction == SortDirection::Desc))
            })
            .collect::<Option<Vec<_>>>()?;
        let mut order = order.to_vec();
        // Apply keys in reverse so the first key wins under a stable sort —
        // exactly how the row engine layers its `sort_by` calls.
        for (column, desc) in resolved.iter().rev() {
            sort_one(&mut order, column, *desc);
        }
        Some(order)
    }
}

/// Stable-sort `order` in place by one typed column, oriented for descending.
fn sort_one(order: &mut [usize], column: &Column, desc: bool) {
    match column {
        Column::Int(col) => order.sort_by(|&a, &b| oriented(col[a].cmp(&col[b]), desc)),
        // A built float column has no NaN, so `partial_cmp` is total.
        Column::Float(col) => order.sort_by(|&a, &b| {
            oriented(col[a].partial_cmp(&col[b]).unwrap_or(Ordering::Equal), desc)
        }),
        Column::Str(col) => order.sort_by(|&a, &b| oriented(col[a].cmp(&col[b]), desc)),
        Column::Bool(col) => order.sort_by(|&a, &b| oriented(col[a].cmp(&col[b]), desc)),
    }
}

/// Reverse an ordering for descending sorts (keeps stability via `sort_by`).
fn oriented(ordering: Ordering, desc: bool) -> Ordering {
    if desc {
        ordering.reverse()
    } else {
        ordering
    }
}

#[cfg(test)]
mod tests;
