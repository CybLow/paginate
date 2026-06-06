//! Shared dataset generators and spec builders for the engine microbenchmarks.
//!
//! Lives in a subdirectory so criterion's auto-discovery never mistakes it for a
//! bench target; the per-subsystem bench files (`filter`, `sort`, `search`,
//! `pipeline`) pull it in via `crate::common`.

#![allow(dead_code)] // each bench file uses only the subset it needs.

use std::collections::BTreeMap;

use paginate_core::filter::{FilterLogic, FilterOp, FilterSpec};
use paginate_core::search::{FuzzyMode, SearchFieldMode, SearchSpec};
use paginate_core::sort::{NullsPosition, SortDirection, SortSpec};
use paginate_core::value::Value;

/// Row counts every subsystem benchmark sweeps over.
pub const SIZES: [usize; 3] = [1_000, 10_000, 100_000];

/// Dataset mirroring pypaginate's `tests/factories/data.py::make_users`.
pub fn make_users(n: usize) -> Vec<Value> {
    (0..n)
        .map(|i| {
            let mut row = BTreeMap::new();
            row.insert("id".to_owned(), Value::Int(i as i64));
            row.insert("name".to_owned(), Value::Str(format!("User_{i}")));
            row.insert("age".to_owned(), Value::Int(20 + (i % 50) as i64));
            row.insert("email".to_owned(), Value::Str(format!("user{i}@test.com")));
            row.insert("active".to_owned(), Value::Bool(i % 3 != 0));
            Value::Map(row)
        })
        .collect()
}

/// Varied titles so a query is *selective* (the trigram index can prune most
/// rows) — unlike `make_users`, whose names all share the "user" trigrams.
pub fn make_titles(n: usize) -> Vec<Value> {
    const WORDS: [&str; 12] = [
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india",
        "juliet", "kilo", "lima",
    ];
    (0..n)
        .map(|i| {
            let mut row = BTreeMap::new();
            let title = format!(
                "{} {} number {i}",
                WORDS[i % WORDS.len()],
                WORDS[(i / WORDS.len()) % WORDS.len()]
            );
            row.insert("title".to_owned(), Value::Str(title));
            Value::Map(row)
        })
        .collect()
}

/// A single flat filter leaf.
pub fn leaf(field: &str, op: &str, value: Value, logic: FilterLogic) -> FilterSpec {
    FilterSpec {
        field: field.to_owned(),
        op: FilterOp::from_name(op).expect("known operator"),
        value,
        logic,
    }
}

/// A single sort key (nulls last).
pub fn key(field: &str, direction: SortDirection) -> SortSpec {
    SortSpec {
        field: field.to_owned(),
        direction,
        nulls: NullsPosition::Last,
    }
}

/// A search spec with a default threshold of 75.
pub fn search(query: &str, fields: &[&str], mode: SearchFieldMode, fuzzy: FuzzyMode) -> SearchSpec {
    SearchSpec {
        query: query.to_owned(),
        fields: fields.iter().map(|f| (*f).to_owned()).collect(),
        weights: None,
        mode,
        fuzzy,
        threshold: 75,
        min_length: 1,
        max_results: None,
    }
}
