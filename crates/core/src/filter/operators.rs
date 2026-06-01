//! Evaluation of the comparison, membership, range, and null/empty operators.
//!
//! The string operators (`contains`/`starts_with`/`ends_with`/`like`/`ilike`)
//! and `regex` are compiled with precomputed state in [`super::compile_spec`]
//! and never reach this function.

use std::cmp::Ordering;

use super::FilterOp;
use crate::coerce;
use crate::error::{CoreError, Result};
use crate::value::Value;

pub(super) fn eval_op(op: FilterOp, field: &Value, spec: &Value) -> Result<bool> {
    match op {
        FilterOp::Eq => Ok(coerce::eq(field, spec)),
        FilterOp::Ne => Ok(!coerce::eq(field, spec)),
        FilterOp::Gt => cmp(field, spec, |o| o == Ordering::Greater),
        FilterOp::Gte => cmp(field, spec, |o| o != Ordering::Less),
        FilterOp::Lt => cmp(field, spec, |o| o == Ordering::Less),
        FilterOp::Lte => cmp(field, spec, |o| o != Ordering::Greater),
        FilterOp::In => member(field, spec),
        FilterOp::NotIn => member(field, spec).map(|m| !m),
        FilterOp::Between => between(field, spec),
        FilterOp::IsNull => Ok(field.is_null()),
        FilterOp::IsNotNull => Ok(!field.is_null()),
        FilterOp::Empty => Ok(is_empty(field)),
        FilterOp::NotEmpty => Ok(!is_empty(field)),
        FilterOp::Exists => Ok(true),
        FilterOp::Contains
        | FilterOp::StartsWith
        | FilterOp::EndsWith
        | FilterOp::Like
        | FilterOp::ILike
        | FilterOp::Regex => {
            unreachable!("string/regex operators are compiled separately")
        }
    }
}

fn cmp(field: &Value, spec: &Value, pred: impl Fn(Ordering) -> bool) -> Result<bool> {
    match coerce::compare(field, spec) {
        Some(ordering) => Ok(pred(ordering)),
        None => Err(CoreError::Filter {
            message: format!("{field:?} and {spec:?} are not order-comparable"),
        }),
    }
}

fn member(field: &Value, spec: &Value) -> Result<bool> {
    match spec {
        Value::List(items) => Ok(items.iter().any(|e| coerce::eq(field, e))),
        // `x in "string"` is a substring test in Python.
        Value::Str(haystack) => Ok(haystack.contains(coerce::to_py_str(field).as_str())),
        // `key in dict` is key membership.
        Value::Map(map) => Ok(map.contains_key(coerce::to_py_str(field).as_str())),
        other => Err(CoreError::Filter {
            message: format!("argument of type {other:?} is not iterable"),
        }),
    }
}

fn between(field: &Value, spec: &Value) -> Result<bool> {
    let pair = match spec {
        Value::List(v) if v.len() == 2 => v,
        Value::List(_) => {
            return Err(CoreError::Filter {
                message: "Between requires exactly 2 elements".to_owned(),
            })
        }
        _ => {
            return Err(CoreError::Filter {
                message: "Between requires a two-element sequence".to_owned(),
            })
        }
    };
    let (low, high) = (&pair[0], &pair[1]);
    // `low <= field <= high`, short-circuiting like Python's chained comparison.
    match coerce::compare(low, field) {
        Some(Ordering::Greater) => return Ok(false),
        Some(_) => {}
        None => return Err(not_comparable()),
    }
    match coerce::compare(field, high) {
        Some(ordering) => Ok(ordering != Ordering::Greater),
        None => Err(not_comparable()),
    }
}

fn not_comparable() -> CoreError {
    CoreError::Filter {
        message: "Between bounds are not order-comparable with the field".to_owned(),
    }
}

/// `field is None or field in ("", [])`.
fn is_empty(field: &Value) -> bool {
    match field {
        Value::Null => true,
        Value::Str(s) => s.is_empty(),
        Value::List(l) => l.is_empty(),
        _ => false,
    }
}
