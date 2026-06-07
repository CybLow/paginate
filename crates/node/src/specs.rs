//! JSON → core spec parsing for the napi bindings.
//!
//! The boundary functions in [`crate::engines`] and the resident
//! [`crate::dataset::Dataset`] share these parsers, which translate the typed
//! `#[napi(object)]` inputs and loose JSON objects into the core's filter / sort
//! / search specs. Kept separate so `engines.rs` carries only the napi entry
//! points and this module owns the marshalling shapes (mirrors the PyO3 split).

use std::collections::HashMap;

use napi::bindgen_prelude::{Error, Result, Status};
use napi_derive::napi;
use serde_json::{Map, Value as Json};

use crate::conv::{core_err, json_to_value};
use ::paginate_core as core;

/// A flat filter condition from JS: `{field, operator|op, value?, logic?}`.
/// Typed so the generated `.d.ts` documents the shape (instead of opaque `Json`)
/// and napi-rs validates it; `op` is the legacy alias for `operator`.
#[napi(object)]
pub struct FilterSpecInput {
    /// Dotted field path (e.g. `"user.age"`).
    pub field: String,
    /// Operator name (canonical); see also `op`.
    pub operator: Option<String>,
    /// Legacy alias for `operator`.
    pub op: Option<String>,
    /// Comparison value (meaning depends on the operator).
    pub value: Option<Json>,
    /// `"and"` / `"or"` (default `"and"`).
    pub logic: Option<String>,
}

/// A single sort key from JS: `{field, direction?, nulls?}`.
#[napi(object)]
pub struct SortSpecInput {
    /// Dotted field path to sort by.
    pub field: String,
    /// `"asc"` (default) / `"desc"`.
    pub direction: Option<String>,
    /// `"first"` / `"last"` (default `"last"`).
    pub nulls: Option<String>,
}

/// Map a typed [`FilterSpecInput`] onto a core filter spec.
fn to_core_filter(spec: FilterSpecInput) -> Result<core::filter::FilterSpec> {
    let op_name = spec
        .operator
        .or(spec.op)
        .ok_or_else(|| Error::new(Status::InvalidArg, "spec.operator must be a string"))?;
    let op = core::filter::FilterOp::from_name(&op_name)
        .ok_or_else(|| Error::new(Status::InvalidArg, format!("unknown operator: {op_name}")))?;
    let logic = match spec.logic.as_deref() {
        Some(token) => core::filter::FilterLogic::from_token(token).map_err(|e| core_err(&e))?,
        None => core::filter::FilterLogic::And,
    };
    Ok(core::filter::FilterSpec {
        field: spec.field,
        op,
        value: spec.value.as_ref().map_or(core::Value::Null, json_to_value),
        logic,
    })
}

/// Map a typed [`SortSpecInput`] onto a core sort spec.
fn to_core_sort(spec: SortSpecInput) -> Result<core::sort::SortSpec> {
    let direction = match spec.direction.as_deref() {
        Some(token) => core::sort::SortDirection::from_token(token).map_err(|e| core_err(&e))?,
        None => core::sort::SortDirection::Asc,
    };
    let nulls = match spec.nulls.as_deref() {
        Some(token) => core::sort::NullsPosition::from_token(token).map_err(|e| core_err(&e))?,
        None => core::sort::NullsPosition::Last,
    };
    Ok(core::sort::SortSpec {
        field: spec.field,
        direction,
        nulls,
    })
}

/// Convert typed filter inputs into core flat filter specs.
pub(crate) fn to_filter_specs(
    specs: Vec<FilterSpecInput>,
) -> Result<Vec<core::filter::FilterSpec>> {
    specs.into_iter().map(to_core_filter).collect()
}

/// Convert typed filter inputs into a core flat `FilterInput`.
pub(crate) fn to_filter_input(specs: Vec<FilterSpecInput>) -> Result<core::filter::FilterInput> {
    Ok(core::filter::FilterInput::Flat(to_filter_specs(specs)?))
}

/// Convert typed sort inputs into core sort specs.
pub(crate) fn to_sort_specs(specs: Vec<SortSpecInput>) -> Result<Vec<core::sort::SortSpec>> {
    specs.into_iter().map(to_core_sort).collect()
}

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

/// Parse a nested filter node: a leaf `{field, op, value, logic?}` or a group
/// `{logic, conditions: [node, ...]}` (an object with a `conditions` array).
pub(crate) fn parse_filter_node(node: &Json) -> Result<core::filter::FilterNode> {
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

/// Map an optional mode token to the core enum (default `Contains`) via the
/// core's parser — shared with the PyO3 binding so the two cannot drift.
pub(crate) fn search_mode(mode: Option<&str>) -> Result<core::search::SearchFieldMode> {
    match mode {
        Some(token) => core::search::SearchFieldMode::from_token(token).map_err(|e| core_err(&e)),
        None => Ok(core::search::SearchFieldMode::Contains),
    }
}

/// Map an optional fuzzy token to the core enum (default `Exact`) via the core's
/// parser.
pub(crate) fn search_fuzzy(fuzzy: Option<&str>) -> Result<core::search::FuzzyMode> {
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
