//! High-level pagination pipeline: filter → search → sort → offset-paginate in
//! one pass, returning the page's item indices plus offset metadata.
//!
//! This is the "do it all in the core" entry point. A host adapter passes the
//! specs once and gets the page's indices + metadata back in a single call — the
//! orchestration that pypaginate's `engine/pipeline.py` does in Python lives
//! here instead, so the host stays a thin adapter. The optional [`SearchStage`]
//! is a match-filter (explicit `sort_specs` still decide the order), so a search
//! that combines with filters/sorting is one FFI crossing, not three.
//!
//! The per-stage index resolution (the columnar fast paths and row-engine
//! fallbacks) lives in [`stages`]; this module owns the orchestration and the
//! page-slicing math.

mod stages;

use crate::columnar::Columns;
use crate::error::Result;
use crate::filter::FilterInput;
use crate::pagination;
use crate::search::{self, FuzzyMode, SearchFieldMode, TrigramIndex};
use crate::sort::SortSpec;
use crate::value::Value;

use stages::{filter_stage, sort_stage};

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
    let limit = pagination::Limit::new(limit)?;
    let total = matched.len() as u64; // filtered count, before the (top-k) sort
    let meta = pagination::offset_meta(page, limit, total);
    let start = (pagination::offset(page, limit) as usize).min(matched.len());
    let end = start
        .saturating_add(limit.get() as usize)
        .min(matched.len());
    // Sort only enough to fill the page window `[start, end)` — a top-k on the
    // columnar path (the row fallback sorts fully); the slice is identical.
    let indices = sort_stage(items, columns, matched, sort_specs, Some(end))?;
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
mod tests;
