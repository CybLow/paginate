use super::*;
use std::collections::BTreeMap;

fn item(pairs: &[(&str, &str)]) -> Value {
    let mut map = BTreeMap::new();
    for (key, value) in pairs {
        map.insert((*key).to_owned(), Value::Str((*value).to_owned()));
    }
    Value::Map(map)
}

fn spec(query: &str, fields: &[&str]) -> SearchSpec {
    SearchSpec {
        query: query.to_owned(),
        fields: fields.iter().map(|s| (*s).to_owned()).collect(),
        weights: None,
        mode: SearchFieldMode::Contains,
        fuzzy: FuzzyMode::Exact,
        threshold: 75,
        min_length: 1,
        max_results: None,
    }
}

#[test]
fn single_field_contains_and_ranks() {
    let items = vec![
        item(&[("name", "Alice")]),
        item(&[("name", "Bob")]),
        item(&[("name", "Alicia")]),
    ];
    let idx = search_indices(&items, &spec("ali", &["name"])).unwrap();
    // Both Alice and Alicia contain "ali"; equal score keeps original order.
    assert_eq!(idx, vec![0, 2]);
}

#[test]
fn all_tokens_must_match() {
    let items = vec![
        item(&[("bio", "rust developer")]),
        item(&[("bio", "rust enthusiast")]),
    ];
    let idx = search_indices(&items, &spec("rust developer", &["bio"])).unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn short_query_returns_all() {
    let items = vec![item(&[("name", "Alice")]), item(&[("name", "Bob")])];
    let mut s = spec("ab", &["name"]);
    s.min_length = 3;
    let idx = search_indices(&items, &s).unwrap();
    assert_eq!(idx, vec![0, 1]);
}

#[test]
fn weighted_multi_field_ranks_by_weight() {
    let items = vec![
        item(&[("name", "zeta"), ("bio", "alpha")]),
        item(&[("name", "alpha"), ("bio", "zeta")]),
    ];
    let mut s = spec("alpha", &["name", "bio"]);
    s.weights = Some(BTreeMap::from([("name".to_owned(), 3.0)]));
    let idx = search_indices(&items, &s).unwrap();
    // Item 1 matches "alpha" in the weighted `name` field -> ranks first.
    assert_eq!(idx, vec![1, 0]);
}

#[test]
fn max_results_caps_output() {
    let items = vec![
        item(&[("name", "aaa")]),
        item(&[("name", "aab")]),
        item(&[("name", "aac")]),
    ];
    let mut s = spec("aa", &["name"]);
    s.max_results = Some(2);
    let idx = search_indices(&items, &s).unwrap();
    assert_eq!(idx.len(), 2);
}

#[test]
fn exact_mode_requires_full_value() {
    let items = vec![item(&[("tag", "rust")]), item(&[("tag", "rustacean")])];
    let mut s = spec("rust", &["tag"]);
    s.mode = SearchFieldMode::Exact;
    let idx = search_indices(&items, &s).unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn match_indices_contains_filters_in_original_order() {
    let items = vec![
        item(&[("name", "Alice")]),
        item(&[("name", "Bob")]),
        item(&[("name", "Alicia")]),
    ];
    let fields = ["name".to_owned()];
    let idx = match_indices(
        &items,
        "ali",
        &fields,
        SearchFieldMode::Contains,
        FuzzyMode::Exact,
        75,
    )
    .unwrap();
    assert_eq!(idx, vec![0, 2]);
}

#[test]
fn match_indices_fuzzy_tolerates_typos() {
    let items = vec![item(&[("name", "Alice")]), item(&[("name", "Bob")])];
    let fields = ["name".to_owned()];
    // Trigram containment of "alise" in "alice" is 50 (3 of 6 query trigrams),
    // clearing the default threshold of 30; "bob" shares none -> filtered out.
    let idx = match_indices(
        &items,
        "alise",
        &fields,
        SearchFieldMode::Contains,
        FuzzyMode::Fuzzy,
        30,
    )
    .unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn index_matches_full_scan_for_fuzzy() {
    let items = vec![
        item(&[("title", "The Rust Programming Language")]),
        item(&[("title", "Cooking with Cast Iron")]),
        item(&[("title", "Rust in Action")]),
        item(&[("title", "Programming Pearls")]),
    ];
    let index = TrigramIndex::build(&items);
    for mode in [FuzzyMode::Fuzzy, FuzzyMode::TokenSort] {
        for query in ["rust programing", "cast iron", "pearls", "zzz nomatch"] {
            let mut s = spec(query, &["title"]);
            s.fuzzy = mode;
            s.threshold = 30;
            let full = search_indices(&items, &s).unwrap();
            let indexed = search_with_index(&items, &s, &index).unwrap();
            assert_eq!(full, indexed, "mode={mode:?} query={query}");
        }
    }
}

#[test]
fn trigram_fuzzy_ranks_by_containment() {
    // The typo'd title still ranks its target first (more shared trigrams).
    let items = vec![
        item(&[("title", "The Rust Programming Language")]),
        item(&[("title", "Cooking with Cast Iron")]),
        item(&[("title", "Rust in Action")]),
    ];
    let mut s = spec("rust programing", &["title"]);
    s.fuzzy = FuzzyMode::Fuzzy;
    s.threshold = 30;
    let idx = search_indices(&items, &s).unwrap();
    assert_eq!(idx.first(), Some(&0)); // the Rust programming title wins
    assert!(!idx.contains(&1)); // the unrelated cooking title is excluded
}

#[test]
fn match_indices_token_sort_ignores_word_order() {
    let items = vec![
        item(&[("name", "alice johnson")]),
        item(&[("name", "bob smith")]),
    ];
    let fields = ["name".to_owned()];
    let idx = match_indices(
        &items,
        "johnson alice",
        &fields,
        SearchFieldMode::Contains,
        FuzzyMode::TokenSort,
        90,
    )
    .unwrap();
    assert_eq!(idx, vec![0]);
}

#[test]
fn mode_and_fuzzy_from_token_parse_and_reject() {
    assert_eq!(
        SearchFieldMode::from_token("prefix").unwrap(),
        SearchFieldMode::Prefix
    );
    assert_eq!(
        SearchFieldMode::from_token("contains").unwrap(),
        SearchFieldMode::Contains
    );
    assert_eq!(
        FuzzyMode::from_token("token_sort").unwrap(),
        FuzzyMode::TokenSort
    );
    assert!(matches!(
        SearchFieldMode::from_token("substr"),
        Err(crate::CoreError::Search { .. })
    ));
    assert!(matches!(
        FuzzyMode::from_token("levenshtein"),
        Err(crate::CoreError::Search { .. })
    ));
}
