//! High-level pagination pipeline: filter → sort → offset-paginate in one pass,
//! returning the page's item indices plus offset metadata.
//!
//! This is the "do it all in the core" entry point. A host adapter passes the
//! specs once and gets the page's indices + metadata back in a single call — the
//! orchestration that pypaginate's `engine/pipeline.py` does in Python lives
//! here instead, so the host stays a thin adapter. (Search is applied by the
//! caller for now; a search stage can join this pass later.)

use crate::error::Result;
use crate::filter::{self, FilterInput};
use crate::pagination;
use crate::sort::{self, SortSpec};
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
/// `filter` is skipped when `None`; `sort_specs` is skipped when empty. Mirrors
/// pypaginate's `filter → sort → paginate` ordering.
///
/// # Errors
/// Propagates filter/sort errors from the underlying engines.
pub fn offset_page(
    items: &[Value],
    filter: Option<&FilterInput>,
    sort_specs: &[SortSpec],
    page: u64,
    limit: u64,
) -> Result<Page> {
    let mut indices = match filter {
        Some(input) => filter::filter_indices(items, input)?,
        None => (0..items.len()).collect(),
    };
    if !sort_specs.is_empty() {
        indices = sort::sort_indices_of(items, indices, sort_specs)?;
    }
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
        let page = offset_page(&items, Some(&filter), &sorts, 1, 5).unwrap();
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
        let page = offset_page(&items, None, &[], 99, 5).unwrap();
        assert_eq!(page.total, 10);
        assert!(page.indices.is_empty());
        assert!(!page.has_next);
    }
}
