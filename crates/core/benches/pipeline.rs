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
    }
    group.finish();
}
