use super::*;
use std::collections::BTreeMap;

fn item(pairs: &[(&str, Value)]) -> Value {
    let mut map = BTreeMap::new();
    for (key, value) in pairs {
        map.insert((*key).to_owned(), value.clone());
    }
    Value::Map(map)
}

fn spec(field: &str, op: FilterOp, value: Value) -> FilterSpec {
    FilterSpec {
        field: field.to_owned(),
        op,
        value,
        logic: FilterLogic::And,
    }
}

fn flat(specs: Vec<FilterSpec>) -> FilterInput {
    FilterInput::Flat(specs)
}

#[test]
fn comparison_and_numeric_equality() {
    let items = vec![
        item(&[("age", Value::Int(20))]),
        item(&[("age", Value::Int(40))]),
        item(&[("age", Value::Int(18))]),
    ];
    let idx = filter_indices(
        &items,
        &flat(vec![spec("age", FilterOp::Gte, Value::Int(20))]),
    )
    .unwrap();
    assert_eq!(idx, vec![0, 1]);
    // 40 == 40.0 (cross-type numeric equality, like Python).
    let idx = filter_indices(
        &items,
        &flat(vec![spec("age", FilterOp::Eq, Value::Float(40.0))]),
    )
    .unwrap();
    assert_eq!(idx, vec![1]);
}

#[test]
fn string_operators() {
    let items = vec![
        item(&[("name", Value::Str("Alice".into()))]),
        item(&[("name", Value::Str("Bob".into()))]),
    ];
    let idx = filter_indices(
        &items,
        &flat(vec![spec(
            "name",
            FilterOp::Contains,
            Value::Str("li".into()),
        )]),
    )
    .unwrap();
    assert_eq!(idx, vec![0]);
    let idx = filter_indices(
        &items,
        &flat(vec![spec("name", FilterOp::Like, Value::Str("Bo%".into()))]),
    )
    .unwrap();
    assert_eq!(idx, vec![1]);
    let idx = filter_indices(
        &items,
        &flat(vec![spec(
            "name",
            FilterOp::ILike,
            Value::Str("%LICE".into()),
        )]),
    )
    .unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn membership_range_and_empty() {
    let items = vec![
        item(&[("s", Value::Str("a".into())), ("n", Value::Int(5))]),
        item(&[("s", Value::Str("".into())), ("n", Value::Int(50))]),
    ];
    let in_list = Value::List(vec![Value::Str("a".into()), Value::Str("b".into())]);
    let idx = filter_indices(&items, &flat(vec![spec("s", FilterOp::In, in_list)])).unwrap();
    assert_eq!(idx, vec![0]);
    let bounds = Value::List(vec![Value::Int(0), Value::Int(10)]);
    let idx = filter_indices(&items, &flat(vec![spec("n", FilterOp::Between, bounds)])).unwrap();
    assert_eq!(idx, vec![0]);
    let idx = filter_indices(&items, &flat(vec![spec("s", FilterOp::Empty, Value::Null)])).unwrap();
    assert_eq!(idx, vec![1]);
}

#[test]
fn regex_operator() {
    let items = vec![
        item(&[("code", Value::Str("AB123".into()))]),
        item(&[("code", Value::Str("xx".into()))]),
    ];
    let idx = filter_indices(
        &items,
        &flat(vec![spec(
            "code",
            FilterOp::Regex,
            Value::Str("[0-9]+".into()),
        )]),
    )
    .unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn nested_group_and_of_or() {
    // (a == 1 OR b == 2) AND c == 3
    let items = vec![
        item(&[
            ("a", Value::Int(1)),
            ("b", Value::Int(0)),
            ("c", Value::Int(3)),
        ]),
        item(&[
            ("a", Value::Int(0)),
            ("b", Value::Int(2)),
            ("c", Value::Int(3)),
        ]),
        item(&[
            ("a", Value::Int(1)),
            ("b", Value::Int(2)),
            ("c", Value::Int(9)),
        ]),
    ];
    let group = FilterGroup {
        logic: FilterLogic::And,
        conditions: vec![
            FilterNode::Group(FilterGroup {
                logic: FilterLogic::Or,
                conditions: vec![
                    FilterNode::Spec(spec("a", FilterOp::Eq, Value::Int(1))),
                    FilterNode::Spec(spec("b", FilterOp::Eq, Value::Int(2))),
                ],
            }),
            FilterNode::Spec(spec("c", FilterOp::Eq, Value::Int(3))),
        ],
    };
    let idx = filter_indices(&items, &FilterInput::Group(group)).unwrap();
    assert_eq!(idx, vec![0, 1]);
}

#[test]
fn flat_or_logic() {
    let items = vec![
        item(&[("name", Value::Str("Alice".into())), ("age", Value::Int(1))]),
        item(&[("name", Value::Str("Bob".into())), ("age", Value::Int(99))]),
        item(&[("name", Value::Str("Cara".into())), ("age", Value::Int(1))]),
    ];
    let specs = vec![
        FilterSpec {
            field: "name".into(),
            op: FilterOp::Eq,
            value: Value::Str("Alice".into()),
            logic: FilterLogic::Or,
        },
        FilterSpec {
            field: "age".into(),
            op: FilterOp::Eq,
            value: Value::Int(99),
            logic: FilterLogic::Or,
        },
    ];
    let idx = filter_indices(&items, &flat(specs)).unwrap();
    assert_eq!(idx, vec![0, 1]);
}

#[test]
fn dotted_path_resolves_nested() {
    let inner = item(&[("age", Value::Int(30))]);
    let items = vec![item(&[("user", inner)])];
    let idx = filter_indices(
        &items,
        &flat(vec![spec("user.age", FilterOp::Gte, Value::Int(18))]),
    )
    .unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn errors_and_edge_cases() {
    let items = vec![item(&[("a", Value::Int(1))])];
    assert!(matches!(
        filter_indices(
            &items,
            &flat(vec![spec("missing", FilterOp::Eq, Value::Int(1))])
        ),
        Err(CoreError::FieldNotFound { .. })
    ));
    assert!(matches!(
        filter_indices(
            &items,
            &flat(vec![spec("_secret", FilterOp::Eq, Value::Int(1))])
        ),
        Err(CoreError::Filter { .. })
    ));
    // Empty filter list returns everything.
    let idx = filter_indices(&items, &flat(vec![])).unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn op_names_round_trip() {
    assert_eq!(FilterOp::from_name("not_in"), Some(FilterOp::NotIn));
    assert_eq!(
        FilterOp::from_name("starts_with"),
        Some(FilterOp::StartsWith)
    );
    assert_eq!(FilterOp::from_name("nope"), None);
}

#[test]
fn filter_logic_from_token_parses_and_rejects() {
    assert_eq!(FilterLogic::from_token("and").unwrap(), FilterLogic::And);
    assert_eq!(FilterLogic::from_token("or").unwrap(), FilterLogic::Or);
    assert!(matches!(
        FilterLogic::from_token("xor"),
        Err(crate::CoreError::Filter { .. })
    ));
}

#[test]
fn remaining_operators_behavior() {
    // Each item has all three fields present (the strict resolver errors on a
    // missing field), with `x` null in items 0 and 2 and `s` empty in item 1.
    let items = vec![
        item(&[
            ("n", Value::Int(10)),
            ("s", Value::Str("apple".into())),
            ("x", Value::Null),
        ]),
        item(&[
            ("n", Value::Int(20)),
            ("s", Value::Str("".into())),
            ("x", Value::Int(1)),
        ]),
        item(&[
            ("n", Value::Int(30)),
            ("s", Value::Str("apricot".into())),
            ("x", Value::Null),
        ]),
    ];
    let run = |op: FilterOp, field: &str, value: Value| {
        filter_indices(&items, &flat(vec![spec(field, op, value)])).unwrap()
    };
    assert_eq!(run(FilterOp::Ne, "n", Value::Int(20)), vec![0, 2]);
    assert_eq!(run(FilterOp::Lt, "n", Value::Int(20)), vec![0]);
    assert_eq!(run(FilterOp::Lte, "n", Value::Int(20)), vec![0, 1]);
    assert_eq!(
        run(FilterOp::StartsWith, "s", Value::Str("ap".into())),
        vec![0, 2]
    );
    assert_eq!(
        run(FilterOp::EndsWith, "s", Value::Str("cot".into())),
        vec![2]
    );
    let not_in = Value::List(vec![Value::Int(10), Value::Int(20)]);
    assert_eq!(run(FilterOp::NotIn, "n", not_in), vec![2]);
    assert_eq!(run(FilterOp::IsNull, "x", Value::Null), vec![0, 2]);
    assert_eq!(run(FilterOp::IsNotNull, "x", Value::Null), vec![1]);
    assert_eq!(run(FilterOp::NotEmpty, "s", Value::Null), vec![0, 2]);
    assert_eq!(run(FilterOp::Exists, "x", Value::Null), vec![0, 1, 2]);
}

#[test]
fn exists_is_false_for_absent_field_not_an_error() {
    let items = vec![
        item(&[("a", Value::Int(1))]),
        item(&[("b", Value::Int(2))]), // "a" absent -> false, not an error
        item(&[("a", Value::Null)]),   // present but null still exists
    ];
    let idx = filter_indices(
        &items,
        &flat(vec![spec("a", FilterOp::Exists, Value::Null)]),
    )
    .unwrap();
    assert_eq!(idx, vec![0, 2]);
}
