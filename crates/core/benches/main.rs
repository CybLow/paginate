//! Criterion microbenchmarks for the in-memory engine hot paths.
//!
//! These measure the row engine / columnar paths in isolation (no FFI
//! marshalling) so optimizations to filter dispatch, columnar build, and search
//! normalization can be judged on real before/after numbers and guarded against
//! regression. Run: `cargo bench -p paginate-core` (release; criterion forces
//! optimized builds). Filter to a group with e.g. `cargo bench -- filter`.
//!
//! Each subsystem lives in its own file (`filter`, `sort`, `search`,
//! `pipeline`); shared dataset/spec builders live in [`common`]. This single
//! bench target wires them together so there is one `criterion_main`.

mod common;
mod filter;
mod pipeline;
mod search;
mod sort;

use criterion::{criterion_group, criterion_main};

criterion_group!(
    benches,
    filter::bench_filter,
    sort::bench_sort,
    search::bench_search,
    search::bench_indexed_search,
    pipeline::bench_pipeline,
);
criterion_main!(benches);
