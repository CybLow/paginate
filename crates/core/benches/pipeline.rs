//! Pure-engine pipeline ceiling (marshalling excluded): the row engine vs. the
//! columnar fast path for `filter → sort → offset_page`, including a multi-AND
//! that is now fully columnar thanks to Bool columns.

use std::hint::black_box;

use criterion::{BenchmarkId, Criterion};

use paginate_core::columnar::Columns;
use paginate_core::filter::{FilterInput, FilterLogic};
use paginate_core::pipeline::offset_page;
use paginate_core::sort::SortDirection;
use paginate_core::value::Value;

use crate::common::{key, leaf, make_users, SIZES};

pub fn bench_pipeline(c: &mut Criterion) {
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
                offset_page(
                    black_box(&items),
                    Some(&columns),
                    Some(&filter),
                    &sorts,
                    1,
                    20,
                )
                .unwrap()
            });
        });

        // Multi-AND including a bool field — now fully columnar (was row-only
        // because `active` had no typed column before Bool columns).
        let and_bool = FilterInput::Flat(vec![
            leaf("age", "gte", Value::Int(25), FilterLogic::And),
            leaf("active", "eq", Value::Bool(true), FilterLogic::And),
        ]);
        group.bench_with_input(BenchmarkId::new("and_bool_row", n), &n, |b, _| {
            b.iter(|| offset_page(black_box(&items), None, Some(&and_bool), &[], 1, 20).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("and_bool_columnar", n), &n, |b, _| {
            b.iter(|| {
                offset_page(
                    black_box(&items),
                    Some(&columns),
                    Some(&and_bool),
                    &[],
                    1,
                    20,
                )
                .unwrap()
            });
        });

        // String filter (`name contains "3"`): row-only before the Str-column
        // substring fast path, now columnar. The standalone filter/contains bench
        // calls the row engine directly, so this pair is what measures the win.
        let contains = FilterInput::Flat(vec![leaf(
            "name",
            "contains",
            Value::Str("3".into()),
            FilterLogic::And,
        )]);
        group.bench_with_input(BenchmarkId::new("contains_row", n), &n, |b, _| {
            b.iter(|| offset_page(black_box(&items), None, Some(&contains), &[], 1, 20).unwrap());
        });
        group.bench_with_input(BenchmarkId::new("contains_columnar", n), &n, |b, _| {
            b.iter(|| {
                offset_page(
                    black_box(&items),
                    Some(&columns),
                    Some(&contains),
                    &[],
                    1,
                    20,
                )
                .unwrap()
            });
        });

        // Range + membership filters: row-only before, now columnar.
        let between = FilterInput::Flat(vec![leaf(
            "age",
            "between",
            Value::List(vec![Value::Int(25), Value::Int(60)]),
            FilterLogic::And,
        )]);
        let in_ids = FilterInput::Flat(vec![leaf(
            "id",
            "in",
            Value::List((0..64).map(|k| Value::Int(k * 101 % 100_000)).collect()),
            FilterLogic::And,
        )]);
        let like = FilterInput::Flat(vec![leaf(
            "name",
            "like",
            Value::Str("User_3%".into()),
            FilterLogic::And,
        )]);
        for (name, filter) in [("between", &between), ("in", &in_ids), ("like", &like)] {
            group.bench_with_input(BenchmarkId::new(format!("{name}_row"), n), &n, |b, _| {
                b.iter(|| offset_page(black_box(&items), None, Some(filter), &[], 1, 20).unwrap());
            });
            group.bench_with_input(
                BenchmarkId::new(format!("{name}_columnar"), n),
                &n,
                |b, _| {
                    b.iter(|| {
                        offset_page(black_box(&items), Some(&columns), Some(filter), &[], 1, 20)
                            .unwrap()
                    });
                },
            );
        }
    }
    group.finish();
}
