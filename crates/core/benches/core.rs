//! Criterion microbenchmarks for the in-memory engine hot paths.
//!
//! These measure the row engine / columnar paths in isolation (no FFI
//! marshalling) so optimizations to filter dispatch, columnar build, and search
//! normalization can be judged on real before/after numbers and guarded against
//! regression. Run: `cargo bench -p paginate-core` (release; criterion forces
//! optimized builds). Filter to a group with e.g. `cargo bench -- filter`.

use std::collections::BTreeMap;
use std::hint::black_box;

use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};

use paginate_core::columnar::Columns;
use paginate_core::filter::{
    filter_indices, FilterGroup, FilterInput, FilterLogic, FilterNode, FilterOp, FilterSpec,
};
use paginate_core::pipeline::offset_page;
use paginate_core::search::{search_indices, FuzzyMode, SearchFieldMode, SearchSpec};
use paginate_core::sort::{sort_indices, NullsPosition, SortDirection, SortSpec};
use paginate_core::value::Value;

const SIZES: [usize; 3] = [1_000, 10_000, 100_000];

/// Dataset mirroring pypaginate's `tests/factories/data.py::make_users`.
fn make_users(n: usize) -> Vec<Value> {
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

fn leaf(field: &str, op: &str, value: Value, logic: FilterLogic) -> FilterSpec {
    FilterSpec {
        field: field.to_owned(),
        op: FilterOp::from_name(op).expect("known operator"),
        value,
        logic,
    }
}

fn key(field: &str, direction: SortDirection) -> SortSpec {
    SortSpec {
        field: field.to_owned(),
        direction,
        nulls: NullsPosition::Last,
    }
}

fn search(query: &str, fields: &[&str], mode: SearchFieldMode, fuzzy: FuzzyMode) -> SearchSpec {
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

fn bench_filter(c: &mut Criterion) {
    let mut group = c.benchmark_group("filter");
    for &n in &SIZES {
        let items = make_users(n);
        let single = FilterInput::Flat(vec![leaf("age", "gte", Value::Int(30), FilterLogic::And)]);
        let and3 = FilterInput::Flat(vec![
            leaf("age", "gte", Value::Int(25), FilterLogic::And),
            leaf("age", "lt", Value::Int(60), FilterLogic::And),
            leaf("active", "eq", Value::Bool(true), FilterLogic::And),
        ]);
        // (age < 25 OR age >= 60) AND active == true
        let nested = FilterInput::Group(FilterGroup {
            logic: FilterLogic::And,
            conditions: vec![
                FilterNode::Group(FilterGroup {
                    logic: FilterLogic::Or,
                    conditions: vec![
                        FilterNode::Spec(leaf("age", "lt", Value::Int(25), FilterLogic::And)),
                        FilterNode::Spec(leaf("age", "gte", Value::Int(60), FilterLogic::And)),
                    ],
                }),
                FilterNode::Spec(leaf("active", "eq", Value::Bool(true), FilterLogic::And)),
            ],
        });
        let contains =
            FilterInput::Flat(vec![leaf("name", "contains", Value::Str("3".to_owned()), FilterLogic::And)]);

        group.bench_with_input(BenchmarkId::new("flat_single", n), &n, |b, _| {
            b.iter(|| filter_indices(black_box(&items), black_box(&single)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("flat_and3", n), &n, |b, _| {
            b.iter(|| filter_indices(black_box(&items), black_box(&and3)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("nested_group", n), &n, |b, _| {
            b.iter(|| filter_indices(black_box(&items), black_box(&nested)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("contains", n), &n, |b, _| {
            b.iter(|| filter_indices(black_box(&items), black_box(&contains)).unwrap());
        });
    }
    group.finish();
}

fn bench_sort(c: &mut Criterion) {
    let mut group = c.benchmark_group("sort");
    for &n in &SIZES {
        let items = make_users(n);
        let single = vec![key("age", SortDirection::Desc)];
        let multi = vec![key("age", SortDirection::Asc), key("id", SortDirection::Desc)];
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

fn bench_search(c: &mut Criterion) {
    let mut group = c.benchmark_group("search");
    for &n in &SIZES {
        let items = make_users(n);
        let contains = search("user_42", &["name"], SearchFieldMode::Contains, FuzzyMode::Exact);
        let fuzzy = search("user_42", &["name", "email"], SearchFieldMode::Contains, FuzzyMode::Fuzzy);

        group.bench_with_input(BenchmarkId::new("contains", n), &n, |b, _| {
            b.iter(|| search_indices(black_box(&items), black_box(&contains)).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("fuzzy_multi", n), &n, |b, _| {
            b.iter(|| search_indices(black_box(&items), black_box(&fuzzy)).unwrap());
        });
    }
    group.finish();
}

/// Pure-engine pipeline ceiling: row engine vs columnar (marshalling excluded).
fn bench_pipeline(c: &mut Criterion) {
    let mut group = c.benchmark_group("pipeline_offset_page");
    for &n in &SIZES {
        let items = make_users(n);
        let columns = Columns::build(&items);
        let filter = FilterInput::Flat(vec![leaf("age", "gte", Value::Int(30), FilterLogic::And)]);
        let sorts = vec![key("age", SortDirection::Desc)];

        group.bench_with_input(BenchmarkId::new("row", n), &n, |b, _| {
            b.iter(|| offset_page(black_box(&items), None, Some(&filter), &sorts, 1, 20).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("columnar", n), &n, |b, _| {
            b.iter(|| {
                offset_page(black_box(&items), Some(&columns), Some(&filter), &sorts, 1, 20).unwrap()
            });
        });
    }
    group.finish();
}

criterion_group!(benches, bench_filter, bench_sort, bench_search, bench_pipeline);
criterion_main!(benches);
