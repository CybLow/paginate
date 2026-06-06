use super::*;
use std::collections::BTreeMap;

fn item(pairs: &[(&str, Value)]) -> Value {
    let mut map = BTreeMap::new();
    for (key, value) in pairs {
        map.insert((*key).to_owned(), value.clone());
    }
    Value::Map(map)
}

fn by(field: &str, direction: SortDirection, nulls: NullsPosition) -> SortSpec {
    SortSpec {
        field: field.to_owned(),
        direction,
        nulls,
    }
}

#[test]
fn ascending_and_descending() {
    let items = vec![
        item(&[("n", Value::Int(3))]),
        item(&[("n", Value::Int(1))]),
        item(&[("n", Value::Int(2))]),
    ];
    let asc = sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]).unwrap();
    assert_eq!(asc, vec![1, 2, 0]);
    let desc = sort_indices(&items, &[by("n", SortDirection::Desc, NullsPosition::Last)]).unwrap();
    assert_eq!(desc, vec![0, 2, 1]);
}

#[test]
fn null_placement() {
    let items = vec![
        item(&[("n", Value::Int(2))]),
        item(&[("n", Value::Null)]),
        item(&[("n", Value::Int(1))]),
    ];
    let last = sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]).unwrap();
    assert_eq!(last, vec![2, 0, 1]); // 1, 2, null
    let first = sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::First)]).unwrap();
    assert_eq!(first, vec![1, 2, 0]); // null, 1, 2
}

#[test]
fn desc_keeps_nulls_last_when_requested() {
    let items = vec![
        item(&[("n", Value::Int(1))]),
        item(&[("n", Value::Null)]),
        item(&[("n", Value::Int(2))]),
    ];
    let idx = sort_indices(&items, &[by("n", SortDirection::Desc, NullsPosition::Last)]).unwrap();
    assert_eq!(idx, vec![2, 0, 1]); // 2, 1, null
}

#[test]
fn multi_key_is_stable() {
    // Sort by group ASC, then by id ASC. Ties on group keep id order.
    let items = vec![
        item(&[("g", Value::Int(1)), ("id", Value::Int(2))]),
        item(&[("g", Value::Int(1)), ("id", Value::Int(1))]),
        item(&[("g", Value::Int(0)), ("id", Value::Int(9))]),
    ];
    let idx = sort_indices(
        &items,
        &[
            by("g", SortDirection::Asc, NullsPosition::Last),
            by("id", SortDirection::Asc, NullsPosition::Last),
        ],
    )
    .unwrap();
    assert_eq!(idx, vec![2, 1, 0]);
}

#[test]
fn missing_field_treated_as_null() {
    let items = vec![
        item(&[("n", Value::Int(1))]),
        item(&[("other", Value::Int(9))]),
    ];
    let idx = sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]).unwrap();
    assert_eq!(idx, vec![0, 1]); // present first, missing (null) last
}

#[test]
fn incomparable_values_error() {
    let items = vec![
        item(&[("n", Value::Int(1))]),
        item(&[("n", Value::Str("x".into()))]),
    ];
    let err = sort_indices(&items, &[by("n", SortDirection::Asc, NullsPosition::Last)]);
    assert!(matches!(err, Err(CoreError::Sort { .. })));
}

#[test]
fn direction_and_nulls_from_token_parse_and_reject() {
    assert_eq!(
        SortDirection::from_token("asc").unwrap(),
        SortDirection::Asc
    );
    assert_eq!(
        SortDirection::from_token("desc").unwrap(),
        SortDirection::Desc
    );
    assert_eq!(
        NullsPosition::from_token("first").unwrap(),
        NullsPosition::First
    );
    assert_eq!(
        NullsPosition::from_token("last").unwrap(),
        NullsPosition::Last
    );
    assert!(matches!(
        SortDirection::from_token("up"),
        Err(CoreError::Sort { .. })
    ));
    assert!(matches!(
        NullsPosition::from_token("middle"),
        Err(CoreError::Sort { .. })
    ));
}
