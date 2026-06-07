//! Column extraction: turn a field into a dense typed [`Column`], or `None` if
//! the field is not the same scalar variant in every row (missing / null / mixed
//! / `NaN` all disqualify it, so the fast path is only taken when it is provably
//! equivalent to the row engine).

use crate::value::Value;

use super::Column;

/// Build a typed column for `field`, seeded by its value in the first row.
pub(super) fn build_column(items: &[Value], field: &str, seed: &Value) -> Option<Column> {
    match seed {
        Value::Int(_) => build_col(items, field, value_as_int).map(Column::Int),
        Value::Float(f) if !f.is_nan() => {
            build_col(items, field, value_as_float).map(Column::Float)
        }
        Value::Str(_) => build_col(items, field, value_as_str).map(Column::Str),
        Value::Bool(_) => build_col(items, field, value_as_bool).map(Column::Bool),
        _ => None,
    }
}

/// Extract a dense `Vec<T>` for `field` across every row, or `None` if any row
/// is missing the field or `extract` rejects its value (wrong variant / `NaN`) —
/// which disqualifies the whole column and sends the query to the row engine.
fn build_col<T>(
    items: &[Value],
    field: &str,
    extract: impl Fn(&Value) -> Option<T>,
) -> Option<Vec<T>> {
    let mut col = Vec::with_capacity(items.len());
    for item in items {
        col.push(extract(field_value(item, field)?)?);
    }
    Some(col)
}

/// The value of `field` in `item`, or `None` if `item` is not a map or the
/// field is absent (either disqualifies the column).
fn field_value<'a>(item: &'a Value, field: &str) -> Option<&'a Value> {
    match item {
        Value::Map(map) => map.get(field),
        _ => None,
    }
}

pub(super) fn value_as_int(value: &Value) -> Option<i64> {
    match value {
        Value::Int(n) => Some(*n),
        _ => None,
    }
}

/// A `NaN` float disqualifies the column (the row engine would error/short-circuit).
fn value_as_float(value: &Value) -> Option<f64> {
    match value {
        Value::Float(f) if !f.is_nan() => Some(*f),
        _ => None,
    }
}

pub(super) fn value_as_str(value: &Value) -> Option<String> {
    match value {
        Value::Str(s) => Some(s.clone()),
        _ => None,
    }
}

pub(super) fn value_as_bool(value: &Value) -> Option<bool> {
    match value {
        Value::Bool(b) => Some(*b),
        _ => None,
    }
}
