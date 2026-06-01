//! The plain, language-agnostic value model that crosses the FFI boundary.
//!
//! [`Value`] is intentionally small and JSON-shaped. The binding layer converts
//! host objects (Python `dict`/`datetime`/`Decimal`/..., or a JS object) into
//! `Value`, the core does its work, and the binding converts back. Keeping this
//! the *only* shared vocabulary is what makes the core reusable across runtimes.

use std::collections::BTreeMap;

/// A single language-agnostic value.
///
/// The first variants map 1:1 onto JSON. The trailing typed-scalar variants
/// (`DateTime`, `Date`, `Decimal`, `Uuid`) exist so the cursor codec can
/// round-trip ordering keys with full fidelity — they carry the value's
/// canonical string form and the binding layer rebuilds the rich host type.
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    /// Absence of a value (`None` / `null`).
    Null,
    /// Boolean.
    Bool(bool),
    /// 64-bit signed integer.
    Int(i64),
    /// 64-bit float.
    Float(f64),
    /// UTF-8 string.
    Str(String),
    /// Opaque bytes.
    Bytes(Vec<u8>),
    /// Ordered list of values.
    List(Vec<Value>),
    /// String-keyed map (an item / record).
    Map(BTreeMap<String, Value>),
    /// ISO-8601 datetime (carried as its `isoformat()` string).
    DateTime(String),
    /// ISO-8601 date.
    Date(String),
    /// Arbitrary-precision decimal (carried as its canonical string).
    Decimal(String),
    /// UUID (carried as its canonical hyphenated string).
    Uuid(String),
}

impl Value {
    /// True when this value represents the absence of data.
    #[must_use]
    pub fn is_null(&self) -> bool {
        matches!(self, Value::Null)
    }

    /// Borrow the inner string for the textual variants, else `None`.
    #[must_use]
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Value::Str(s)
            | Value::DateTime(s)
            | Value::Date(s)
            | Value::Decimal(s)
            | Value::Uuid(s) => Some(s),
            _ => None,
        }
    }
}
