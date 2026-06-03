//! Cursor value encoding/decoding for keyset pagination.
//!
//! A faithful port of pypaginate's `engine/cursor_codec.py`. The wire format is
//! **byte-identical** to the Python implementation so a cursor minted by either
//! side decodes in the other:
//!
//! 1. each ordering value is serialised to a JSON-safe form (typed scalars get a
//!    `{"__type__": "...", "v": "..."}` tag);
//! 2. the list is rendered as **compact** JSON (`separators=(",", ":")`) with
//!    **`ensure_ascii=True`** (every non-ASCII char escaped as `\uXXXX`),
//!    exactly like `json.dumps`;
//! 3. the payload is URL-safe base64 with trailing `=` padding stripped.

use std::collections::BTreeMap;

use base64::Engine as _;

use crate::error::{CoreError, Result};
use crate::value::Value;

const URL_SAFE_NO_PAD: base64::engine::GeneralPurpose =
    base64::engine::general_purpose::URL_SAFE_NO_PAD;
const URL_SAFE: base64::engine::GeneralPurpose = base64::engine::general_purpose::URL_SAFE;

/// Encode ordering values into a URL-safe cursor string.
#[must_use]
pub fn encode_cursor(values: &[Value]) -> String {
    let mut payload = String::new();
    write_array(&mut payload, values);
    URL_SAFE_NO_PAD.encode(payload.as_bytes())
}

/// Decode a cursor string back into its ordering values.
///
/// # Errors
/// Returns [`CoreError::InvalidCursor`] if the cursor is not valid base64, not
/// valid UTF-8, not a JSON list, or carries an unknown type tag.
pub fn decode_cursor(cursor: &str) -> Result<Vec<Value>> {
    let bytes = decode_base64(cursor)?;
    let text = std::str::from_utf8(&bytes).map_err(|_| invalid("utf8"))?;
    let parsed: serde_json::Value = serde_json::from_str(text).map_err(|_| invalid("json"))?;
    let array = parsed.as_array().ok_or_else(|| invalid("not a list"))?;
    array.iter().map(json_to_value).collect()
}

fn decode_base64(cursor: &str) -> Result<Vec<u8>> {
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

fn invalid(reason: &str) -> CoreError {
    CoreError::InvalidCursor {
        reason: reason.to_owned(),
    }
}

// -- Serialisation -----------------------------------------------------------

fn write_array(out: &mut String, values: &[Value]) {
    out.push('[');
    for (i, value) in values.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        write_value(out, value);
    }
    out.push(']');
}

fn write_value(out: &mut String, value: &Value) {
    match value {
        Value::Null => out.push_str("null"),
        Value::Bool(true) => out.push_str("true"),
        Value::Bool(false) => out.push_str("false"),
        Value::Int(i) => out.push_str(&i.to_string()),
        Value::Float(f) => write_float(out, *f),
        Value::Str(s) => write_string(out, s),
        Value::DateTime(s) => write_tagged(out, "datetime", s),
        Value::Date(s) => write_tagged(out, "date", s),
        Value::Decimal(s) => write_tagged(out, "decimal", s),
        Value::Uuid(s) => write_tagged(out, "uuid", s),
        Value::List(items) => write_array(out, items),
        Value::Map(map) => write_map(out, map),
        // Cursors are built from scalar ORDER BY columns; bytes are not a valid
        // ordering key. Render lossily so encoding never panics.
        Value::Bytes(b) => write_string(out, &String::from_utf8_lossy(b)),
    }
}

fn write_map(out: &mut String, map: &BTreeMap<String, Value>) {
    out.push('{');
    for (i, (key, value)) in map.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        write_string(out, key);
        out.push(':');
        write_value(out, value);
    }
    out.push('}');
}

fn write_tagged(out: &mut String, tag: &str, raw: &str) {
    // `{"__type__":"<tag>","v":"<raw>"}` — keys in this exact order match the
    // Python dict's insertion order under compact `json.dumps`.
    out.push_str("{\"__type__\":\"");
    out.push_str(tag);
    out.push_str("\",\"v\":");
    write_string(out, raw);
    out.push('}');
}

fn write_float(out: &mut String, f: f64) {
    match serde_json::Number::from_f64(f) {
        Some(n) => out.push_str(&n.to_string()),
        // NaN / ±Inf are not representable in standard JSON and are invalid
        // ordering keys; emit `null` defensively rather than producing garbage.
        None => out.push_str("null"),
    }
}

/// Write `s` as a JSON string with `ensure_ascii=True` semantics, matching
/// CPython's `json.encoder.py_encode_basestring_ascii`.
fn write_string(out: &mut String, s: &str) {
    out.push('"');
    for ch in s.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0c}' => out.push_str("\\f"),
            c if (c as u32) < 0x20 => push_u_escape(out, c as u32),
            c if (c as u32) <= 0x7e => out.push(c),
            c => write_escaped_non_ascii(out, c as u32),
        }
    }
    out.push('"');
}

fn write_escaped_non_ascii(out: &mut String, cp: u32) {
    if cp <= 0xffff {
        push_u_escape(out, cp);
    } else {
        // Encode as a UTF-16 surrogate pair, exactly like CPython.
        let v = cp - 0x1_0000;
        push_u_escape(out, 0xd800 + (v >> 10));
        push_u_escape(out, 0xdc00 + (v & 0x3ff));
    }
}

fn push_u_escape(out: &mut String, code: u32) {
    use std::fmt::Write as _;
    // Lowercase hex, zero-padded to 4 — matches `'\\u{0:04x}'.format(n)`.
    let _ = write!(out, "\\u{code:04x}");
}

// -- Deserialisation ---------------------------------------------------------

fn json_to_value(v: &serde_json::Value) -> Result<Value> {
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

#[cfg(test)]
mod tests;
