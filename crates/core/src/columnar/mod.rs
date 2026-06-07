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
//! A `Str` column also serves the substring operators (`contains`/`starts_with`/
//! `ends_with`) via a direct scan — byte-identical to the row engine's `str`
//! methods, but without the per-row accessor walk and boxed-predicate dispatch.
//!
//! Anything else — an unknown field, `like`/`ilike`/`regex`, a range, a value
//! whose coercion can't be proven equal — returns `None`, and the caller falls
//! back to the row engine. Silently correct beats cleverly wrong.
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
    /// `limit` keeps only the first `k` rows (a top-k partial sort) — the page
    /// window — instead of fully ordering the whole subset; `None` sorts all.
    #[must_use]
    pub fn sort_subset(
        &self,
        order: &[usize],
        keys: &[(&str, SortDirection)],
        limit: Option<usize>,
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
        // A single-key sort (the common case) gets a comparator specialised to the
        // column type — no per-comparison `Column` enum match, which profiling
        // showed dominates once the full sort became a top-k. Multi-key uses one
        // total comparator (keys in priority order). Both break ties by ascending
        // item index (stable, since `order` is ascending) and honour `limit`.
        if let [(column, desc)] = resolved.as_slice() {
            sort_one_key(&mut order, column, *desc, limit);
        } else {
            partial_sort(&mut order, limit, |&a, &b| {
                for (column, desc) in &resolved {
                    let ord = oriented(column.compare(a, b), *desc);
                    if ord != Ordering::Equal {
                        return ord;
                    }
                }
                a.cmp(&b)
            });
        }
        Some(order)
    }
}

impl Column {
    /// Compare two rows by this column's natural (ascending) order. A built float
    /// column has no `NaN`, so `partial_cmp` is total.
    fn compare(&self, a: usize, b: usize) -> Ordering {
        match self {
            Column::Int(col) => col[a].cmp(&col[b]),
            Column::Float(col) => col[a].partial_cmp(&col[b]).unwrap_or(Ordering::Equal),
            Column::Str(col) => col[a].cmp(&col[b]),
            Column::Bool(col) => col[a].cmp(&col[b]),
        }
    }
}

/// Single-key sort with a comparator specialised to the column's element type
/// (ties broken by ascending item index for stability). The `Ord` columns share
/// one generic body — the compiler still monomorphises it per type, so each gets
/// an enum-match-free comparator; `Float` is separate (`f64` is only `PartialOrd`).
fn sort_one_key(order: &mut Vec<usize>, column: &Column, desc: bool, limit: Option<usize>) {
    match column {
        Column::Int(c) => sort_by_key(order, c, desc, limit),
        Column::Str(c) => sort_by_key(order, c, desc, limit),
        Column::Bool(c) => sort_by_key(order, c, desc, limit),
        Column::Float(c) => partial_sort(order, limit, |&a, &b| {
            oriented(c[a].partial_cmp(&c[b]).unwrap_or(Ordering::Equal), desc)
                .then_with(|| a.cmp(&b))
        }),
    }
}

/// Top-k/full sort of `order` by one totally-ordered column, descending-aware,
/// ties by ascending item index.
fn sort_by_key<T: Ord>(order: &mut Vec<usize>, col: &[T], desc: bool, limit: Option<usize>) {
    partial_sort(order, limit, |&a, &b| {
        oriented(col[a].cmp(&col[b]), desc).then_with(|| a.cmp(&b))
    });
}

/// Sort `order` by `cmp`, keeping only the first `k` rows when `limit` is `Some(k)`
/// (a top-k partial sort for a bounded page); a `None`/large limit sorts all.
fn partial_sort(
    order: &mut Vec<usize>,
    limit: Option<usize>,
    mut cmp: impl FnMut(&usize, &usize) -> Ordering,
) {
    match limit {
        Some(0) => order.clear(),
        Some(k) if k < order.len() => {
            order.select_nth_unstable_by(k - 1, &mut cmp);
            order.truncate(k);
            order.sort_unstable_by(&mut cmp);
        }
        _ => order.sort_unstable_by(&mut cmp),
    }
}

/// Reverse an ordering for descending sorts.
fn oriented(ordering: Ordering, desc: bool) -> Ordering {
    if desc {
        ordering.reverse()
    } else {
        ordering
    }
}

#[cfg(test)]
mod tests;
