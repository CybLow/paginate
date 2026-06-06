//! Filter-engine microbenchmarks: flat single/AND, nested groups, and a string
//! `contains` scan, across the standard size sweep.

use std::hint::black_box;

use criterion::{BenchmarkId, Criterion};

use paginate_core::filter::{filter_indices, FilterGroup, FilterInput, FilterLogic, FilterNode};
use paginate_core::value::Value;

use crate::common::{leaf, make_users, SIZES};

pub fn bench_filter(c: &mut Criterion) {
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
        let contains = FilterInput::Flat(vec![leaf(
            "name",
            "contains",
            Value::Str("3".to_owned()),
            FilterLogic::And,
        )]);

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
