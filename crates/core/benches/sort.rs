//! Sort-engine microbenchmarks: single/multi integer keys and a string key.

use std::hint::black_box;

use criterion::{BenchmarkId, Criterion};

use paginate_core::sort::{sort_indices, SortDirection};

use crate::common::{key, make_users, SIZES};

pub fn bench_sort(c: &mut Criterion) {
    let mut group = c.benchmark_group("sort");
    for &n in &SIZES {
        let items = make_users(n);
        let single = vec![key("age", SortDirection::Desc)];
        let multi = vec![
            key("age", SortDirection::Asc),
            key("id", SortDirection::Desc),
        ];
        let by_str = vec![key("name", SortDirection::Asc)];

        group.bench_with_input(BenchmarkId::new("single_int", n), &n, |b, _| {
            b.iter(|| sort_indices(black_box(&items), black_box(&single)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("multi_int", n), &n, |b, _| {
            b.iter(|| sort_indices(black_box(&items), black_box(&multi)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("single_str", n), &n, |b, _| {
            b.iter(|| sort_indices(black_box(&items), black_box(&by_str)).unwrap());
        });
    }
    group.finish();
}
