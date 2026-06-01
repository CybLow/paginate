//! napi-rs (Node-API) bindings exposing `paginate-core` to Node/TypeScript.
//!
//! Mirrors the PyO3 adapter's surface (cursor encode/decode, `normalize_text`,
//! offset/`max_pages`/`offset_meta`/`clamp_page`). Like the Python layer, the
//! binding's only job is marshalling: convert the host (JS) values to the
//! core's plain [`core::Value`] model, call the pure engine, convert back.
//!
//! Function names follow napi-rs convention — snake_case Rust idents are
//! exported to JS as camelCase (`normalize_text` -> `normalizeText`).
//!
//! ## Cursor values
//!
//! JS has no native datetime/Decimal/UUID, so cursor values cross as a plain
//! `serde_json::Value`. The mapping is the JSON subset of [`core::Value`]:
//! `null`/`bool`/`number`(Int if integral, else Float)/`string`/`array`/
//! `object`. The typed scalars the Python codec round-trips (datetime, date,
//! Decimal, UUID) are not produced here — callers pass their ISO strings.

use std::collections::BTreeMap;

use napi::bindgen_prelude::{Error, Result, Status};
use napi_derive::napi;
use serde_json::{Map, Number, Value as Json};

use ::paginate_core as core;

// -- cursor conv (serde_json::Value <-> core::Value) -------------------------

/// Convert a JSON value into the core [`core::Value`] model.
fn json_to_value(json: &Json) -> core::Value {
    match json {
        Json::Null => core::Value::Null,
        Json::Bool(b) => core::Value::Bool(*b),
        Json::Number(n) => number_to_value(n),
        Json::String(s) => core::Value::Str(s.clone()),
        Json::Array(items) => core::Value::List(items.iter().map(json_to_value).collect()),
        Json::Object(map) => core::Value::Map(object_to_map(map)),
    }
}

/// Number to `Int` when it fits an i64, else `Float` (matches the core codec).
fn number_to_value(n: &Number) -> core::Value {
    if let Some(i) = n.as_i64() {
        return core::Value::Int(i);
    }
    n.as_f64().map_or(core::Value::Null, core::Value::Float)
}

fn object_to_map(map: &Map<String, Json>) -> BTreeMap<String, core::Value> {
    map.iter()
        .map(|(key, value)| (key.clone(), json_to_value(value)))
        .collect()
}

/// Convert a core [`core::Value`] back into a JSON value. Typed scalars carry a
/// string payload, so they map back to `string` for JS consumers.
fn value_to_json(value: &core::Value) -> Json {
    match value {
        core::Value::Null => Json::Null,
        core::Value::Bool(b) => Json::Bool(*b),
        core::Value::Int(i) => Json::Number((*i).into()),
        core::Value::Float(f) => float_to_json(*f),
        core::Value::Str(s)
        | core::Value::DateTime(s)
        | core::Value::Date(s)
        | core::Value::Decimal(s)
        | core::Value::Uuid(s) => Json::String(s.clone()),
        core::Value::Bytes(b) => Json::String(String::from_utf8_lossy(b).into_owned()),
        core::Value::List(items) => Json::Array(items.iter().map(value_to_json).collect()),
        core::Value::Map(map) => Json::Object(map_to_object(map)),
    }
}

/// Non-finite floats are not valid JSON numbers; emit `null` defensively.
fn float_to_json(f: f64) -> Json {
    Number::from_f64(f).map_or(Json::Null, Json::Number)
}

fn map_to_object(map: &BTreeMap<String, core::Value>) -> Map<String, Json> {
    map.iter()
        .map(|(key, value)| (key.clone(), value_to_json(value)))
        .collect()
}

/// Map a core error onto a napi error thrown to JS.
fn core_err(err: &core::CoreError) -> Error {
    Error::new(Status::InvalidArg, err.to_string())
}

// -- cursor codec ------------------------------------------------------------

/// Encode a list of ordering values into a URL-safe cursor string.
#[napi]
pub fn encode_cursor(values: Json) -> Result<String> {
    let decoded: Vec<core::Value> = match values {
        Json::Array(items) => items.iter().map(json_to_value).collect(),
        // A non-array is treated as a single-element ordering tuple.
        other => vec![json_to_value(&other)],
    };
    Ok(core::cursor::encode_cursor(&decoded))
}

/// Decode a cursor string back into its array of ordering values.
#[napi]
pub fn decode_cursor(cursor: String) -> Result<Json> {
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
pub fn offset(page: u32, limit: u32) -> i64 {
    core::pagination::offset(page.into(), limit.into()) as i64
}

/// Total page count for `total` rows at `limit` per page.
#[napi]
pub fn max_pages(total: u32, limit: u32) -> i64 {
    core::pagination::max_pages(total.into(), limit.into()) as i64
}

/// Page metadata as an [`OffsetMeta`] object for `(page, limit, total)`.
#[napi]
pub fn offset_meta(page: u32, limit: u32, total: u32) -> OffsetMeta {
    let meta = core::pagination::offset_meta(page.into(), limit.into(), total.into());
    OffsetMeta {
        page: meta.page as i64,
        pages: meta.pages as i64,
        has_next: meta.has_next,
        has_previous: meta.has_previous,
    }
}

/// Clamp `page` into the valid `[1, max_page]` range.
#[napi]
pub fn clamp_page(page: u32, limit: u32, total: u32) -> i64 {
    core::pagination::clamp_page(page.into(), limit.into(), total.into()) as i64
}

// -- in-memory engines (filter / sort / search) ------------------------------
//
// Items arrive as a JS array of objects; napi marshals them to serde_json and
// we map to core Values. The engines return indices; the JS caller selects from
// its original array. Unlike pypaginate's 7-round-optimized pure-Python engines
// (where FFI marshalling can dominate), a naive JS engine has nothing to beat —
// so native wins here across the board.

fn json_array_to_values(items: &Json) -> Result<Vec<core::Value>> {
    match items {
        Json::Array(array) => Ok(array.iter().map(json_to_value).collect()),
        _ => Err(Error::new(Status::InvalidArg, "items must be an array")),
    }
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

fn parse_filter_specs(specs: &Json) -> Result<Vec<core::filter::FilterSpec>> {
    let array = specs
        .as_array()
        .ok_or_else(|| Error::new(Status::InvalidArg, "specs must be an array"))?;
    let mut out = Vec::with_capacity(array.len());
    for spec in array {
        let obj = spec_object(spec)?;
        let op_name = required_str(obj, "op")?;
        let op = core::filter::FilterOp::from_name(&op_name).ok_or_else(|| {
            Error::new(Status::InvalidArg, format!("unknown operator: {op_name}"))
        })?;
        let logic = match obj.get("logic").and_then(Json::as_str) {
            Some("or") => core::filter::FilterLogic::Or,
            _ => core::filter::FilterLogic::And,
        };
        out.push(core::filter::FilterSpec {
            field: required_str(obj, "field")?,
            op,
            value: obj.get("value").map_or(core::Value::Null, json_to_value),
            logic,
        });
    }
    Ok(out)
}

/// Indices of items matching flat filter specs `[{field, op, value, logic?}]`.
#[napi]
pub fn filter_indices(items: Json, specs: Json) -> Result<Vec<u32>> {
    let values = json_array_to_values(&items)?;
    let core_specs = parse_filter_specs(&specs)?;
    let indices =
        core::filter::filter_indices(&values, &core::filter::FilterInput::Flat(core_specs))
            .map_err(|e| core_err(&e))?;
    Ok(indices.into_iter().map(|i| i as u32).collect())
}

fn parse_sort_specs(specs: &Json) -> Result<Vec<core::sort::SortSpec>> {
    let array = specs
        .as_array()
        .ok_or_else(|| Error::new(Status::InvalidArg, "specs must be an array"))?;
    let mut out = Vec::with_capacity(array.len());
    for spec in array {
        let obj = spec_object(spec)?;
        let direction = match obj.get("direction").and_then(Json::as_str) {
            Some("desc") => core::sort::SortDirection::Desc,
            _ => core::sort::SortDirection::Asc,
        };
        let nulls = match obj.get("nulls").and_then(Json::as_str) {
            Some("first") => core::sort::NullsPosition::First,
            _ => core::sort::NullsPosition::Last,
        };
        out.push(core::sort::SortSpec {
            field: required_str(obj, "field")?,
            direction,
            nulls,
        });
    }
    Ok(out)
}

/// A permutation of item indices for sort specs `[{field, direction?, nulls?}]`.
#[napi]
pub fn sort_indices(items: Json, specs: Json) -> Result<Vec<u32>> {
    let values = json_array_to_values(&items)?;
    let core_specs = parse_sort_specs(&specs)?;
    let indices = core::sort::sort_indices(&values, &core_specs).map_err(|e| core_err(&e))?;
    Ok(indices.into_iter().map(|i| i as u32).collect())
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
) -> Result<Vec<u32>> {
    let values = json_array_to_values(&items)?;
    let spec = core::search::SearchSpec {
        query,
        fields,
        weights: None,
        mode: match mode.as_deref() {
            Some("prefix") => core::search::SearchFieldMode::Prefix,
            Some("exact") => core::search::SearchFieldMode::Exact,
            _ => core::search::SearchFieldMode::Contains,
        },
        fuzzy: match fuzzy.as_deref() {
            Some("fuzzy") => core::search::FuzzyMode::Fuzzy,
            Some("token_sort") => core::search::FuzzyMode::TokenSort,
            _ => core::search::FuzzyMode::Exact,
        },
        threshold: threshold.unwrap_or(75),
        min_length: min_length.unwrap_or(1) as usize,
        max_results: max_results.map(|m| m as usize),
    };
    let indices = core::search::search_indices(&values, &spec).map_err(|e| core_err(&e))?;
    Ok(indices.into_iter().map(|i| i as u32).collect())
}
