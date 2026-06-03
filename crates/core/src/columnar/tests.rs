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
        let columnar = cols.sort_subset(&order, &[(field, dir)]).unwrap();
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
    let columnar = cols
        .sort_subset(&order, &[("p", SortDirection::Asc)])
        .unwrap();
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
fn multi_key_sort_matches_row_engine() {
    // group asc, then id desc — both typed int columns.
    let items = vec![
        item(&[("g", Value::Int(1)), ("id", Value::Int(2))]),
        item(&[("g", Value::Int(1)), ("id", Value::Int(5))]),
        item(&[("g", Value::Int(0)), ("id", Value::Int(9))]),
    ];
    let cols = Columns::build(&items);
    let order: Vec<usize> = (0..items.len()).collect();
    let columnar = cols
        .sort_subset(
            &order,
            &[("g", SortDirection::Asc), ("id", SortDirection::Desc)],
        )
        .unwrap();
    let row = sort_indices(
        &items,
        &[
            SortSpec {
                field: "g".into(),
                direction: SortDirection::Asc,
                nulls: NullsPosition::Last,
            },
            SortSpec {
                field: "id".into(),
                direction: SortDirection::Desc,
                nulls: NullsPosition::Last,
            },
        ],
    )
    .unwrap();
    assert_eq!(columnar, row);
}

#[test]
fn multi_key_sort_falls_back_when_a_key_is_not_a_column() {
    // `x` is null in every row -> not a typed column -> the whole sort falls back.
    let items = vec![
        item(&[("g", Value::Int(1)), ("x", Value::Null)]),
        item(&[("g", Value::Int(0)), ("x", Value::Null)]),
    ];
    let cols = Columns::build(&items);
    assert!(cols
        .sort_subset(
            &[0, 1],
            &[("g", SortDirection::Asc), ("x", SortDirection::Asc)]
        )
        .is_none());
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
        .sort_subset(&[0], &[("missing", SortDirection::Asc)])
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
