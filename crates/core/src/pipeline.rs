//! High-level pagination pipeline: filter → sort → offset-paginate in one pass,
//! returning the page's item indices plus offset metadata.
//!
//! This is the "do it all in the core" entry point. A host adapter passes the
//! specs once and gets the page's indices + metadata back in a single call — the
//! orchestration that pypaginate's `engine/pipeline.py` does in Python lives
//! here instead, so the host stays a thin adapter. (Search is applied by the
//! caller for now; a search stage can join this pass later.)

use std::cmp::Ordering;

use crate::columnar::Columns;
use crate::error::Result;
use crate::filter::{self, FilterInput, FilterLogic};
use crate::pagination;
use crate::sort::{self, SortDirection, SortSpec};
use crate::value::Value;

/// One page of results: indices into the original `items` (in final order) plus
/// offset metadata.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Page {
    /// Indices of this page's items, in final (filtered + sorted) order.
    pub indices: Vec<usize>,
    /// Total matched rows (after filtering), before paging.
    pub total: u64,
    /// The requested page number.
    pub page: u64,
    /// Total number of pages.
    pub pages: u64,
    /// Whether a following page exists.
    pub has_next: bool,
    /// Whether a preceding page exists.
    pub has_previous: bool,
}

/// Filter, then sort, then take one offset page — in a single pass.
///
/// `filter` is skipped when `None`; `sort_specs` is skipped when empty. When
/// `columns` is supplied, a single-comparison filter and a single-key sort take
/// the columnar fast path (identical results); everything else uses the row
/// engine. Mirrors pypaginate's `filter → sort → paginate` ordering.
///
/// # Errors
/// Propagates filter/sort errors from the underlying engines.
pub fn offset_page(
    items: &[Value],
    columns: Option<&Columns>,
    filter: Option<&FilterInput>,
    sort_specs: &[SortSpec],
    page: u64,
    limit: u64,
) -> Result<Page> {
    let filtered = filter_stage(items, columns, filter)?;
    let indices = sort_stage(items, columns, filtered, sort_specs)?;
    let total = indices.len() as u64;
    let meta = pagination::offset_meta(page, limit, total);
    let start = (pagination::offset(page, limit) as usize).min(indices.len());
    let end = start.saturating_add(limit as usize).min(indices.len());
    Ok(Page {
        indices: indices[start..end].to_vec(),
        total,
        page,
        pages: meta.pages,
        has_next: meta.has_next,
        has_previous: meta.has_previous,
    })
}

/// Resolve the filter stage to a set of indices: columnar fast path for a single
/// comparison when it applies, else the row engine.
fn filter_stage(
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
fn sort_stage(
    items: &[Value],
    columns: Option<&Columns>,
    indices: Vec<usize>,
    sort_specs: &[SortSpec],
) -> Result<Vec<usize>> {
    if sort_specs.is_empty() {
        return Ok(indices);
    }
    if let Some(sorted) = columnar_sort(columns, &indices, sort_specs) {
        return Ok(sorted);
    }
    sort::sort_indices_of(items, indices, sort_specs)
}

/// Multi-key columnar sort when every key is a typed column, else `None`.
fn columnar_sort(
    columns: Option<&Columns>,
    indices: &[usize],
    sort_specs: &[SortSpec],
) -> Option<Vec<usize>> {
    let keys: Vec<(&str, SortDirection)> = sort_specs
        .iter()
        .map(|spec| (spec.field.as_str(), spec.direction))
        .collect();
    columns?.sort_subset(indices, &keys)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::filter::{FilterLogic, FilterOp, FilterSpec};
    use crate::sort::{NullsPosition, SortDirection};
    use std::collections::BTreeMap;

    fn item(n: i64) -> Value {
        let mut map = BTreeMap::new();
        map.insert("n".to_owned(), Value::Int(n));
        Value::Map(map)
    }

    #[test]
    fn filter_sort_paginate_in_one_pass() {
        // n = 0..20; keep n >= 5 (15 rows); sort desc; page 1, limit 5.
        let items: Vec<Value> = (0..20).map(item).collect();
        let filter = FilterInput::Flat(vec![FilterSpec {
            field: "n".into(),
            op: FilterOp::Gte,
            value: Value::Int(5),
            logic: FilterLogic::And,
        }]);
        let sorts = [SortSpec {
            field: "n".into(),
            direction: SortDirection::Desc,
            nulls: NullsPosition::Last,
        }];
        let page = offset_page(&items, None, Some(&filter), &sorts, 1, 5).unwrap();
        assert_eq!(page.total, 15);
        assert_eq!(page.pages, 3);
        assert!(page.has_next);
        assert!(!page.has_previous);
        // n == original index here, so descending-from-19 gives these indices.
        assert_eq!(page.indices, vec![19, 18, 17, 16, 15]);
    }

    #[test]
    fn page_past_the_end_is_empty() {
        let items: Vec<Value> = (0..10).map(item).collect();
        let page = offset_page(&items, None, None, &[], 99, 5).unwrap();
        assert_eq!(page.total, 10);
        assert!(page.indices.is_empty());
        assert!(!page.has_next);
    }

    #[test]
    fn columnar_path_matches_row_path() {
        // Single int comparison (-> columnar filter) + single-key desc sort
        // (-> columnar sort) must equal the row-engine path exactly.
        let items: Vec<Value> = (0..30).map(item).collect();
        let cols = crate::columnar::Columns::build(&items);
        let filter = FilterInput::Flat(vec![FilterSpec {
            field: "n".into(),
            op: FilterOp::Gte,
            value: Value::Int(10),
            logic: FilterLogic::And,
        }]);
        let sorts = [SortSpec {
            field: "n".into(),
            direction: SortDirection::Desc,
            nulls: NullsPosition::Last,
        }];
        let with_cols = offset_page(&items, Some(&cols), Some(&filter), &sorts, 1, 7).unwrap();
        let row = offset_page(&items, None, Some(&filter), &sorts, 1, 7).unwrap();
        assert_eq!(with_cols, row);
    }

    #[test]
    fn columnar_multi_filter_and_matches_row() {
        // Two flat AND specs, both int-columnar: n >= 10 AND n < 15.
        let items: Vec<Value> = (0..30).map(item).collect();
        let cols = crate::columnar::Columns::build(&items);
        let filter = FilterInput::Flat(vec![
            FilterSpec {
                field: "n".into(),
                op: FilterOp::Gte,
                value: Value::Int(10),
                logic: FilterLogic::And,
            },
            FilterSpec {
                field: "n".into(),
                op: FilterOp::Lt,
                value: Value::Int(15),
                logic: FilterLogic::And,
            },
        ]);
        let with_cols = offset_page(&items, Some(&cols), Some(&filter), &[], 1, 100).unwrap();
        let row = offset_page(&items, None, Some(&filter), &[], 1, 100).unwrap();
        assert_eq!(with_cols, row);
        assert_eq!(with_cols.total, 5); // n in {10, 11, 12, 13, 14}
    }
}
