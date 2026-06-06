//! High-level pagination pipeline: filter → search → sort → offset-paginate in
//! one pass, returning the page's item indices plus offset metadata.
//!
//! This is the "do it all in the core" entry point. A host adapter passes the
//! specs once and gets the page's indices + metadata back in a single call — the
//! orchestration that pypaginate's `engine/pipeline.py` does in Python lives
//! here instead, so the host stays a thin adapter. The optional [`SearchStage`]
//! is a match-filter (explicit `sort_specs` still decide the order), so a search
//! that combines with filters/sorting is one FFI crossing, not three.

use std::cmp::Ordering;

use crate::columnar::Columns;
use crate::error::Result;
use crate::filter::{self, FilterInput, FilterLogic};
use crate::pagination;
use crate::search::{self, FuzzyMode, SearchFieldMode, TrigramIndex};
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

/// The optional search stage of the pipeline: a match-filter applied between
/// filtering and sorting (keep rows where any field matches `query`). It is a
/// *filter*, not a re-rank — explicit `sort_specs` decide the order. Filtering
/// before the sort gives the same page as pypaginate's old `filter → sort →
/// search`, because a match-filter is order-preserving and the sort is stable,
/// so the two orders commute. For the fuzzy/token-sort modes a resident `index`
/// prunes candidates.
pub struct SearchStage<'a> {
    /// Raw query string (normalized internally).
    pub query: &'a str,
    /// Fields to match against (dotted paths).
    pub fields: &'a [String],
    /// Exact/prefix/contains matching mode.
    pub mode: SearchFieldMode,
    /// Fuzzy strategy (Exact disables trigram scoring).
    pub fuzzy: FuzzyMode,
    /// Minimum trigram similarity (0-100) for a fuzzy match.
    pub threshold: i64,
    /// Resident trigram index for fuzzy candidate pruning (optional).
    pub index: Option<&'a TrigramIndex>,
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
    offset_page_searched(items, columns, filter, None, sort_specs, page, limit)
}

/// Like [`offset_page`], plus an optional [`SearchStage`] match-filter applied
/// after filtering and before sorting (so `sort_specs` still decide the order).
/// `filter → search → sort → paginate`, all in one pass returning page indices.
///
/// # Errors
/// Propagates filter/sort/search errors from the underlying engines.
#[allow(clippy::too_many_arguments)]
pub fn offset_page_searched(
    items: &[Value],
    columns: Option<&Columns>,
    filter: Option<&FilterInput>,
    search: Option<&SearchStage>,
    sort_specs: &[SortSpec],
    page: u64,
    limit: u64,
) -> Result<Page> {
    let filtered = filter_stage(items, columns, filter)?;
    let matched = match search {
        Some(s) => search::retain_matching(
            items,
            &filtered,
            s.query,
            s.fields,
            s.mode,
            s.fuzzy,
            s.threshold,
            s.index,
        )?,
        None => filtered,
    };
    let indices = sort_stage(items, columns, matched, sort_specs)?;
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

    fn row(tag: &str, n: i64) -> Value {
        let mut map = BTreeMap::new();
        map.insert("tag".to_owned(), Value::Str(tag.to_owned()));
        map.insert("n".to_owned(), Value::Int(n));
        Value::Map(map)
    }

    fn contains_search<'a>(query: &'a str, fields: &'a [String]) -> super::SearchStage<'a> {
        super::SearchStage {
            query,
            fields,
            mode: SearchFieldMode::Contains,
            fuzzy: FuzzyMode::Exact,
            threshold: 30,
            index: None,
        }
    }

    #[test]
    fn search_filters_then_sort_orders() {
        // Search keeps tags containing "a"; the explicit sort (n desc) decides
        // order -- search is a filter, not a re-rank.
        let items = vec![
            row("apple", 3),
            row("banana", 1),
            row("avocado", 2),
            row("cherry", 4),
        ];
        let fields = ["tag".to_owned()];
        let search = contains_search("a", &fields);
        let sorts = [SortSpec {
            field: "n".into(),
            direction: SortDirection::Desc,
            nulls: NullsPosition::Last,
        }];
        let page = offset_page_searched(&items, None, None, Some(&search), &sorts, 1, 10).unwrap();
        assert_eq!(page.total, 3); // cherry excluded
        assert_eq!(page.indices, vec![0, 2, 1]); // apple(3), avocado(2), banana(1)
    }

    #[test]
    fn search_none_equals_plain_offset_page() {
        let items: Vec<Value> = (0..12).map(item).collect();
        let with = offset_page_searched(&items, None, None, None, &[], 1, 5).unwrap();
        let plain = offset_page(&items, None, None, &[], 1, 5).unwrap();
        assert_eq!(with, plain);
    }

    #[test]
    fn fuzzy_search_uses_index_with_same_result() {
        let items = vec![
            row("alpha one", 1),
            row("bravo two", 2),
            row("alpine three", 3),
        ];
        let fields = ["tag".to_owned()];
        let index = crate::search::TrigramIndex::build(&items);
        let mut search = contains_search("alpha", &fields);
        search.fuzzy = FuzzyMode::Fuzzy;
        let no_index = offset_page_searched(&items, None, None, Some(&search), &[], 1, 10).unwrap();
        search.index = Some(&index);
        let indexed = offset_page_searched(&items, None, None, Some(&search), &[], 1, 10).unwrap();
        assert_eq!(no_index, indexed);
        assert!(!no_index.indices.contains(&1)); // "bravo two" shares no trigrams
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

    #[test]
    fn columnar_bool_filter_matches_row() {
        // A bool field qualifies as a typed column; `active == true` must take
        // the columnar path and equal the row engine exactly.
        let items: Vec<Value> = (0..30)
            .map(|n| {
                let mut map = BTreeMap::new();
                map.insert("n".to_owned(), Value::Int(n));
                map.insert("active".to_owned(), Value::Bool(n % 2 == 0));
                Value::Map(map)
            })
            .collect();
        let cols = crate::columnar::Columns::build(&items);
        let filter = FilterInput::Flat(vec![FilterSpec {
            field: "active".into(),
            op: FilterOp::Eq,
            value: Value::Bool(true),
            logic: FilterLogic::And,
        }]);
        let with_cols = offset_page(&items, Some(&cols), Some(&filter), &[], 1, 100).unwrap();
        let row = offset_page(&items, None, Some(&filter), &[], 1, 100).unwrap();
        assert_eq!(with_cols, row);
        assert_eq!(with_cols.total, 15); // even n in 0..30
    }

    #[test]
    fn columnar_bool_sort_matches_row() {
        // A bool sort key (false < true) must match the row engine.
        let items: Vec<Value> = (0..10)
            .map(|n| {
                let mut map = BTreeMap::new();
                map.insert("n".to_owned(), Value::Int(n));
                map.insert("active".to_owned(), Value::Bool(n % 3 == 0));
                Value::Map(map)
            })
            .collect();
        let cols = crate::columnar::Columns::build(&items);
        let sorts = [SortSpec {
            field: "active".into(),
            direction: SortDirection::Desc,
            nulls: NullsPosition::Last,
        }];
        let with_cols = offset_page(&items, Some(&cols), None, &sorts, 1, 100).unwrap();
        let row = offset_page(&items, None, None, &sorts, 1, 100).unwrap();
        assert_eq!(with_cols, row);
    }
}
