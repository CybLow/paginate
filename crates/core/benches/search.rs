//! Search-engine microbenchmarks: exact `contains`, whole-query fuzzy, and the
//! resident trigram index (full scan vs. candidate-pruned) on a selective query.

use std::hint::black_box;

use criterion::{BenchmarkId, Criterion};

use paginate_core::search::{
    search_indices, search_with_index, FuzzyMode, SearchFieldMode, TrigramIndex,
};

use crate::common::{make_titles, make_users, search, SIZES};

pub fn bench_search(c: &mut Criterion) {
    let mut group = c.benchmark_group("search");
    for &n in &SIZES {
        let items = make_users(n);
        let contains = search(
            "user_42",
            &["name"],
            SearchFieldMode::Contains,
            FuzzyMode::Exact,
        );
        let fuzzy = search(
            "user_42",
            &["name", "email"],
            SearchFieldMode::Contains,
            FuzzyMode::Fuzzy,
        );

        group.bench_with_input(BenchmarkId::new("contains", n), &n, |b, _| {
            b.iter(|| search_indices(black_box(&items), black_box(&contains)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("fuzzy_multi", n), &n, |b, _| {
            b.iter(|| search_indices(black_box(&items), black_box(&fuzzy)).unwrap());
        });
    }
    group.finish();
}

/// Fuzzy ranked search: full scan (score every row) vs the resident trigram
/// index (score only candidate rows) for a selective query.
pub fn bench_indexed_search(c: &mut Criterion) {
    let mut group = c.benchmark_group("fuzzy_indexed");
    for &n in &SIZES {
        let items = make_titles(n);
        let index = TrigramIndex::build(&items);
        let mut spec = search(
            "alpha bravo",
            &["title"],
            SearchFieldMode::Contains,
            FuzzyMode::Fuzzy,
        );
        spec.threshold = 30;

        group.bench_with_input(BenchmarkId::new("full_scan", n), &n, |b, _| {
            b.iter(|| search_indices(black_box(&items), black_box(&spec)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("indexed", n), &n, |b, _| {
            b.iter(|| {
                search_with_index(black_box(&items), black_box(&spec), black_box(&index)).unwrap()
            });
        });
    }
    group.finish();
}
