//! Typed integer columns for a fast single-field numeric filter path.
//!
//! The row engine resolves a `BTreeMap` lookup per item per field; for a tight
//! `age >= 500`-style filter that map lookup dominates. When a field is an
//! integer in **every** row, we keep it as a dense `Vec<i64>` and scan it
//! directly — no map lookup, no `Value` dispatch.
//!
//! Correctness over cleverness: a column is built **only** if the field is
//! `Int` in every row (no missing, null, float, or other type). That guarantees
//! the columnar result is identical to the row engine's, so the fast path is
//! always safe to take when it applies; anything else falls back to the rows.

use std::collections::BTreeMap;

use crate::filter::FilterOp;
use crate::value::Value;

/// Dense `i64` columns keyed by field name (only fully-integer fields).
pub struct IntColumns {
    columns: BTreeMap<String, Vec<i64>>,
}

impl IntColumns {
    /// Build integer columns from `items`. A field qualifies only if it is
    /// `Value::Int` in every row.
    #[must_use]
    pub fn build(items: &[Value]) -> Self {
        let mut columns = BTreeMap::new();
        let Some(Value::Map(first)) = items.first() else {
            return Self { columns };
        };
        'field: for (field, value) in first {
            if !matches!(value, Value::Int(_)) {
                continue;
            }
            let mut column = Vec::with_capacity(items.len());
            for item in items {
                match item {
                    Value::Map(map) => match map.get(field) {
                        Some(Value::Int(n)) => column.push(*n),
                        _ => continue 'field, // missing / null / non-int -> disqualify
                    },
                    _ => continue 'field,
                }
            }
            columns.insert(field.clone(), column);
        }
        Self { columns }
    }

    /// Fast filter for a single integer comparison, or `None` if this path does
    /// not apply (unknown field, or a non-comparison operator). Returns matching
    /// indices in ascending order — identical to the row engine.
    #[must_use]
    pub fn filter(&self, field: &str, op: FilterOp, value: i64) -> Option<Vec<usize>> {
        let column = self.columns.get(field)?;
        let keep: fn(i64, i64) -> bool = match op {
            FilterOp::Gt => |a, b| a > b,
            FilterOp::Gte => |a, b| a >= b,
            FilterOp::Lt => |a, b| a < b,
            FilterOp::Lte => |a, b| a <= b,
            FilterOp::Eq => |a, b| a == b,
            FilterOp::Ne => |a, b| a != b,
            _ => return None,
        };
        Some(
            (0..column.len())
                .filter(|&i| keep(column[i], value))
                .collect(),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::filter::{FilterInput, FilterLogic, FilterSpec};

    fn item(pairs: &[(&str, Value)]) -> Value {
        let mut map = BTreeMap::new();
        for (k, v) in pairs {
            map.insert((*k).to_owned(), v.clone());
        }
        Value::Map(map)
    }

    #[test]
    fn columnar_matches_row_engine() {
        let items: Vec<Value> = (0..50)
            .map(|i| {
                item(&[
                    ("age", Value::Int(i)),
                    ("name", Value::Str(format!("u{i}"))),
                ])
            })
            .collect();
        let cols = IntColumns::build(&items);
        // `age` qualifies (all Int); `name` does not (Str).
        let columnar = cols.filter("age", FilterOp::Gte, 30).unwrap();
        let row = crate::filter::filter_indices(
            &items,
            &FilterInput::Flat(vec![FilterSpec {
                field: "age".into(),
                op: FilterOp::Gte,
                value: Value::Int(30),
                logic: FilterLogic::And,
            }]),
        )
        .unwrap();
        assert_eq!(columnar, row);
        assert!(cols.filter("name", FilterOp::Gte, 30).is_none()); // not an int column
        assert!(cols.filter("age", FilterOp::Contains, 30).is_none()); // not a comparison
    }

    #[test]
    fn disqualifies_fields_with_a_non_int_or_missing_value() {
        let items = vec![
            item(&[("a", Value::Int(1))]),
            item(&[("a", Value::Null)]), // null -> `a` disqualified
        ];
        assert!(IntColumns::build(&items)
            .filter("a", FilterOp::Gte, 0)
            .is_none());
    }
}
