//! napi-rs (Node-API) bindings exposing `paginate-core` to Node/TypeScript.
//!
//! Mirrors the PyO3 adapter's surface. Like the Python layer, the binding's only
//! job is marshalling: convert the host (JS) values to the core's plain
//! [`core::Value`] model, call the pure engine, convert back. Function names
//! follow napi-rs convention — snake_case Rust idents export to JS as camelCase
//! (`normalize_text` → `normalizeText`).
//!
//! Modules mirror the py crate: [`conv`] (marshalling + error mapping),
//! [`engines`] (one-shot filter/sort/search), [`dataset`] (the resident
//! `Dataset`). Cursor, text, and pagination — small-payload scalar bindings —
//! live here.

// `pub` so the `#[napi]`-exported items in these modules are part of the crate's
// public surface (otherwise they read as dead code in the lib-test build).
pub mod conv;
pub mod dataset;
pub mod engines;
pub mod specs;

use napi_derive::napi;
use serde_json::Value as Json;

use crate::conv::{core_err, json_to_value, value_to_json};
use ::paginate_core as core;

/// Maximum page size (DoS mitigation) — the single source of truth, shared with
/// the Python package; the TS `MAX_LIMIT` re-exports this.
#[napi]
pub const MAX_LIMIT: u32 = core::validate::MAX_LIMIT as u32;

/// Maximum search query length, in characters — shared with the Python package.
#[napi]
pub const MAX_QUERY_LEN: u32 = core::validate::MAX_QUERY_LEN as u32;

/// Maximum `FilterGroup` nesting depth — shared with the Python package.
#[napi]
pub const MAX_FILTER_DEPTH: u32 = core::validate::MAX_FILTER_DEPTH as u32;

// -- input validation --------------------------------------------------------

/// Validate offset params (`page >= 1`, `1 <= limit <= MAX_LIMIT`). Throws on
/// failure with a host-facing message; the TS layer rethrows as ValidationError.
#[napi]
pub fn validate_offset(page: i64, limit: i64) -> napi::Result<()> {
    core::validate::validate_offset(page, limit).map_err(|e| core_err(&e))
}

/// Validate cursor params (valid limit; `after`/`before` not both set).
#[napi]
pub fn validate_cursor(limit: i64, has_after: bool, has_before: bool) -> napi::Result<()> {
    core::validate::validate_cursor(limit, has_after, has_before).map_err(|e| core_err(&e))
}

/// Validate a search query length (`<= MAX_QUERY_LEN` characters). Throws on
/// failure; the TS layer rethrows as SearchQueryError.
#[napi]
pub fn validate_search_query(query: String) -> napi::Result<()> {
    core::validate::validate_search_query(&query).map_err(|e| core_err(&e))
}

/// Validate a precomputed filter-nesting depth (`<= MAX_FILTER_DEPTH`). The TS
/// layer measures group depth and rethrows failures as FilterValidationError.
#[napi]
pub fn validate_filter_depth(depth: u32) -> napi::Result<()> {
    core::validate::validate_filter_depth(depth as usize).map_err(|e| core_err(&e))
}

// -- cursor codec ------------------------------------------------------------

/// Encode a list of ordering values into a URL-safe cursor string.
#[napi]
pub fn encode_cursor(values: Json) -> napi::Result<String> {
    let decoded: Vec<core::Value> = match values {
        Json::Array(items) => items.iter().map(json_to_value).collect(),
        // A non-array is treated as a single-element ordering tuple.
        other => vec![json_to_value(&other)],
    };
    core::cursor::encode_cursor(&decoded).map_err(|e| core_err(&e))
}

/// Decode a cursor string back into its array of ordering values.
#[napi]
pub fn decode_cursor(cursor: String) -> napi::Result<Json> {
    let values = core::cursor::decode_cursor(&cursor).map_err(|e| core_err(&e))?;
    Ok(Json::Array(values.iter().map(value_to_json).collect()))
}

// -- text --------------------------------------------------------------------

/// Normalize text for search/filtering (ASCII fast path + NFKD accent strip).
#[napi]
pub fn normalize_text(value: String) -> String {
    core::normalize_text(&value)
}

// -- pagination math ---------------------------------------------------------

/// Page metadata returned by [`offset_meta`]. Fields export as camelCase
/// (`hasNext`, `hasPrevious`) under napi-rs.
#[napi(object)]
pub struct OffsetMeta {
    /// The (possibly clamped) 1-based page number.
    pub page: i64,
    /// Total number of pages.
    pub pages: i64,
    /// Whether a following page exists.
    pub has_next: bool,
    /// Whether a preceding page exists.
    pub has_previous: bool,
}

/// Zero-based row offset for `(page, limit)`.
#[napi]
pub fn offset(page: u32, limit: u32) -> napi::Result<i64> {
    let limit = core::pagination::Limit::new(limit.into()).map_err(|e| core_err(&e))?;
    Ok(core::pagination::offset(page.into(), limit) as i64)
}

/// Total page count for `total` rows at `limit` per page.
#[napi]
pub fn max_pages(total: u32, limit: u32) -> napi::Result<i64> {
    let limit = core::pagination::Limit::new(limit.into()).map_err(|e| core_err(&e))?;
    Ok(core::pagination::max_pages(total.into(), limit) as i64)
}

/// Page metadata as an [`OffsetMeta`] object for `(page, limit, total)`.
#[napi]
pub fn offset_meta(page: u32, limit: u32, total: u32) -> napi::Result<OffsetMeta> {
    let limit = core::pagination::Limit::new(limit.into()).map_err(|e| core_err(&e))?;
    let meta = core::pagination::offset_meta(page.into(), limit, total.into());
    Ok(OffsetMeta {
        page: meta.page as i64,
        pages: meta.pages as i64,
        has_next: meta.has_next,
        has_previous: meta.has_previous,
    })
}

/// Clamp `page` into the valid `[1, max_page]` range.
#[napi]
pub fn clamp_page(page: u32, limit: u32, total: u32) -> napi::Result<i64> {
    let limit = core::pagination::Limit::new(limit.into()).map_err(|e| core_err(&e))?;
    Ok(core::pagination::clamp_page(page.into(), limit, total.into()) as i64)
}

// -- keyset (cursor) predicate ----------------------------------------------

/// Lexicographic keyset predicate as OR-of-AND terms. `ascending[i]` is the
/// effective direction of key `i`; each term is a list of `[key_index, op]`
/// where `op` is `"gt"` / `"lt"` / `"eq"`. The adapter renders `key[i] OP
/// value[i]`, ANDs each term, then ORs the terms. Returned as nested JSON
/// arrays: `[[[0,"gt"]], [[0,"eq"],[1,"lt"]]]`.
#[napi]
pub fn keyset_terms(ascending: Vec<bool>) -> Json {
    let terms = core::keyset::keyset_terms(&ascending)
        .into_iter()
        .map(|term| {
            let pairs = term
                .into_iter()
                .map(|(i, op)| Json::Array(vec![Json::from(i as u64), Json::from(op.as_str())]))
                .collect();
            Json::Array(pairs)
        })
        .collect();
    Json::Array(terms)
}
