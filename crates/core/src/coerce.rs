//! Python-semantics operations on [`Value`]: ordering, equality, and
//! stringification. Shared by the filter operators and the sort engine so both
//! agree on what "greater than", "equal", and `str(x)` mean.
//!
//! The model mirrors CPython's behaviour for the cases that actually occur in
//! pagination data:
//!
//! * **Numbers** (`int`, `float`, `bool`, `Decimal`) compare and compare-equal
//!   across types, like Python (`1 == 1.0`, `True == 1`, `2.5 > 2`).
//! * **Text** (`str` and the ISO-carrying typed scalars) compares by Unicode
//!   code point — which for UTF-8 is byte order.
//! * **Mismatched kinds** are *not* comparable (Python raises `TypeError`); we
//!   return `None`, and the caller turns that into an error.

use std::borrow::Cow;
use std::cmp::Ordering;

use crate::value::Value;

/// Numeric view of a value (bool as 0/1, decimal parsed), or `None`.
#[must_use]
pub fn as_number(v: &Value) -> Option<f64> {
    match v {
        Value::Int(i) => Some(*i as f64),
        Value::Float(f) => Some(*f),
        Value::Bool(b) => Some(if *b { 1.0 } else { 0.0 }),
        Value::Decimal(s) => s.parse::<f64>().ok(),
        _ => None,
    }
}

/// Textual view of a value, or `None`.
fn as_text(v: &Value) -> Option<&str> {
    match v {
        Value::Str(s) | Value::DateTime(s) | Value::Date(s) | Value::Uuid(s) => Some(s),
        _ => None,
    }
}

/// Compare two values with Python ordering semantics.
///
/// Returns `None` when the values are not order-comparable (mismatched kinds,
/// or a `NaN` operand) — mirroring a Python `TypeError`.
#[must_use]
pub fn compare(a: &Value, b: &Value) -> Option<Ordering> {
    match (a, b) {
        // Exact integer / bool comparison avoids the f64 precision loss that
        // would bite very large integers.
        (Value::Int(x), Value::Int(y)) => Some(x.cmp(y)),
        (Value::Bool(x), Value::Bool(y)) => Some(x.cmp(y)),
        _ => {
            if let (Some(x), Some(y)) = (as_number(a), as_number(b)) {
                return x.partial_cmp(&y);
            }
            if let (Some(x), Some(y)) = (as_text(a), as_text(b)) {
                return Some(x.cmp(y));
            }
            if a.is_null() && b.is_null() {
                return Some(Ordering::Equal);
            }
            None
        }
    }
}

/// Equality with Python `==` semantics (`1 == 1.0`, `True == 1`, but
/// `str("x") != datetime("x")`).
#[must_use]
pub fn eq(a: &Value, b: &Value) -> bool {
    match (a, b) {
        (Value::Null, Value::Null) => true,
        (Value::List(x), Value::List(y)) => {
            x.len() == y.len() && x.iter().zip(y).all(|(p, q)| eq(p, q))
        }
        (Value::Map(x), Value::Map(y)) => {
            x.len() == y.len() && x.iter().all(|(k, v)| y.get(k).is_some_and(|w| eq(v, w)))
        }
        (Value::Str(x), Value::Str(y)) => x == y,
        (Value::DateTime(x), Value::DateTime(y)) => x == y,
        (Value::Date(x), Value::Date(y)) => x == y,
        (Value::Uuid(x), Value::Uuid(y)) => x == y,
        (Value::Bytes(x), Value::Bytes(y)) => x == y,
        // Exact integer equality (matches `compare` and Python's arbitrary-
        // precision `==`); the f64 fallback below collapses ints past 2^53.
        (Value::Int(x), Value::Int(y)) => x == y,
        _ => match (as_number(a), as_number(b)) {
            (Some(x), Some(y)) => x == y,
            _ => false,
        },
    }
}

/// `str(value)` with Python semantics for the scalar cases that matter to the
/// string operators (`contains`, `starts_with`, ...), **borrowing** the
/// string-carrying variants so the per-item field side allocates nothing (the
/// hot path — field values feeding those operators are virtually always strings).
#[must_use]
pub fn to_py_str_cow(v: &Value) -> Cow<'_, str> {
    match v {
        Value::Str(s)
        | Value::DateTime(s)
        | Value::Date(s)
        | Value::Decimal(s)
        | Value::Uuid(s) => Cow::Borrowed(s),
        Value::Int(i) => Cow::Owned(i.to_string()),
        // `{:?}` keeps the trailing `.0` on integral floats, like Python's repr.
        Value::Float(f) => Cow::Owned(format!("{f:?}")),
        Value::Bool(true) => Cow::Borrowed("True"),
        Value::Bool(false) => Cow::Borrowed("False"),
        Value::Null => Cow::Borrowed("None"),
        Value::Bytes(b) => Cow::Owned(String::from_utf8_lossy(b).into_owned()),
        Value::List(_) | Value::Map(_) => Cow::Owned(format!("{v:?}")),
    }
}

/// Owned `str(value)` — see [`to_py_str_cow`]. Used for the spec side, which is
/// stringified once at compile time rather than per item.
#[must_use]
pub fn to_py_str(v: &Value) -> String {
    to_py_str_cow(v).into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cmp::Ordering::{Equal, Greater, Less};

    #[test]
    fn numbers_compare_across_types() {
        assert_eq!(compare(&Value::Int(2), &Value::Float(2.5)), Some(Less));
        assert_eq!(compare(&Value::Float(3.0), &Value::Int(3)), Some(Equal));
        assert_eq!(compare(&Value::Int(10), &Value::Int(2)), Some(Greater));
        assert_eq!(compare(&Value::Bool(true), &Value::Int(0)), Some(Greater));
    }

    #[test]
    fn text_compares_by_code_point() {
        assert_eq!(
            compare(&Value::Str("apple".into()), &Value::Str("banana".into())),
            Some(Less)
        );
        // ISO datetimes order correctly as strings.
        assert_eq!(
            compare(
                &Value::DateTime("2025-01-01T00:00:00".into()),
                &Value::DateTime("2025-06-01T00:00:00".into())
            ),
            Some(Less)
        );
    }

    #[test]
    fn mismatched_kinds_are_incomparable() {
        assert_eq!(compare(&Value::Str("1".into()), &Value::Int(1)), None);
        assert_eq!(compare(&Value::Null, &Value::Int(1)), None);
    }

    #[test]
    fn equality_is_python_like() {
        assert!(eq(&Value::Int(1), &Value::Float(1.0)));
        assert!(eq(&Value::Bool(true), &Value::Int(1)));
        assert!(eq(&Value::Null, &Value::Null));
        assert!(eq(&Value::Str("x".into()), &Value::Str("x".into())));
        // str("x") != datetime("x") — type matters.
        assert!(!eq(&Value::Str("x".into()), &Value::DateTime("x".into())));
        assert!(!eq(&Value::Int(1), &Value::Str("1".into())));
    }

    #[test]
    fn large_integers_compare_exactly() {
        // 2^53 and 2^53 + 1 are distinct integers that collapse to one f64.
        let a = Value::Int(9_007_199_254_740_992);
        let b = Value::Int(9_007_199_254_740_993);
        assert!(!eq(&a, &b));
        assert_eq!(compare(&a, &b), Some(Less));
    }

    #[test]
    fn stringification_matches_python_str() {
        assert_eq!(to_py_str(&Value::Int(42)), "42");
        assert_eq!(to_py_str(&Value::Float(2.0)), "2.0");
        assert_eq!(to_py_str(&Value::Bool(true)), "True");
        assert_eq!(to_py_str(&Value::Null), "None");
        assert_eq!(to_py_str(&Value::Str("hi".into())), "hi");
    }
}
