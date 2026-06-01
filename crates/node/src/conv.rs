//! Marshalling between `serde_json::Value` (the JS boundary type) and the core
//! [`core::Value`] model, plus the core-error → napi-error mapping.
//!
//! JS has no native datetime/Decimal/UUID, so cursor values cross as a plain
//! `serde_json::Value`: the JSON subset of [`core::Value`]
//! (`null`/`bool`/`number`/`string`/`array`/`object`). Typed scalars the Python
//! codec round-trips are not produced here — callers pass their ISO strings.

use std::collections::BTreeMap;

use napi::bindgen_prelude::{Error, Result, Status};
use serde_json::{Map, Number, Value as Json};

use ::paginate_core as core;

/// Convert a JSON value into the core [`core::Value`] model.
pub(crate) fn json_to_value(json: &Json) -> core::Value {
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
pub(crate) fn value_to_json(value: &core::Value) -> Json {
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

/// Marshal a JS array of values into core [`core::Value`]s (errors if not an array).
pub(crate) fn json_array_to_values(items: &Json) -> Result<Vec<core::Value>> {
    match items {
        Json::Array(array) => Ok(array.iter().map(json_to_value).collect()),
        _ => Err(Error::new(Status::InvalidArg, "items must be an array")),
    }
}

/// Convert core `usize` indices to the `u32` array napi returns to JS.
pub(crate) fn to_u32(indices: Vec<usize>) -> Vec<u32> {
    indices.into_iter().map(|i| i as u32).collect()
}

/// Map a core error onto a napi error thrown to JS. (`From<CoreError>` is not
/// possible — both types are foreign to this crate — so a helper is the idiom.)
pub(crate) fn core_err(err: &core::CoreError) -> Error {
    Error::new(Status::InvalidArg, err.to_string())
}
