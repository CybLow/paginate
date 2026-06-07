//! Property-based tests mirroring pypaginate's Hypothesis invariants
//! (`tests/property/`). These are the algebraic laws the engines must obey for
//! any input — the gold standard for proving the Rust port behaves like Python.

use std::collections::BTreeMap;

use proptest::prelude::*;

use paginate_core::filter::{FilterInput, FilterLogic, FilterOp, FilterSpec};
use paginate_core::normalize::{normalize_text, normalize_text_cow};
use paginate_core::search::{FuzzyMode, SearchFieldMode, SearchSpec};
use paginate_core::sort::{NullsPosition, SortDirection, SortSpec};
use paginate_core::{cursor, filter, pagination, search, sort, Value};

/// Strategy for a scalar cursor value (exact JSON round-trip).
fn scalar() -> impl Strategy<Value = Value> {
    prop_oneof![
        Just(Value::Null),
        any::<bool>().prop_map(Value::Bool),
        any::<i64>().prop_map(Value::Int),
        ".*".prop_map(Value::Str),
    ]
}

/// A single-field item `{ "n": <int> }`.
fn int_item(n: i64) -> Value {
    let mut map = BTreeMap::new();
    map.insert("n".to_owned(), Value::Int(n));
    Value::Map(map)
}

/// A single-field item `{ "t": <string> }`.
fn text_item(s: &str) -> Value {
    let mut map = BTreeMap::new();
    map.insert("t".to_owned(), Value::Str(s.to_owned()));
    Value::Map(map)
}

proptest! {
    /// Cursor codec round-trips: decode(encode(v)) == v.
    #[test]
    fn cursor_round_trips(values in prop::collection::vec(scalar(), 0..8)) {
        let encoded = cursor::encode_cursor(&values).expect("encode");
        let decoded = cursor::decode_cursor(&encoded).expect("valid cursor");
        prop_assert_eq!(decoded, values);
    }

    /// Pagination metadata is internally consistent.
    #[test]
    fn pagination_meta_is_consistent(page in 1u64..1000, limit in 1u64..1000, total in 0u64..1_000_000) {
        let lim = pagination::Limit::new(limit).unwrap();
        let meta = pagination::offset_meta(page, lim, total);
        prop_assert_eq!(meta.has_next, page < meta.pages);
        prop_assert_eq!(meta.has_previous, page > 1);
        prop_assert_eq!(pagination::offset(page, lim), (page - 1) * limit);
    }

    /// Filtering never adds items, and every match satisfies the predicate.
    #[test]
    fn filter_gte_never_adds_and_all_match(
        ns in prop::collection::vec(any::<i64>(), 0..60),
        threshold in any::<i64>(),
    ) {
        let items: Vec<Value> = ns.iter().map(|n| int_item(*n)).collect();
        let spec = FilterSpec {
            field: "n".to_owned(),
            op: FilterOp::Gte,
            value: Value::Int(threshold),
            logic: FilterLogic::And,
        };
        let idx = filter::filter_indices(&items, &FilterInput::Flat(vec![spec])).unwrap();
        prop_assert!(idx.len() <= items.len());
        for &i in &idx {
            prop_assert!(ns[i] >= threshold);
        }
    }

    /// An empty filter list returns every item, in order.
    #[test]
    fn filter_empty_returns_all(ns in prop::collection::vec(any::<i64>(), 0..60)) {
        let items: Vec<Value> = ns.iter().map(|n| int_item(*n)).collect();
        let idx = filter::filter_indices(&items, &FilterInput::Flat(vec![])).unwrap();
        prop_assert_eq!(idx, (0..items.len()).collect::<Vec<_>>());
    }

    /// Sorting is a permutation (preserves every element) and is monotonic.
    #[test]
    fn sort_is_permutation_and_monotonic(ns in prop::collection::vec(any::<i64>(), 0..60)) {
        let items: Vec<Value> = ns.iter().map(|n| int_item(*n)).collect();
        let spec = SortSpec {
            field: "n".to_owned(),
            direction: SortDirection::Asc,
            nulls: NullsPosition::Last,
        };
        let idx = sort::sort_indices(&items, std::slice::from_ref(&spec)).unwrap();

        let mut as_permutation = idx.clone();
        as_permutation.sort_unstable();
        prop_assert_eq!(as_permutation, (0..items.len()).collect::<Vec<_>>());

        let ordered: Vec<i64> = idx.iter().map(|&i| ns[i]).collect();
        for window in ordered.windows(2) {
            prop_assert!(window[0] <= window[1]);
        }
    }

    /// Sorting is idempotent: sorting the sorted order changes nothing.
    #[test]
    fn sort_is_idempotent(ns in prop::collection::vec(any::<i64>(), 0..60)) {
        let items: Vec<Value> = ns.iter().map(|n| int_item(*n)).collect();
        let spec = SortSpec {
            field: "n".to_owned(),
            direction: SortDirection::Asc,
            nulls: NullsPosition::Last,
        };
        let once = sort::apply(&items, std::slice::from_ref(&spec)).unwrap();
        let twice = sort::apply(&once, std::slice::from_ref(&spec)).unwrap();
        prop_assert_eq!(once, twice);
    }

    /// Search returns a subset of the input with valid indices.
    #[test]
    fn search_is_subset(
        strings in prop::collection::vec(".*", 0..40),
        query in ".*",
    ) {
        let items: Vec<Value> = strings.iter().map(|s| text_item(s)).collect();
        let spec = SearchSpec {
            query,
            fields: vec!["t".to_owned()],
            weights: None,
            mode: SearchFieldMode::Contains,
            fuzzy: FuzzyMode::Exact,
            threshold: 75,
            min_length: 1,
            max_results: None,
        };
        let idx = search::search_indices(&items, &spec).unwrap();
        prop_assert!(idx.len() <= items.len());
        for &i in &idx {
            prop_assert!(i < items.len());
        }
    }

    /// `max_results` always caps the search output length.
    #[test]
    fn search_max_results_caps(
        strings in prop::collection::vec("[a-c]{1,4}", 1..40),
        cap in 0usize..10,
    ) {
        let items: Vec<Value> = strings.iter().map(|s| text_item(s)).collect();
        let spec = SearchSpec {
            query: "a".to_owned(),
            fields: vec!["t".to_owned()],
            weights: None,
            mode: SearchFieldMode::Contains,
            fuzzy: FuzzyMode::Exact,
            threshold: 75,
            min_length: 1,
            max_results: Some(cap),
        };
        let idx = search::search_indices(&items, &spec).unwrap();
        prop_assert!(idx.len() <= cap);
    }

    /// The borrowing normalizer must never disagree with the owned one — the
    /// `is_ascii_normalized` fast path is correctness-critical (a wrong "already
    /// normalized" verdict would silently corrupt search). Stress case +
    /// whitespace, where the predicate logic lives.
    #[test]
    fn normalize_cow_equals_owned(s in "[a-zA-Z0-9 \t\n]{0,16}") {
        let borrowed = normalize_text_cow(&s);
        let owned = normalize_text(&s);
        prop_assert_eq!(borrowed.as_ref(), owned.as_str());
    }
}
