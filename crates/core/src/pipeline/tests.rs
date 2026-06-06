use super::*;
use crate::filter::{FilterLogic, FilterOp, FilterSpec};
use crate::sort::{NullsPosition, SortDirection};
use std::collections::BTreeMap;

fn item(n: i64) -> Value {
    let mut map = BTreeMap::new();
    map.insert("n".to_owned(), Value::Int(n));
    Value::Map(map)
}

fn row(tag: &str, n: i64) -> Value {
    let mut map = BTreeMap::new();
    map.insert("tag".to_owned(), Value::Str(tag.to_owned()));
    map.insert("n".to_owned(), Value::Int(n));
    Value::Map(map)
}

fn contains_search<'a>(query: &'a str, fields: &'a [String]) -> super::SearchStage<'a> {
    super::SearchStage {
        query,
        fields,
        mode: SearchFieldMode::Contains,
        fuzzy: FuzzyMode::Exact,
        threshold: 30,
        index: None,
    }
}

#[test]
fn search_filters_then_sort_orders() {
    // Search keeps tags containing "a"; the explicit sort (n desc) decides
    // order -- search is a filter, not a re-rank.
    let items = vec![
        row("apple", 3),
        row("banana", 1),
        row("avocado", 2),
        row("cherry", 4),
    ];
    let fields = ["tag".to_owned()];
    let search = contains_search("a", &fields);
    let sorts = [SortSpec {
        field: "n".into(),
        direction: SortDirection::Desc,
        nulls: NullsPosition::Last,
    }];
    let page = offset_page_searched(&items, None, None, Some(&search), &sorts, 1, 10).unwrap();
    assert_eq!(page.total, 3); // cherry excluded
    assert_eq!(page.indices, vec![0, 2, 1]); // apple(3), avocado(2), banana(1)
}

#[test]
fn search_none_equals_plain_offset_page() {
    let items: Vec<Value> = (0..12).map(item).collect();
    let with = offset_page_searched(&items, None, None, None, &[], 1, 5).unwrap();
    let plain = offset_page(&items, None, None, &[], 1, 5).unwrap();
    assert_eq!(with, plain);
}

#[test]
fn fuzzy_search_uses_index_with_same_result() {
    let items = vec![
        row("alpha one", 1),
        row("bravo two", 2),
        row("alpine three", 3),
    ];
    let fields = ["tag".to_owned()];
    let index = crate::search::TrigramIndex::build(&items);
    let mut search = contains_search("alpha", &fields);
    search.fuzzy = FuzzyMode::Fuzzy;
    let no_index = offset_page_searched(&items, None, None, Some(&search), &[], 1, 10).unwrap();
    search.index = Some(&index);
    let indexed = offset_page_searched(&items, None, None, Some(&search), &[], 1, 10).unwrap();
    assert_eq!(no_index, indexed);
    assert!(!no_index.indices.contains(&1)); // "bravo two" shares no trigrams
}

#[test]
fn filter_sort_paginate_in_one_pass() {
    // n = 0..20; keep n >= 5 (15 rows); sort desc; page 1, limit 5.
    let items: Vec<Value> = (0..20).map(item).collect();
    let filter = FilterInput::Flat(vec![FilterSpec {
        field: "n".into(),
        op: FilterOp::Gte,
        value: Value::Int(5),
        logic: FilterLogic::And,
    }]);
    let sorts = [SortSpec {
        field: "n".into(),
        direction: SortDirection::Desc,
        nulls: NullsPosition::Last,
    }];
    let page = offset_page(&items, None, Some(&filter), &sorts, 1, 5).unwrap();
    assert_eq!(page.total, 15);
    assert_eq!(page.pages, 3);
    assert!(page.has_next);
    assert!(!page.has_previous);
    // n == original index here, so descending-from-19 gives these indices.
    assert_eq!(page.indices, vec![19, 18, 17, 16, 15]);
}

#[test]
fn page_past_the_end_is_empty() {
    let items: Vec<Value> = (0..10).map(item).collect();
    let page = offset_page(&items, None, None, &[], 99, 5).unwrap();
    assert_eq!(page.total, 10);
    assert!(page.indices.is_empty());
    assert!(!page.has_next);
}

#[test]
fn columnar_path_matches_row_path() {
    // Single int comparison (-> columnar filter) + single-key desc sort
    // (-> columnar sort) must equal the row-engine path exactly.
    let items: Vec<Value> = (0..30).map(item).collect();
    let cols = crate::columnar::Columns::build(&items);
    let filter = FilterInput::Flat(vec![FilterSpec {
        field: "n".into(),
        op: FilterOp::Gte,
        value: Value::Int(10),
        logic: FilterLogic::And,
    }]);
    let sorts = [SortSpec {
        field: "n".into(),
        direction: SortDirection::Desc,
        nulls: NullsPosition::Last,
    }];
    let with_cols = offset_page(&items, Some(&cols), Some(&filter), &sorts, 1, 7).unwrap();
    let row = offset_page(&items, None, Some(&filter), &sorts, 1, 7).unwrap();
    assert_eq!(with_cols, row);
}

#[test]
fn columnar_multi_filter_and_matches_row() {
    // Two flat AND specs, both int-columnar: n >= 10 AND n < 15.
    let items: Vec<Value> = (0..30).map(item).collect();
    let cols = crate::columnar::Columns::build(&items);
    let filter = FilterInput::Flat(vec![
        FilterSpec {
            field: "n".into(),
            op: FilterOp::Gte,
            value: Value::Int(10),
            logic: FilterLogic::And,
        },
        FilterSpec {
            field: "n".into(),
            op: FilterOp::Lt,
            value: Value::Int(15),
            logic: FilterLogic::And,
        },
    ]);
    let with_cols = offset_page(&items, Some(&cols), Some(&filter), &[], 1, 100).unwrap();
    let row = offset_page(&items, None, Some(&filter), &[], 1, 100).unwrap();
    assert_eq!(with_cols, row);
    assert_eq!(with_cols.total, 5); // n in {10, 11, 12, 13, 14}
}

#[test]
fn columnar_bool_filter_matches_row() {
    // A bool field qualifies as a typed column; `active == true` must take
    // the columnar path and equal the row engine exactly.
    let items: Vec<Value> = (0..30)
        .map(|n| {
            let mut map = BTreeMap::new();
            map.insert("n".to_owned(), Value::Int(n));
            map.insert("active".to_owned(), Value::Bool(n % 2 == 0));
            Value::Map(map)
        })
        .collect();
    let cols = crate::columnar::Columns::build(&items);
    let filter = FilterInput::Flat(vec![FilterSpec {
        field: "active".into(),
        op: FilterOp::Eq,
        value: Value::Bool(true),
        logic: FilterLogic::And,
    }]);
    let with_cols = offset_page(&items, Some(&cols), Some(&filter), &[], 1, 100).unwrap();
    let row = offset_page(&items, None, Some(&filter), &[], 1, 100).unwrap();
    assert_eq!(with_cols, row);
    assert_eq!(with_cols.total, 15); // even n in 0..30
}

#[test]
fn columnar_bool_sort_matches_row() {
    // A bool sort key (false < true) must match the row engine.
    let items: Vec<Value> = (0..10)
        .map(|n| {
            let mut map = BTreeMap::new();
            map.insert("n".to_owned(), Value::Int(n));
            map.insert("active".to_owned(), Value::Bool(n % 3 == 0));
            Value::Map(map)
        })
        .collect();
    let cols = crate::columnar::Columns::build(&items);
    let sorts = [SortSpec {
        field: "active".into(),
        direction: SortDirection::Desc,
        nulls: NullsPosition::Last,
    }];
    let with_cols = offset_page(&items, Some(&cols), None, &sorts, 1, 100).unwrap();
    let row = offset_page(&items, None, None, &sorts, 1, 100).unwrap();
    assert_eq!(with_cols, row);
}
