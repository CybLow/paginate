//! The pipeline's per-stage index resolution: each stage takes the columnar fast
//! path when it provably matches the row engine, else falls back to the row
//! engine. Kept separate from the orchestration ([`super`]) so the fast-path
//! reasoning lives in one place.

use std::cmp::Ordering;

use crate::columnar::Columns;
use crate::error::Result;
use crate::filter::{self, FilterInput, FilterLogic};
use crate::sort::{self, SortDirection, SortSpec};
use crate::value::Value;

/// Resolve the filter stage to a set of indices: columnar fast path for a single
/// comparison when it applies, else the row engine.
pub(super) fn filter_stage(
    items: &[Value],
    columns: Option<&Columns>,
    filter: Option<&FilterInput>,
) -> Result<Vec<usize>> {
    let Some(input) = filter else {
        return Ok((0..items.len()).collect());
    };
    if let Some(indices) = columnar_filter(columns, input) {
        return Ok(indices);
    }
    filter::filter_indices(items, input)
}

/// Columnar fast path for a flat, all-`AND` filter where every spec is a typed
/// single comparison: intersect the per-spec index sets (identical to the row
/// engine's all-`AND` `Flat`). Any `OR`, nested group, empty list, or
/// non-columnar spec returns `None` to fall back.
fn columnar_filter(columns: Option<&Columns>, filter: &FilterInput) -> Option<Vec<usize>> {
    let cols = columns?;
    let FilterInput::Flat(specs) = filter else {
        return None;
    };
    if specs.is_empty() || specs.iter().any(|s| s.logic != FilterLogic::And) {
        return None;
    }
    let mut result: Option<Vec<usize>> = None;
    for spec in specs {
        let matched = cols.filter(&spec.field, spec.op, &spec.value)?;
        result = Some(match result {
            Some(acc) => intersect_sorted(&acc, &matched),
            None => matched,
        });
    }
    result
}

/// Intersection of two ascending index lists, preserving ascending order.
fn intersect_sorted(a: &[usize], b: &[usize]) -> Vec<usize> {
    let mut out = Vec::new();
    let (mut i, mut j) = (0, 0);
    while i < a.len() && j < b.len() {
        match a[i].cmp(&b[j]) {
            Ordering::Less => i += 1,
            Ordering::Greater => j += 1,
            Ordering::Equal => {
                out.push(a[i]);
                i += 1;
                j += 1;
            }
        }
    }
    out
}

/// Sort the filtered indices: columnar fast path when every sort key is a typed
/// column, else the row engine.
pub(super) fn sort_stage(
    items: &[Value],
    columns: Option<&Columns>,
    indices: Vec<usize>,
    sort_specs: &[SortSpec],
    limit: Option<usize>,
) -> Result<Vec<usize>> {
    if sort_specs.is_empty() {
        return Ok(indices);
    }
    if let Some(sorted) = columnar_sort(columns, &indices, sort_specs, limit) {
        return Ok(sorted);
    }
    // Row fallback sorts the whole subset (its multi-pass stable sort can't take
    // a partial top-k without changing tie semantics); the caller still slices.
    sort::sort_indices_of(items, indices, sort_specs)
}

/// Multi-key columnar sort when every key is a typed column, else `None`. `limit`
/// keeps only the first k rows (top-k) — the page window.
fn columnar_sort(
    columns: Option<&Columns>,
    indices: &[usize],
    sort_specs: &[SortSpec],
    limit: Option<usize>,
) -> Option<Vec<usize>> {
    let keys: Vec<(&str, SortDirection)> = sort_specs
        .iter()
        .map(|spec| (spec.field.as_str(), spec.direction))
        .collect();
    columns?.sort_subset(indices, &keys, limit)
}
