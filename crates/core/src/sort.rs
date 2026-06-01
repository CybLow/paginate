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
pub enum SortDirection {
    Asc,
    Desc,
}

/// Where nulls are placed relative to non-null values.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NullsPosition {
    First,
    Last,
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
        let mut failure: Option<CoreError> = None;
        order.sort_by(|&a, &b| {
            if failure.is_some() {
                return Ordering::Equal;
            }
            match compare_keys(&items[a], &items[b], &path, null_first) {
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

/// Compare two items by one key as the tuple `(null_flag, value)`.
fn compare_keys(a: &Value, b: &Value, path: &[String], null_first: bool) -> Result<Ordering> {
    let av = resolve_opt(a, path);
    let bv = resolve_opt(b, path);
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
mod tests {
    use super::*;
    use std::collections::BTreeMap;

    fn item(pairs: &[(&str, Value)]) -> Value {
        let mut map = BTreeMap::new();
        for (key, value) in pairs {
            map.insert((*key).to_owned(), value.clone());
        }
        Value::Map(map)
    }

    fn by(field: &str, direction: SortDirection, nulls: NullsPosition) -> SortSpec {
        SortSpec {
            field: field.to_owned(),
            direction,
            nulls,
        }
    }

    #[test]
    fn ascending_and_descending() {
        let items = vec![
            item(&[("n", Value::Int(3))]),
            item(&[("n", Value::Int(1))]),
            item(&[("n", Value::Int(2))]),
        ];
        let asc =
            sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]).unwrap();
        assert_eq!(asc, vec![1, 2, 0]);
        let desc =
            sort_indices(&items, &[by("n", SortDirection::Desc, NullsPosition::Last)]).unwrap();
        assert_eq!(desc, vec![0, 2, 1]);
    }

    #[test]
    fn null_placement() {
        let items = vec![
            item(&[("n", Value::Int(2))]),
            item(&[("n", Value::Null)]),
            item(&[("n", Value::Int(1))]),
        ];
        let last =
            sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]).unwrap();
        assert_eq!(last, vec![2, 0, 1]); // 1, 2, null
        let first =
            sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::First)]).unwrap();
        assert_eq!(first, vec![1, 2, 0]); // null, 1, 2
    }

    #[test]
    fn desc_keeps_nulls_last_when_requested() {
        let items = vec![
            item(&[("n", Value::Int(1))]),
            item(&[("n", Value::Null)]),
            item(&[("n", Value::Int(2))]),
        ];
        let idx =
            sort_indices(&items, &[by("n", SortDirection::Desc, NullsPosition::Last)]).unwrap();
        assert_eq!(idx, vec![2, 0, 1]); // 2, 1, null
    }

    #[test]
    fn multi_key_is_stable() {
        // Sort by group ASC, then by id ASC. Ties on group keep id order.
        let items = vec![
            item(&[("g", Value::Int(1)), ("id", Value::Int(2))]),
            item(&[("g", Value::Int(1)), ("id", Value::Int(1))]),
            item(&[("g", Value::Int(0)), ("id", Value::Int(9))]),
        ];
        let idx = sort_indices(
            &items,
            &[
                by("g", SortDirection::Asc, NullsPosition::Last),
                by("id", SortDirection::Asc, NullsPosition::Last),
            ],
        )
        .unwrap();
        assert_eq!(idx, vec![2, 1, 0]);
    }

    #[test]
    fn missing_field_treated_as_null() {
        let items = vec![
            item(&[("n", Value::Int(1))]),
            item(&[("other", Value::Int(9))]),
        ];
        let idx =
            sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]).unwrap();
        assert_eq!(idx, vec![0, 1]); // present first, missing (null) last
    }

    #[test]
    fn incomparable_values_error() {
        let items = vec![
            item(&[("n", Value::Int(1))]),
            item(&[("n", Value::Str("x".into()))]),
        ];
        let err = sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]);
        assert!(matches!(err, Err(CoreError::Sort { .. })));
    }
}
