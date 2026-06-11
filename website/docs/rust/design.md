---
sidebar_position: 3
title: Design
---

# Design

The core is built so that **one implementation** can serve every language without
re-implementation or drift. The high-level shape — fat core, thin adapters — is in the
[architecture overview](../general/architecture); this page covers the core's own
internals.

## The `Value` model

The boundary is a single small enum, `Value`:

```text
Null | Bool | Int | Float | Str | Bytes | List | Map
  + typed scalars: DateTime | Date | Decimal | Uuid
```

- A **record** is a `Value::Map` (string-keyed); a dataset is a slice of them.
- The **typed scalars** carry their canonical string form (`isoformat()` for datetime,
  the canonical decimal/uuid string), so they compare and round-trip through cursors
  with full fidelity.
- Nothing host-specific — no ORM rows, framework types, or interpreter objects — ever
  crosses the boundary. The adapter converts host objects to/from `Value` and hands the
  core nothing else.

Because the contract is just plain data, the same crate links into Python (PyO3) and
Node/TypeScript (napi-rs) and compiles to `wasm32` unchanged.

## Index-based returns

The cursor codec and pagination math move only a few scalars, so they're a clear native
win. The in-memory engines are the interesting case — every item's fields must cross
the boundary — so the core is careful to **never clone rows**:

- `filter`, `sort`, and `search` return a `Vec<usize>` of **indices** (a selection or a
  permutation), and the adapter selects from the original host objects by index.
- An ORM model therefore **never round-trips** through Rust as data; only the fields a
  spec references are projected to `Value`.

## The columnar fast path

For a **resident** dataset (one built once and queried many times), fields that hold the
*same scalar type in every row* (`i64` / `f64` / `String`) are projected into a dense,
typed `Vec` — `Columns`. The filter and sort stages then scan that typed column with no
per-row map lookup and no `Value` dispatch.

A column is built **only** when the field is that exact scalar in every row, so the
typed scan can't diverge from the row engine — results stay byte-identical. Anything
the columnar path can't serve (`OR`, nested groups, mixed-type fields) transparently
falls back to the row engine.

## Single source of truth

The core owns the **canonical domain contract** so the bindings never redefine it:

- **Enums & specs** (`FilterLogic`, `FilterOp`, `SortDirection`, `NullsPosition`,
  `SearchFieldMode`, `FuzzyMode`, and the `*Spec` structs) live once and are re-exported
  flat from the crate root.
- **String ↔ enum parsing** lives once, so the wire vocabulary has one home and an
  unknown token **fails fast** at the boundary instead of silently defaulting.
- **The error taxonomy** is `CoreError` (`#[non_exhaustive]`); each binding *maps* it to
  a host exception rather than defining a parallel set.
- **The type shapes** are emitted as a single JSON Schema (the `schema` feature), from
  which the Python dataclasses and TypeScript interfaces are generated.

## Ports & adapters

The core is the **domain engine**: it has no knowledge of ORMs, databases, HTTP, or any
host runtime. Responsibilities split cleanly:

| Concern | Owner |
|---|---|
| ORM (SQLAlchemy / Prisma / Drizzle / …) | language adapter |
| Object ↔ `Value` mapping | adapter |
| DB transaction / session lifecycle | adapter |
| Cursor, pagination, filter, sort, search | **core** |

## How parity is verified

The core's correctness — and its agreement with the language packages — is checked three
ways:

1. **In-language tests** — `cargo test` unit cases plus `proptest` properties (cursor
   round-trip, filter-never-adds, sort permutation/idempotence, search-subset,
   `max_results` cap, columnar == row-engine equivalence).
2. **Cross-language golden vectors** — the cursor wire format is asserted
   **byte-identical** to output from the real Python codec, including non-ASCII and
   astral surrogate pairs.
3. **A frozen golden fixture** asserted by Rust, Python, and TypeScript in CI — see
   [cross-language parity](../general/parity).

The crate is `#![forbid(unsafe_code)]` and `#![warn(missing_docs)]`.

## Next

- [Performance](./performance) — the measured boundary trade-offs.
- Full API: [docs.rs/paginate-core](https://docs.rs/paginate-core).
