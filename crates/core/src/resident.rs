//! Single-operation queries over a *resident* dataset — the host rows marshalled
//! once into [`Value`] plus their prebuilt typed [`Columns`].
//!
//! Each query takes the columnar fast path when it provably matches the row
//! engine, else falls back to the row engine. The PyO3 and napi `Dataset.filter`
//! / `Dataset.sort` bindings call these so both languages share one fast-path-or-
//! fallback implementation and cannot drift (the multi-stage `Dataset.page` path
//! lives in [`crate::pipeline`]).

use crate::columnar::Columns;
use crate::error::Result;
use crate::filter::{self, FilterInput, FilterSpec};
use crate::sort::{self, SortDirection, SortSpec};
use crate::value::Value;

/// Indices of `rows` matching `specs`, in original order: the single-spec
/// typed-column fast path when it applies, else the row engine.
///
/// # Errors
/// Propagates the row engine's errors (see [`filter::filter_indices`]).
pub fn filter_indices(
    rows: &[Value],
    columns: &Columns,
    specs: Vec<FilterSpec>,
) -> Result<Vec<usize>> {
    if let [spec] = specs.as_slice() {
        if let Some(indices) = columns.filter(&spec.field, spec.op, &spec.value) {
            return Ok(indices);
        }
    }
    filter::filter_indices(rows, &FilterInput::Flat(specs))
}

/// A permutation of `rows` indices for `specs`: the columnar multi-key sort when
/// every key is a typed column, else the row engine.
///
/// # Errors
/// Propagates the row engine's errors (see [`sort::sort_indices`]).
pub fn sort_indices(rows: &[Value], columns: &Columns, specs: &[SortSpec]) -> Result<Vec<usize>> {
    if !specs.is_empty() {
        let order: Vec<usize> = (0..rows.len()).collect();
        let keys: Vec<(&str, SortDirection)> = specs
            .iter()
            .map(|s| (s.field.as_str(), s.direction))
            .collect();
        if let Some(sorted) = columns.sort_subset(&order, &keys, None) {
            return Ok(sorted);
        }
    }
    sort::sort_indices(rows, specs)
}
