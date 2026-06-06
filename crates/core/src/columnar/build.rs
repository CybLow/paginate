//! Column extraction: turn a field into a dense typed [`Column`], or `None` if
//! the field is not the same scalar variant in every row (missing / null / mixed
//! / `NaN` all disqualify it, so the fast path is only taken when it is provably
//! equivalent to the row engine).

use crate::value::Value;

use super::Column;

/// Build a typed column for `field`, seeded by its value in the first row.
pub(super) fn build_column(items: &[Value], field: &str, seed: &Value) -> Option<Column> {
    match seed {
        Value::Int(_) => build_int(items, field),
        Value::Float(f) if !f.is_nan() => build_float(items, field),
        Value::Str(_) => build_str(items, field),
        Value::Bool(_) => build_bool(items, field),
        _ => None,
    }
}

/// The value of `field` in `item`, or `None` if `item` is not a map or the
/// field is absent (either disqualifies the column).
fn field_value<'a>(item: &'a Value, field: &str) -> Option<&'a Value> {
    match item {
        Value::Map(map) => map.get(field),
        _ => None,
    }
}

fn build_int(items: &[Value], field: &str) -> Option<Column> {
    let mut col = Vec::with_capacity(items.len());
    for item in items {
        match field_value(item, field)? {
            Value::Int(n) => col.push(*n),
            _ => return None, // missing / null / non-int -> disqualify
        }
    }
    Some(Column::Int(col))
}

fn build_float(items: &[Value], field: &str) -> Option<Column> {
    let mut col = Vec::with_capacity(items.len());
    for item in items {
        match field_value(item, field)? {
            Value::Float(f) if !f.is_nan() => col.push(*f),
            _ => return None, // non-float, NaN, or missing -> disqualify
        }
    }
    Some(Column::Float(col))
}

fn build_str(items: &[Value], field: &str) -> Option<Column> {
    let mut col = Vec::with_capacity(items.len());
    for item in items {
        match field_value(item, field)? {
            Value::Str(s) => col.push(s.clone()),
            _ => return None, // non-string / missing -> disqualify
        }
    }
    Some(Column::Str(col))
}

fn build_bool(items: &[Value], field: &str) -> Option<Column> {
    let mut col = Vec::with_capacity(items.len());
    for item in items {
        match field_value(item, field)? {
            Value::Bool(b) => col.push(*b),
            _ => return None, // non-bool / missing -> disqualify
        }
    }
    Some(Column::Bool(col))
}
