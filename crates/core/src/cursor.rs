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
mod tests {
    use super::*;

    fn round_trip(values: Vec<Value>) {
        let encoded = encode_cursor(&values);
        let decoded = decode_cursor(&encoded).expect("decode");
        assert_eq!(decoded, values, "round-trip mismatch for {encoded}");
    }

    #[test]
    fn golden_vectors_match_python_codec() {
        // Generated by running pypaginate.engine.cursor_codec.encode_cursor on
        // the real package. Byte-identical output proves cross-language cursor
        // compatibility (a cursor minted by Python decodes here and vice versa).
        let cases: &[(Vec<Value>, &str)] = &[
            (vec![Value::Int(1)], "WzFd"),
            (vec![Value::Str("a".into())], "WyJhIl0"),
            (vec![Value::Int(42), Value::Str("hello".into())], "WzQyLCJoZWxsbyJd"),
            (
                vec![Value::Null, Value::Bool(true), Value::Bool(false)],
                "W251bGwsdHJ1ZSxmYWxzZV0",
            ),
            (vec![Value::Str("é".into())], "WyJcdTAwZTkiXQ"),
            (
                vec![Value::Str("café ☕ 🚀".into())],
                "WyJjYWZcdTAwZTkgXHUyNjE1IFx1ZDgzZFx1ZGU4MCJd",
            ),
            (
                vec![Value::Decimal("9.99".into())],
                "W3siX190eXBlX18iOiJkZWNpbWFsIiwidiI6IjkuOTkifV0",
            ),
            (
                vec![Value::DateTime("2025-06-01T12:30:00".into())],
                "W3siX190eXBlX18iOiJkYXRldGltZSIsInYiOiIyMDI1LTA2LTAxVDEyOjMwOjAwIn1d",
            ),
            (
                vec![Value::Date("2025-06-01".into())],
                "W3siX190eXBlX18iOiJkYXRlIiwidiI6IjIwMjUtMDYtMDEifV0",
            ),
            (
                vec![Value::Uuid("12345678-1234-5678-1234-567812345678".into())],
                "W3siX190eXBlX18iOiJ1dWlkIiwidiI6IjEyMzQ1Njc4LTEyMzQtNTY3OC0xMjM0LTU2NzgxMjM0NTY3OCJ9XQ",
            ),
            (vec![Value::Int(-7), Value::Float(1.5)], "Wy03LDEuNV0"),
        ];
        for (values, expected) in cases {
            assert_eq!(&encode_cursor(values), expected, "encode {values:?}");
            assert_eq!(
                &decode_cursor(expected).unwrap(),
                values,
                "decode {expected}"
            );
        }
    }

    #[test]
    fn round_trips_scalars() {
        round_trip(vec![Value::Int(42), Value::Str("hello".into())]);
        round_trip(vec![Value::Null, Value::Bool(true), Value::Bool(false)]);
        round_trip(vec![Value::Float(1.5), Value::Int(-7)]);
    }

    #[test]
    fn round_trips_typed_scalars() {
        round_trip(vec![
            Value::DateTime("2025-06-01T12:30:00".into()),
            Value::Date("2025-06-01".into()),
            Value::Decimal("3.14".into()),
            Value::Uuid("12345678-1234-5678-1234-567812345678".into()),
        ]);
    }

    #[test]
    fn non_ascii_is_escaped_like_ensure_ascii() {
        // json.dumps(ensure_ascii=True) escapes non-ASCII, so the encoded
        // payload stays pure ASCII (é becomes a \uXXXX escape, never raw UTF-8).
        let encoded = encode_cursor(&[Value::Str("é".into())]);
        let bytes = URL_SAFE_NO_PAD.decode(encoded.as_bytes()).unwrap();
        assert!(bytes.is_ascii(), "payload must be pure ASCII");
        // The raw UTF-8 of 'é' (0xC3 0xA9) must be absent — it was escaped.
        assert!(!bytes.windows(2).any(|w| w == [0xc3, 0xa9]));
        // Byte-for-byte identical to the Python codec's output.
        assert_eq!(encoded, "WyJcdTAwZTkiXQ");
        round_trip(vec![Value::Str("café ☕ 🚀".into())]);
    }

    #[test]
    fn typed_tag_wire_shape() {
        let encoded = encode_cursor(&[Value::Decimal("9.99".into())]);
        let bytes = URL_SAFE_NO_PAD.decode(encoded.as_bytes()).unwrap();
        assert_eq!(
            std::str::from_utf8(&bytes).unwrap(),
            r#"[{"__type__":"decimal","v":"9.99"}]"#
        );
    }

    #[test]
    fn rejects_malformed_cursors() {
        assert!(matches!(
            decode_cursor("!!!not-base64!!!"),
            Err(CoreError::InvalidCursor { .. })
        ));
        // Valid base64 of `{}` (an object, not a list).
        let not_a_list = URL_SAFE_NO_PAD.encode(b"{}");
        assert!(matches!(
            decode_cursor(&not_a_list),
            Err(CoreError::InvalidCursor { .. })
        ));
        // Unknown type tag.
        let bad_tag = URL_SAFE_NO_PAD.encode(br#"[{"__type__":"complex","v":"1"}]"#);
        assert!(matches!(
            decode_cursor(&bad_tag),
            Err(CoreError::InvalidCursor { reason }) if reason.contains("complex")
        ));
    }

    #[test]
    fn decodes_padded_and_unpadded() {
        // The Python decoder re-pads; ensure both forms work.
        let unpadded = encode_cursor(&[Value::Str("ab".into())]);
        let padded = format!("{unpadded}{}", "=".repeat((4 - unpadded.len() % 4) % 4));
        assert_eq!(
            decode_cursor(&unpadded).unwrap(),
            decode_cursor(&padded).unwrap()
        );
    }
}
