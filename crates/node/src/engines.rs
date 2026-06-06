//! One-shot in-memory engine bindings (filter / sort / search) and the JSON
//! spec parsers they share with [`crate::dataset::Dataset`].
//!
//! Items arrive as a JS array of objects; we map them to core `Value`s and the
//! engines return **indices** the JS caller selects from its original array.
//! PERF: for raw in-memory speed a JS caller should use native `Array` methods
//! — benchmarks show V8 beats this by 40–230× because marshalling 10K objects
//! across napi dwarfs the tiny per-item work. These exist for *behaviour parity*
//! with pypaginate's exact semantics; for speed use the resident `Dataset`.

use std::collections::HashMap;

use napi::bindgen_prelude::{Error, Result, Status};
use napi_derive::napi;
use serde_json::{Map, Value as Json};

use crate::conv::{core_err, json_array_to_values, json_to_value, to_u32};
use ::paginate_core as core;

fn spec_object(spec: &Json) -> Result<&Map<String, Json>> {
    spec.as_object()
        .ok_or_else(|| Error::new(Status::InvalidArg, "each spec must be an object"))
}

fn required_str(obj: &Map<String, Json>, key: &str) -> Result<String> {
    obj.get(key)
        .and_then(Json::as_str)
        .map(str::to_owned)
        .ok_or_else(|| Error::new(Status::InvalidArg, format!("spec.{key} must be a string")))
}

/// The operator name, accepting `operator` (canonical, matches the Python and
/// Rust APIs) or the legacy `op` alias.
fn operator_name(obj: &Map<String, Json>) -> Result<String> {
    obj.get("operator")
        .or_else(|| obj.get("op"))
        .and_then(Json::as_str)
        .map(str::to_owned)
        .ok_or_else(|| Error::new(Status::InvalidArg, "spec.operator must be a string"))
}

/// Parse the optional `logic` token (default AND) via the core's parser, so the
/// flat-spec and nested-group paths share one source with the PyO3 binding.
fn parse_logic(obj: &Map<String, Json>) -> Result<core::filter::FilterLogic> {
    match obj.get("logic").and_then(Json::as_str) {
        Some(token) => core::filter::FilterLogic::from_token(token).map_err(|e| core_err(&e)),
        None => Ok(core::filter::FilterLogic::And),
    }
}

/// Parse one `{field, operator, value, logic?}` object into a core filter spec.
fn parse_one_spec(obj: &Map<String, Json>) -> Result<core::filter::FilterSpec> {
    let op_name = operator_name(obj)?;
    let op = core::filter::FilterOp::from_name(&op_name)
        .ok_or_else(|| Error::new(Status::InvalidArg, format!("unknown operator: {op_name}")))?;
    let logic = parse_logic(obj)?;
    Ok(core::filter::FilterSpec {
        field: required_str(obj, "field")?,
        op,
        value: obj.get("value").map_or(core::Value::Null, json_to_value),
        logic,
    })
}

/// Parse `[{field, op, value, logic?}]` into core filter specs.
pub(crate) fn parse_filter_specs(specs: &Json) -> Result<Vec<core::filter::FilterSpec>> {
    let array = specs
        .as_array()
        .ok_or_else(|| Error::new(Status::InvalidArg, "specs must be an array"))?;
    array
        .iter()
        .map(|spec| parse_one_spec(spec_object(spec)?))
        .collect()
}

/// Parse a nested filter node: a leaf `{field, op, value, logic?}` or a group
/// `{logic, conditions: [node, ...]}` (an object with a `conditions` array).
fn parse_filter_node(node: &Json) -> Result<core::filter::FilterNode> {
    let obj = spec_object(node)?;
    let Some(conditions) = obj.get("conditions") else {
        return Ok(core::filter::FilterNode::Spec(parse_one_spec(obj)?));
    };
    let array = conditions
        .as_array()
        .ok_or_else(|| Error::new(Status::InvalidArg, "group.conditions must be an array"))?;
    let logic = parse_logic(obj)?;
    let conditions = array
        .iter()
        .map(parse_filter_node)
        .collect::<Result<Vec<_>>>()?;
    Ok(core::filter::FilterNode::Group(core::filter::FilterGroup {
        logic,
        conditions,
    }))
}

/// Parse `[{field, direction?, nulls?}]` into core sort specs.
pub(crate) fn parse_sort_specs(specs: &Json) -> Result<Vec<core::sort::SortSpec>> {
    let array = specs
        .as_array()
        .ok_or_else(|| Error::new(Status::InvalidArg, "specs must be an array"))?;
    let mut out = Vec::with_capacity(array.len());
    for spec in array {
        let obj = spec_object(spec)?;
        let direction = match obj.get("direction").and_then(Json::as_str) {
            Some(token) => {
                core::sort::SortDirection::from_token(token).map_err(|e| core_err(&e))?
            }
            None => core::sort::SortDirection::Asc,
        };
        let nulls = match obj.get("nulls").and_then(Json::as_str) {
            Some(token) => {
                core::sort::NullsPosition::from_token(token).map_err(|e| core_err(&e))?
            }
            None => core::sort::NullsPosition::Last,
        };
        out.push(core::sort::SortSpec {
            field: required_str(obj, "field")?,
            direction,
            nulls,
        });
    }
    Ok(out)
}

/// Map an optional mode token to the core enum (default `Contains`) via the
/// core's parser — shared with the PyO3 binding so the two cannot drift.
fn search_mode(mode: Option<&str>) -> Result<core::search::SearchFieldMode> {
    match mode {
        Some(token) => core::search::SearchFieldMode::from_token(token).map_err(|e| core_err(&e)),
        None => Ok(core::search::SearchFieldMode::Contains),
    }
}

/// Map an optional fuzzy token to the core enum (default `Exact`) via the core's
/// parser.
fn search_fuzzy(fuzzy: Option<&str>) -> Result<core::search::FuzzyMode> {
    match fuzzy {
        Some(token) => core::search::FuzzyMode::from_token(token).map_err(|e| core_err(&e)),
        None => Ok(core::search::FuzzyMode::Exact),
    }
}

/// Build a [`core::search::SearchSpec`] from the optional JS arguments (shared
/// by `search_indices` and `Dataset::search`).
#[allow(clippy::too_many_arguments)]
pub(crate) fn build_search_spec(
    query: String,
    fields: Vec<String>,
    mode: Option<String>,
    fuzzy: Option<String>,
    threshold: Option<i64>,
    min_length: Option<u32>,
    max_results: Option<u32>,
    weights: Option<HashMap<String, f64>>,
) -> Result<core::search::SearchSpec> {
    core::validate::validate_search_query(&query).map_err(|e| core_err(&e))?;
    Ok(core::search::SearchSpec {
        query,
        fields,
        // Field names pass through directly (no synthetic re-keying), so weights
        // key by the same names the caller supplied.
        weights: weights.map(|w| w.into_iter().collect()),
        mode: search_mode(mode.as_deref())?,
        fuzzy: search_fuzzy(fuzzy.as_deref())?,
        threshold: threshold.unwrap_or(30),
        min_length: min_length.unwrap_or(1) as usize,
        max_results: max_results.map(|m| m as usize),
    })
}

/// Owned parts of a search stage, parsed from a `{query, fields, mode?, fuzzy?,
/// threshold?}` object (the resident `Dataset::page` search arg).
pub(crate) type SearchStageParts = (
    String,
    Vec<String>,
    core::search::SearchFieldMode,
    core::search::FuzzyMode,
    i64,
);

/// Parse a search-stage object into its owned parts.
pub(crate) fn parse_search_stage(spec: &Json) -> Result<SearchStageParts> {
    let obj = spec_object(spec)?;
    let fields = obj
        .get("fields")
        .and_then(Json::as_array)
        .map(|a| {
            a.iter()
                .filter_map(|v| v.as_str().map(str::to_owned))
                .collect()
        })
        .unwrap_or_default();
    let query = required_str(obj, "query")?;
    core::validate::validate_search_query(&query).map_err(|e| core_err(&e))?;
    Ok((
        query,
        fields,
        search_mode(obj.get("mode").and_then(Json::as_str))?,
        search_fuzzy(obj.get("fuzzy").and_then(Json::as_str))?,
        obj.get("threshold").and_then(Json::as_i64).unwrap_or(30),
    ))
}

/// Indices of items matching flat filter specs `[{field, op, value, logic?}]`.
#[napi]
pub fn filter_indices(items: Json, specs: Json) -> Result<Vec<u32>> {
    let values = json_array_to_values(&items)?;
    let core_specs = parse_filter_specs(&specs)?;
    core::filter::filter_indices(&values, &core::filter::FilterInput::Flat(core_specs))
        .map(to_u32)
        .map_err(|e| core_err(&e))
}

/// Indices of items matching a nested filter `group`. A leaf is
/// `{field, op, value, logic?}`; a group is `{logic, conditions: [node, ...]}`.
/// Mirrors the PyO3 `filter_group_indices` so JS/TS gets nested And/Or filters.
#[napi]
pub fn filter_group_indices(items: Json, group: Json) -> Result<Vec<u32>> {
    let values = json_array_to_values(&items)?;
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
pub fn sort_indices(items: Json, specs: Json) -> Result<Vec<u32>> {
    let values = json_array_to_values(&items)?;
    let core_specs = parse_sort_specs(&specs)?;
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
    let values = json_array_to_values(&items)?;
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
