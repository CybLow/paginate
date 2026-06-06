//! Stable, multi-key in-memory sort with null placement.
//!
//! Faithful port of pypaginate's `sorting/`:
//!
//! * Each spec contributes a `(null_flag, value)` key; `reverse` (for DESC) is
//!   applied to the whole key so null placement stays independent of direction.
//! * Specs are applied in **reverse priority order** with a **stable** sort, so
//!   the first spec wins ties — identical to Python's repeated `list.sort`.
//! * A missing field or an explicit null is treated as null (the Python engine
//!   catches the accessor error); incomparable values raise [`CoreError::Sort`].
//!
//! [`sort_indices`] returns a permutation so the binding can reorder the
//! original host objects without cloning them through the core.

use std::cmp::Ordering;

use crate::accessor::{compile_path, resolve_opt};
use crate::coerce;
use crate::error::{CoreError, Result};
use crate::value::Value;

/// Sort direction.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum SortDirection {
    /// Ascending order.
    Asc,
    /// Descending order.
    Desc,
}

impl SortDirection {
    /// Parse the wire token (`"asc"` / `"desc"`) shared by every binding.
    ///
    /// # Errors
    /// [`CoreError::Sort`] for any other token.
    pub fn from_token(token: &str) -> Result<Self> {
        match token {
            "asc" => Ok(Self::Asc),
            "desc" => Ok(Self::Desc),
            other => Err(CoreError::Sort {
                message: format!("unknown sort direction: {other}"),
            }),
        }
    }
}

/// Where nulls are placed relative to non-null values.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum NullsPosition {
    /// Nulls sort before non-null values.
    First,
    /// Nulls sort after non-null values.
    Last,
}

impl NullsPosition {
    /// Parse the wire token (`"first"` / `"last"`) shared by every binding.
    ///
    /// # Errors
    /// [`CoreError::Sort`] for any other token.
    pub fn from_token(token: &str) -> Result<Self> {
        match token {
            "first" => Ok(Self::First),
            "last" => Ok(Self::Last),
            other => Err(CoreError::Sort {
                message: format!("unknown nulls position: {other}"),
            }),
        }
    }
}

/// A single sort key.
#[derive(Debug, Clone)]
pub struct SortSpec {
    /// Dotted field path to sort by.
    pub field: String,
    /// Ascending or descending.
    pub direction: SortDirection,
    /// Null placement.
    pub nulls: NullsPosition,
}

/// Return a permutation of `items` indices sorted by `specs` (first = highest
/// priority). With no specs the original order is returned.
///
/// # Errors
/// [`CoreError::Filter`] for a path segment starting with `_`, or
/// [`CoreError::Sort`] when two field values are not order-comparable.
pub fn sort_indices(items: &[Value], specs: &[SortSpec]) -> Result<Vec<usize>> {
    sort_indices_of(items, (0..items.len()).collect(), specs)
}

/// Sort an existing index list (a subset/permutation of `items`) by `specs`,
/// preserving its relative order for equal keys (stable). The pipeline uses this
/// to sort a *filtered* subset without disturbing the rest.
///
/// # Errors
/// See [`sort_indices`].
pub fn sort_indices_of(
    items: &[Value],
    mut order: Vec<usize>,
    specs: &[SortSpec],
) -> Result<Vec<usize>> {
    if specs.is_empty() {
        return Ok(order);
    }
    // Apply specs in reverse so the first spec has highest priority under a
    // stable sort — exactly how the Python engine layers `list.sort` calls.
    for spec in specs.iter().rev() {
        let path = compile_path(&spec.field)?;
        let null_first = null_sorts_first(spec.direction, spec.nulls);
        let reverse = spec.direction == SortDirection::Desc;
        // Decorate: resolve each item's sort key ONCE, not on every comparison
        // (a comparison sort does O(n log n) compares — re-resolving the field
        // each time dominated the cost). `keys[i]` borrows item `i`'s value.
        let keys: Vec<Option<&Value>> = items.iter().map(|it| resolve_opt(it, &path)).collect();
        let mut failure: Option<CoreError> = None;
        order.sort_by(|&a, &b| {
            if failure.is_some() {
                return Ordering::Equal;
            }
            match compare_keys(keys[a], keys[b], null_first) {
                Ok(ordering) if reverse => ordering.reverse(),
                Ok(ordering) => ordering,
                Err(err) => {
                    failure = Some(err);
                    Ordering::Equal
                }
            }
        });
        if let Some(err) = failure {
            return Err(err);
        }
    }
    Ok(order)
}

/// Convenience wrapper around [`sort_indices`] that clones items into order.
///
/// # Errors
/// See [`sort_indices`].
pub fn apply(items: &[Value], specs: &[SortSpec]) -> Result<Vec<Value>> {
    let order = sort_indices(items, specs)?;
    Ok(order.into_iter().map(|i| items[i].clone()).collect())
}

fn null_sorts_first(direction: SortDirection, nulls: NullsPosition) -> bool {
    (nulls == NullsPosition::First) != (direction == SortDirection::Desc)
}

/// Compare two precomputed keys as the tuple `(null_flag, value)`.
fn compare_keys(av: Option<&Value>, bv: Option<&Value>, null_first: bool) -> Result<Ordering> {
    let a_flag = null_first ^ av.is_none();
    let b_flag = null_first ^ bv.is_none();
    if a_flag != b_flag {
        return Ok(a_flag.cmp(&b_flag));
    }
    match (av, bv) {
        (Some(x), Some(y)) => coerce::compare(x, y).ok_or_else(|| CoreError::Sort {
            message: "field values are not order-comparable".to_owned(),
        }),
        _ => Ok(Ordering::Equal),
    }
}

#[cfg(test)]
mod tests;
