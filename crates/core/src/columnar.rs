//! Typed columns for a fast single-field filter and single-key sort path.
//!
//! The row engine resolves a `BTreeMap` lookup per item per field and dispatches
//! on `Value`; for a tight `age >= 500` / `name == "x"` / `price < 9.99` query
//! that overhead dominates. When a field holds the **same scalar type in every
//! row**, we keep it as a dense typed `Vec` (`i64`/`f64`/`String`) and scan it
//! directly — no map lookup, no `Value` dispatch.
//!
//! Correctness over cleverness. A column is built **only** if the field is that
//! exact scalar in every row (no missing, null, mixed, or — for floats — `NaN`),
//! and a fast path is taken **only** for operators whose typed comparison
//! provably equals the row engine's [`coerce`] semantics:
//!
//! * **Int** — exact `i64` order and equality (matches `coerce::compare`'s exact
//!   `(Int, Int)` arm and, after the matching fix, `coerce::eq`).
//! * **Float** — `f64` order/equality after coercing the needle through
//!   [`coerce::as_number`] (so `price > 5` works); a `NaN` needle or column is
//!   never fast-pathed (it would error/short-circuit in the row engine).
//! * **Str** — byte order (== Unicode code-point order for UTF-8, which is what
//!   `coerce::compare` uses) and exact equality.
//!
//! Anything else — an unknown field, a string/regex operator, a value whose
//! coercion can't be proven equal — returns `None`, and the caller falls back to
//! the row engine. Silently correct beats cleverly wrong.

use std::cmp::Ordering;
use std::collections::BTreeMap;

use crate::coerce;
use crate::filter::FilterOp;
use crate::sort::SortDirection;
use crate::value::Value;

/// A dense, single-type column extracted from every row of a dataset.
enum Column {
    Int(Vec<i64>),
    Float(Vec<f64>),
    Str(Vec<String>),
}

/// Dense typed columns keyed by field name (only fully-typed, NaN-free fields).
pub struct Columns {
    columns: BTreeMap<String, Column>,
}

impl Columns {
    /// Build typed columns from `items`. A field qualifies only if it is the
    /// same scalar variant (`Int`/`Float`/`Str`) in every row — floats must also
    /// be non-`NaN`. The first row seeds the candidate type per field.
    #[must_use]
    pub fn build(items: &[Value]) -> Self {
        let mut columns = BTreeMap::new();
        let Some(Value::Map(first)) = items.first() else {
            return Self { columns };
        };
        for (field, seed) in first {
            if let Some(column) = build_column(items, field, seed) {
                columns.insert(field.clone(), column);
            }
        }
        Self { columns }
    }

    /// Fast filter for a single comparison/equality op on a typed column, or
    /// `None` when this path does not apply (unknown field, unsupported
    /// operator, or a value whose coercion can't be proven equal to the row
    /// engine). Returns matching indices in ascending order — identical to
    /// [`crate::filter::filter_indices`].
    #[must_use]
    pub fn filter(&self, field: &str, op: FilterOp, value: &Value) -> Option<Vec<usize>> {
        match self.columns.get(field)? {
            Column::Int(col) => filter_int(col, op, value),
            Column::Float(col) => filter_float(col, op, value),
            Column::Str(col) => filter_str(col, op, value),
        }
    }

    /// Sort an existing index list by a single typed column, preserving relative
    /// order for equal keys (stable). Returns `None` for the fallback case (the
    /// field is not a typed column). A typed column has no nulls, so null
    /// placement is irrelevant; the result matches [`crate::sort::sort_indices`]
    /// for a single key.
    #[must_use]
    pub fn sort_subset(
        &self,
        order: &[usize],
        field: &str,
        direction: SortDirection,
    ) -> Option<Vec<usize>> {
        let column = self.columns.get(field)?; // unknown field -> fall back, no clone
        let mut order = order.to_vec();
        let desc = direction == SortDirection::Desc;
        match column {
            Column::Int(col) => order.sort_by(|&a, &b| oriented(col[a].cmp(&col[b]), desc)),
            // No NaN in the column (build disqualifies it), so `partial_cmp` is
            // total; `Equal` is an unreachable safety default.
            Column::Float(col) => order.sort_by(|&a, &b| {
                oriented(col[a].partial_cmp(&col[b]).unwrap_or(Ordering::Equal), desc)
            }),
            Column::Str(col) => order.sort_by(|&a, &b| oriented(col[a].cmp(&col[b]), desc)),
        }
        Some(order)
    }
}

/// Reverse an ordering for descending sorts (keeps stability via `sort_by`).
fn oriented(ordering: Ordering, desc: bool) -> Ordering {
    if desc {
        ordering.reverse()
    } else {
        ordering
    }
}

fn build_column(items: &[Value], field: &str, seed: &Value) -> Option<Column> {
    match seed {
        Value::Int(_) => build_int(items, field),
        Value::Float(f) if !f.is_nan() => build_float(items, field),
        Value::Str(_) => build_str(items, field),
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

fn collect(len: usize, keep: impl Fn(usize) -> bool) -> Vec<usize> {
    (0..len).filter(|&i| keep(i)).collect()
}

fn filter_int(col: &[i64], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    let &Value::Int(needle) = value else {
        return None; // non-int needle (e.g. `age > 2.5`) -> row engine via as_number
    };
    let keep: fn(&i64, &i64) -> bool = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

fn filter_float(col: &[f64], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    let needle = coerce::as_number(value)?; // Int/Float/Bool/Decimal -> f64, else fallback
    if needle.is_nan() {
        return None; // row engine errors (ordered) or all-false (eq); let it decide
    }
    let keep: fn(&f64, &f64) -> bool = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

fn filter_str(col: &[String], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    let Value::Str(needle) = value else {
        return None; // non-string needle -> row engine (type-aware eq / as_text)
    };
    let keep: fn(&str, &str) -> bool = comparison(op)?;
    Some(collect(col.len(), |i| {
        keep(col[i].as_str(), needle.as_str())
    }))
}

/// The six order/equality operators as a comparison function, or `None` for any
/// operator the columnar path does not handle (string ops, ranges, null/empty).
fn comparison<T: PartialOrd + ?Sized>(op: FilterOp) -> Option<fn(&T, &T) -> bool> {
    Some(match op {
        FilterOp::Gt => |a, b| a > b,
        FilterOp::Gte => |a, b| a >= b,
        FilterOp::Lt => |a, b| a < b,
        FilterOp::Lte => |a, b| a <= b,
        FilterOp::Eq => |a, b| a == b,
        FilterOp::Ne => |a, b| a != b,
        _ => return None,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::filter::{filter_indices, FilterInput, FilterLogic, FilterSpec};
    use crate::sort::{sort_indices, NullsPosition, SortSpec};

    fn item(pairs: &[(&str, Value)]) -> Value {
        let mut map = BTreeMap::new();
        for (key, value) in pairs {
            map.insert((*key).to_owned(), value.clone());
        }
        Value::Map(map)
    }

    fn row_filter(items: &[Value], field: &str, op: FilterOp, value: Value) -> Vec<usize> {
        filter_indices(
            items,
            &FilterInput::Flat(vec![FilterSpec {
                field: field.into(),
                op,
                value,
                logic: FilterLogic::And,
            }]),
        )
        .unwrap()
    }

    const OPS: [FilterOp; 6] = [
        FilterOp::Gt,
        FilterOp::Gte,
        FilterOp::Lt,
        FilterOp::Lte,
        FilterOp::Eq,
        FilterOp::Ne,
    ];

    #[test]
    fn int_columnar_matches_row_engine() {
        let items: Vec<Value> = (0..50).map(|i| item(&[("age", Value::Int(i))])).collect();
        let cols = Columns::build(&items);
        for op in OPS {
            let columnar = cols.filter("age", op, &Value::Int(30)).unwrap();
            assert_eq!(
                columnar,
                row_filter(&items, "age", op, Value::Int(30)),
                "{op:?}"
            );
        }
    }

    #[test]
    fn float_columnar_matches_row_engine() {
        let items: Vec<Value> = (0..50)
            .map(|i| item(&[("p", Value::Float(f64::from(i) / 2.0))]))
            .collect();
        let cols = Columns::build(&items);
        // Float needle and an int needle (cross-type coercion, `p > 5`).
        for needle in [Value::Float(9.5), Value::Int(5)] {
            for op in OPS {
                let columnar = cols.filter("p", op, &needle).unwrap();
                let row = row_filter(&items, "p", op, needle.clone());
                assert_eq!(columnar, row, "{op:?} {needle:?}");
            }
        }
    }

    #[test]
    fn str_columnar_matches_row_engine() {
        let names = ["alice", "bob", "carol", "bob", "dave"];
        let items: Vec<Value> = names
            .iter()
            .map(|n| item(&[("name", Value::Str((*n).into()))]))
            .collect();
        let cols = Columns::build(&items);
        for op in OPS {
            let needle = Value::Str("bob".into());
            let columnar = cols.filter("name", op, &needle).unwrap();
            assert_eq!(columnar, row_filter(&items, "name", op, needle), "{op:?}");
        }
    }

    #[test]
    fn columnar_sort_matches_row_engine() {
        let items = vec![
            item(&[("n", Value::Int(3)), ("s", Value::Str("c".into()))]),
            item(&[("n", Value::Int(1)), ("s", Value::Str("a".into()))]),
            item(&[("n", Value::Int(2)), ("s", Value::Str("b".into()))]),
        ];
        let cols = Columns::build(&items);
        for (field, dir) in [
            ("n", SortDirection::Asc),
            ("n", SortDirection::Desc),
            ("s", SortDirection::Asc),
            ("s", SortDirection::Desc),
        ] {
            let order: Vec<usize> = (0..items.len()).collect();
            let columnar = cols.sort_subset(&order, field, dir).unwrap();
            let row = sort_indices(
                &items,
                &[SortSpec {
                    field: field.into(),
                    direction: dir,
                    nulls: NullsPosition::Last,
                }],
            )
            .unwrap();
            assert_eq!(columnar, row, "{field} {dir:?}");
        }
    }

    #[test]
    fn float_sort_is_stable_and_matches_row_engine() {
        // Ties on the float key must preserve input order (stable), like the row
        // engine's repeated stable sort.
        let items: Vec<Value> = [1.0, 1.0, 0.5, 2.0, 0.5]
            .iter()
            .map(|f| item(&[("p", Value::Float(*f))]))
            .collect();
        let cols = Columns::build(&items);
        let order: Vec<usize> = (0..items.len()).collect();
        let columnar = cols.sort_subset(&order, "p", SortDirection::Asc).unwrap();
        let row = sort_indices(
            &items,
            &[SortSpec {
                field: "p".into(),
                direction: SortDirection::Asc,
                nulls: NullsPosition::Last,
            }],
        )
        .unwrap();
        assert_eq!(columnar, row);
    }

    #[test]
    fn disqualifies_mixed_null_or_nan_fields() {
        // A null in an otherwise-int field disqualifies it.
        let with_null = vec![item(&[("a", Value::Int(1))]), item(&[("a", Value::Null)])];
        assert!(Columns::build(&with_null)
            .filter("a", FilterOp::Gte, &Value::Int(0))
            .is_none());
        // Mixed int/float disqualifies (row engine coerces; column can't be typed).
        let mixed = vec![
            item(&[("a", Value::Int(1))]),
            item(&[("a", Value::Float(2.0))]),
        ];
        assert!(Columns::build(&mixed)
            .filter("a", FilterOp::Gte, &Value::Int(0))
            .is_none());
        // A NaN disqualifies a float field.
        let nan = vec![
            item(&[("a", Value::Float(1.0))]),
            item(&[("a", Value::Float(f64::NAN))]),
        ];
        assert!(Columns::build(&nan)
            .filter("a", FilterOp::Lt, &Value::Float(5.0))
            .is_none());
    }

    #[test]
    fn unsupported_ops_and_fields_fall_back() {
        let items: Vec<Value> = (0..5).map(|i| item(&[("age", Value::Int(i))])).collect();
        let cols = Columns::build(&items);
        // String operator on an int column -> not handled.
        assert!(cols
            .filter("age", FilterOp::Contains, &Value::Int(1))
            .is_none());
        // Unknown field / non-int needle on int column -> fall back.
        assert!(cols
            .filter("missing", FilterOp::Eq, &Value::Int(1))
            .is_none());
        assert!(cols
            .filter("age", FilterOp::Eq, &Value::Float(1.5))
            .is_none());
        assert!(cols
            .sort_subset(&[0], "missing", SortDirection::Asc)
            .is_none());
    }

    #[test]
    fn large_integers_filter_exactly() {
        // Two ints that collapse to one f64; exact i64 eq must distinguish them.
        let items = vec![
            item(&[("id", Value::Int(9_007_199_254_740_992))]),
            item(&[("id", Value::Int(9_007_199_254_740_993))]),
        ];
        let cols = Columns::build(&items);
        let needle = Value::Int(9_007_199_254_740_992);
        let columnar = cols.filter("id", FilterOp::Eq, &needle).unwrap();
        assert_eq!(columnar, vec![0]);
        assert_eq!(columnar, row_filter(&items, "id", FilterOp::Eq, needle));
    }
}
