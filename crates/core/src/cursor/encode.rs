//! Serialisation half of the cursor codec: render ordering values as the exact
//! compact, `ensure_ascii=True` JSON CPython's `json.dumps` produces, so the
//! base64 payload is byte-identical to pypaginate's.

use std::collections::BTreeMap;

use crate::value::Value;

/// Render `values` as a compact JSON array into `out`.
pub(super) fn write_array(out: &mut String, values: &[Value]) {
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
