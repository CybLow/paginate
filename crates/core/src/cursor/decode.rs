//! Deserialisation half of the cursor codec: re-pad and base64-decode the
//! payload, then rebuild the typed [`Value`]s from the JSON (recognising the
//! `{"__type__": "...", "v": "..."}` tags the encoder emits).

use std::collections::BTreeMap;

use base64::Engine as _;

use crate::error::Result;
use crate::value::Value;

use super::{invalid, URL_SAFE, URL_SAFE_NO_PAD};

pub(super) fn decode_base64(cursor: &str) -> Result<Vec<u8>> {
    // Re-pad to a multiple of 4 (mirrors the Python codec) so a strict decoder
    // accepts the stripped form; fall back to the lenient no-pad decoder.
    let pad = (4 - cursor.len() % 4) % 4;
    if pad == 0 {
        return URL_SAFE_NO_PAD
            .decode(cursor.as_bytes())
            .or_else(|_| URL_SAFE.decode(cursor.as_bytes()))
            .map_err(|_| invalid("base64"));
    }
    let mut padded = String::with_capacity(cursor.len() + pad);
    padded.push_str(cursor);
    padded.extend(std::iter::repeat('=').take(pad));
    URL_SAFE
        .decode(padded.as_bytes())
        .map_err(|_| invalid("base64"))
}

pub(super) fn json_to_value(v: &serde_json::Value) -> Result<Value> {
    match v {
        serde_json::Value::Null => Ok(Value::Null),
        serde_json::Value::Bool(b) => Ok(Value::Bool(*b)),
        serde_json::Value::Number(n) => number_to_value(n),
        serde_json::Value::String(s) => Ok(Value::Str(s.clone())),
        serde_json::Value::Array(a) => a
            .iter()
            .map(json_to_value)
            .collect::<Result<Vec<_>>>()
            .map(Value::List),
        serde_json::Value::Object(map) => object_to_value(map),
    }
}

fn number_to_value(n: &serde_json::Number) -> Result<Value> {
    if let Some(i) = n.as_i64() {
        Ok(Value::Int(i))
    } else if let Some(f) = n.as_f64() {
        Ok(Value::Float(f))
    } else {
        Err(invalid("number"))
    }
}

fn object_to_value(map: &serde_json::Map<String, serde_json::Value>) -> Result<Value> {
    let Some(serde_json::Value::String(tag)) = map.get("__type__") else {
        // A plain object (no recognised tag) round-trips as a Map.
        let mut out = BTreeMap::new();
        for (k, v) in map {
            out.insert(k.clone(), json_to_value(v)?);
        }
        return Ok(Value::Map(out));
    };
    let raw = match map.get("v") {
        Some(serde_json::Value::String(s)) => s.clone(),
        Some(other) => other.to_string(),
        None => String::new(),
    };
    match tag.as_str() {
        "datetime" => Ok(Value::DateTime(raw)),
        "date" => Ok(Value::Date(raw)),
        "decimal" => Ok(Value::Decimal(raw)),
        "uuid" => Ok(Value::Uuid(raw)),
        other => Err(invalid(&format!("unknown type tag: {other}"))),
    }
}
