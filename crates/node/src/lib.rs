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
