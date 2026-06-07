//! One-shot in-memory engine bindings (filter / sort / search).
//!
//! Items arrive as a JS array of objects; we map them to core `Value`s and the
//! engines return **indices** the JS caller selects from its original array.
//! PERF: for raw in-memory speed a JS caller should use native `Array` methods
//! — benchmarks show V8 beats this by 40–230× because marshalling 10K objects
//! across napi dwarfs the tiny per-item work. These exist for *behaviour parity*
//! with pypaginate's exact semantics; for speed use the resident `Dataset`.
//!
//! The JSON → core spec parsing these share with [`crate::dataset::Dataset`]
//! lives in [`crate::specs`].

use std::collections::HashMap;

use napi::bindgen_prelude::Result;
use napi_derive::napi;
use serde_json::Value as Json;

use crate::conv::{core_err, json_array_to_values, to_u32};
use crate::specs::{
    build_search_spec, parse_filter_node, search_fuzzy, search_mode, to_filter_input,
    to_sort_specs, FilterSpecInput, SortSpecInput,
};
use ::paginate_core as core;

/// Indices of items matching flat filter specs `[{field, operator, value?, logic?}]`.
#[napi]
pub fn filter_indices(items: Json, specs: Vec<FilterSpecInput>) -> Result<Vec<u32>> {
    let values = json_array_to_values(items)?;
    let input = to_filter_input(specs)?;
    core::filter::filter_indices(&values, &input)
        .map(to_u32)
        .map_err(|e| core_err(&e))
}

/// Indices of items matching a nested filter `group`. A leaf is
/// `{field, op, value, logic?}`; a group is `{logic, conditions: [node, ...]}`.
/// Mirrors the PyO3 `filter_group_indices` so JS/TS gets nested And/Or filters.
#[napi]
pub fn filter_group_indices(items: Json, group: Json) -> Result<Vec<u32>> {
    let values = json_array_to_values(items)?;
    let input = match parse_filter_node(&group)? {
        core::filter::FilterNode::Group(group) => core::filter::FilterInput::Group(group),
        core::filter::FilterNode::Spec(spec) => core::filter::FilterInput::Flat(vec![spec]),
    };
    core::validate::validate_filter_input(&input).map_err(|e| core_err(&e))?;
    core::filter::filter_indices(&values, &input)
        .map(to_u32)
        .map_err(|e| core_err(&e))
}

/// A permutation of item indices for sort specs `[{field, direction?, nulls?}]`.
#[napi]
pub fn sort_indices(items: Json, specs: Vec<SortSpecInput>) -> Result<Vec<u32>> {
    let values = json_array_to_values(items)?;
    let core_specs = to_sort_specs(specs)?;
    core::sort::sort_indices(&values, &core_specs)
        .map(to_u32)
        .map_err(|e| core_err(&e))
}

/// Ranked search: indices of items by relevance of `query` over `fields`.
#[napi]
#[allow(clippy::too_many_arguments)]
pub fn search_indices(
    items: Json,
    query: String,
    fields: Vec<String>,
    mode: Option<String>,
    fuzzy: Option<String>,
    threshold: Option<i64>,
    min_length: Option<u32>,
    max_results: Option<u32>,
    weights: Option<HashMap<String, f64>>,
) -> Result<Vec<u32>> {
    let values = json_array_to_values(items)?;
    let spec = build_search_spec(
        query,
        fields,
        mode,
        fuzzy,
        threshold,
        min_length,
        max_results,
        weights,
    )?;
    core::search::search_indices(&values, &spec)
        .map(to_u32)
        .map_err(|e| core_err(&e))
}

/// Indices of items where any field matches the whole query — by `mode`
/// (contains/prefix/exact) when `fuzzy="exact"`, else by trigram score. Original
/// order, unranked. Mirrors the PyO3 `match_indices` so JS/TS has the same
/// engine surface (closing a parity gap where Node lacked it).
#[napi]
pub fn match_indices(
    items: Json,
    query: String,
    fields: Vec<String>,
    mode: Option<String>,
    fuzzy: Option<String>,
    threshold: Option<i64>,
) -> Result<Vec<u32>> {
    let values = json_array_to_values(items)?;
    core::search::match_indices(
        &values,
        &query,
        &fields,
        search_mode(mode.as_deref())?,
        search_fuzzy(fuzzy.as_deref())?,
        threshold.unwrap_or(30),
    )
    .map(to_u32)
    .map_err(|e| core_err(&e))
}
