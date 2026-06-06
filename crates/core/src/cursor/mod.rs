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
//!
//! [`encode`] owns step 1-2 (serialisation); [`decode`] owns the reverse.

mod decode;
mod encode;

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
    encode::write_array(&mut payload, values);
    URL_SAFE_NO_PAD.encode(payload.as_bytes())
}

/// Decode a cursor string back into its ordering values.
///
/// # Errors
/// Returns [`CoreError::InvalidCursor`] if the cursor is not valid base64, not
/// valid UTF-8, not a JSON list, or carries an unknown type tag.
pub fn decode_cursor(cursor: &str) -> Result<Vec<Value>> {
    let bytes = decode::decode_base64(cursor)?;
    let text = std::str::from_utf8(&bytes).map_err(|_| invalid("utf8"))?;
    let parsed: serde_json::Value = serde_json::from_str(text).map_err(|_| invalid("json"))?;
    let array = parsed.as_array().ok_or_else(|| invalid("not a list"))?;
    array.iter().map(decode::json_to_value).collect()
}

/// Construct an [`CoreError::InvalidCursor`] with a machine-readable `reason`.
fn invalid(reason: &str) -> CoreError {
    CoreError::InvalidCursor {
        reason: reason.to_owned(),
    }
}

#[cfg(test)]
mod tests;
