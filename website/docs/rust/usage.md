---
sidebar_position: 2
title: Using the core
---

# Using the core

This page orients you in the crate; for exact signatures see
[docs.rs/paginate-core](https://docs.rs/paginate-core).

```toml
[dependencies]
paginate-core = "0.1"
```

## The `Value` model

The engine speaks only `Value`, a small JSON-like enum. Host data is converted to
`Value` at the boundary; nothing host-specific ever enters the core:

```rust
pub enum Value {
    Null,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(String),
    Bytes(Vec<u8>),
    List(Vec<Value>),
    Map(BTreeMap<String, Value>),  // an item / record
    // Typed scalars carry their canonical string so cursors round-trip exactly:
    DateTime(String),
    Date(String),
    Decimal(String),
    Uuid(String),
}
```

A record is a `Value::Map`; a dataset is a `&[Value]` of maps.

## The cursor codec

`encode_cursor` and `decode_cursor` are the portable, typed wire format — the same
bytes a Python or TypeScript service produces:

```rust
use paginate_core::{encode_cursor, decode_cursor, Value};

let cursor = encode_cursor(&[
    Value::Int(42),
    Value::DateTime("2025-06-01T00:00:00".to_string()),
])?;

let values = decode_cursor(&cursor)?; // Vec<Value> — round-trips exactly
```

## Pagination, filter, sort, search

The in-memory pipeline runs **filter → search → sort → paginate** in one call,
returning the page's indices plus offset metadata; you select your own rows by index:

```rust
use paginate_core::{offset_page, SortSpec};

// items: &[Value] of Value::Map records
let page = offset_page(
    items,
    None,                       // optional columnar projection (Columns)
    None,                       // optional filter (FilterInput)
    &[/* SortSpec { .. } */],   // sort keys
    /* page */ 1,
    /* limit */ 20,
)?;
// page.indices -> the rows on this page; page.total -> match count
```

For repeated queries over a stable dataset, build a `Columns` projection once and pass
it in — the filter and sort stages take the typed columnar fast path. See
[performance](./performance).

## Feature flags

| Feature | Default | Enables |
|---|---|---|
| `schema` | off | The `schema` module + JSON-Schema export — the single source of truth for the generated Python / TS types. The published engine carries no `schemars` dependency by default. |

## Errors

All fallible calls return `Result<T, CoreError>`. `CoreError` is `#[non_exhaustive]`
and classified by `ErrorKind`; each language binding maps it to a host-native
exception with a matching hierarchy.

## Next

- [Design](./design) — the boundary, index returns, and the columnar path.
- [Performance](./performance) — where native wins, measured.
- Full API: [docs.rs/paginate-core](https://docs.rs/paginate-core).
