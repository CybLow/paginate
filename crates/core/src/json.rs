//! Lossy bridge between `serde_json::Value` and the core [`Value`] model.
//!
//! For bindings whose host boundary is JSON (the Node/napi binding), and for any
//! `serde`-shaped consumer. Unlike the cursor codec's tagged wire form, the
//! typed scalars collapse to plain strings here — JSON has no
//! datetime/Decimal/UUID — so this is a faithful *data* mapping for general
//! marshalling, not a round-tripping codec (use [`crate::cursor`] for that).

use std::collections::BTreeMap;

use serde_json::{Map, Number, Value as Json};

use crate::value::Value;

/// Convert a `serde_json::Value` into the core [`Value`] model.
#[must_use]
pub fn from_json(json: &Json) -> Value {
    match json {
        Json::Null => Value::Null,
        Json::Bool(b) => Value::Bool(*b),
        Json::Number(n) => number_to_value(n),
        Json::String(s) => Value::Str(s.clone()),
        Json::Array(items) => Value::List(items.iter().map(from_json).collect()),
        Json::Object(map) => Value::Map(object_to_map(map)),
    }
}

/// Convert an owned `serde_json::Value` into [`Value`], **moving** strings and
/// map keys instead of cloning them. Use when the caller owns the JSON (e.g. the
/// napi binding receives it by value) — it skips the per-string allocation that
/// the borrowing [`from_json`] must pay.
#[must_use]
pub fn from_json_owned(json: Json) -> Value {
    match json {
        Json::Null => Value::Null,
        Json::Bool(b) => Value::Bool(b),
        Json::Number(n) => number_to_value(&n),
        Json::String(s) => Value::Str(s),
        Json::Array(items) => Value::List(items.into_iter().map(from_json_owned).collect()),
        Json::Object(map) => Value::Map(
            map.into_iter()
                .map(|(k, v)| (k, from_json_owned(v)))
                .collect(),
        ),
    }
}

/// A JSON number as `Int` when it fits an `i64`, else `Float` (general
/// marshalling is lossy by design; the cursor codec rejects out-of-range ints).
fn number_to_value(n: &Number) -> Value {
    if let Some(i) = n.as_i64() {
        return Value::Int(i);
    }
    n.as_f64().map_or(Value::Null, Value::Float)
}

fn object_to_map(map: &Map<String, Json>) -> BTreeMap<String, Value> {
    map.iter()
        .map(|(key, value)| (key.clone(), from_json(value)))
        .collect()
}

/// Convert a core [`Value`] into a `serde_json::Value`. The typed scalars carry
/// a canonical string, so they map to a JSON `string`; `Bytes` is rendered
/// lossily (UTF-8 with replacement) as JSON has no byte type.
#[must_use]
pub fn to_json(value: &Value) -> Json {
    match value {
        Value::Null => Json::Null,
        Value::Bool(b) => Json::Bool(*b),
        Value::Int(i) => Json::Number((*i).into()),
        Value::Float(f) => float_to_json(*f),
        Value::Str(s)
        | Value::DateTime(s)
        | Value::Date(s)
        | Value::Decimal(s)
        | Value::Uuid(s) => Json::String(s.clone()),
        Value::Bytes(b) => Json::String(String::from_utf8_lossy(b).into_owned()),
        Value::List(items) => Json::Array(items.iter().map(to_json).collect()),
        Value::Map(map) => Json::Object(map_to_object(map)),
    }
}

/// Non-finite floats are not valid JSON numbers; emit `null` defensively.
fn float_to_json(f: f64) -> Json {
    Number::from_f64(f).map_or(Json::Null, Json::Number)
}

fn map_to_object(map: &BTreeMap<String, Value>) -> Map<String, Json> {
    map.iter()
        .map(|(key, value)| (key.clone(), to_json(value)))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn scalars_round_trip_through_json() {
        let value = Value::Map(BTreeMap::from([
            ("n".to_owned(), Value::Int(7)),
            ("f".to_owned(), Value::Float(2.5)),
            ("s".to_owned(), Value::Str("hi".to_owned())),
            ("b".to_owned(), Value::Bool(true)),
            ("nil".to_owned(), Value::Null),
            (
                "xs".to_owned(),
                Value::List(vec![Value::Int(1), Value::Int(2)]),
            ),
        ]));
        assert_eq!(from_json(&to_json(&value)), value);
    }

    #[test]
    fn typed_scalars_collapse_to_strings() {
        assert_eq!(
            to_json(&Value::Decimal("9.99".to_owned())),
            Json::String("9.99".to_owned())
        );
        // Round-tripping a typed scalar yields a plain string (lossy, by design).
        assert_eq!(
            from_json(&to_json(&Value::Uuid("u".to_owned()))),
            Value::Str("u".to_owned())
        );
    }

    #[test]
    fn big_int_falls_back_to_float() {
        // > i64::MAX is lossy here (general marshalling), unlike the cursor codec.
        let json: Json = serde_json::from_str("9223372036854775808").unwrap();
        assert!(matches!(from_json(&json), Value::Float(_)));
    }

    #[test]
    fn owned_matches_borrowed() {
        let json: Json =
            serde_json::from_str(r#"{"a":1,"b":"x","c":[true,null,2.5],"d":{"k":"v"}}"#).unwrap();
        assert_eq!(from_json_owned(json.clone()), from_json(&json));
    }
}
