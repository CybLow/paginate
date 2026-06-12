---
sidebar_position: 11
title: Glossary
description: Definitions of the core terms used across paginate — offset, keyset, cursor, spec, operator, marshalling, columnar, Dataset, and more.
---

# Glossary

**Offset pagination** — Addressing a page by a 1-based page number and a limit
(rows per page). Simple, supports jump-to-page and a total count. See
[pagination models](./pagination-models).

**Keyset / cursor pagination** — Addressing a page by the ordering values of the last
row seen, carried as an opaque cursor. Stable under writes and fast at depth. See
[pagination models](./pagination-models#keyset-cursor-pagination).

**Cursor** — An opaque, URL-safe string encoding the ordering values of a boundary row.
Typed and deterministic, so it round-trips across languages. See [cursors](./cursors).

**Spec** — A small declarative description of an operation: `FilterSpec`, `SortSpec`, or
`SearchSpec`. A dataclass in Python, a plain object in TypeScript; both generated from
one schema.

**Operator** — One of the 20 filter comparisons (`eq`, `gte`, `contains`, `between`,
`in`, `regex`, …), expressed as a plain string. See [filtering](./filtering).

**Filter group** — A nested boolean tree built with `And()` / `Or()`, up to 5 levels
deep. See [filtering](./filtering#combining-conditions).

**Dotted field path** — A `"a.b.c"` path that resolves through nested maps to reach a
value on each item (e.g. `"address.city"`).

**Null placement** — Where missing / null values sort, set per key with
`nulls: "first" | "last"`, independent of direction. See [sorting](./sorting#null-placement).

**Stable sort** — A sort in which items that compare equal keep their original relative
order — the basis for predictable multi-key sorting.

**Token matching** — The default search mode: the query is split into tokens, and an
item matches only when every token is found in a searched field. See [search](./search).

**Trigram** — An overlapping 3-character slice of a string (the PostgreSQL `pg_trgm`
model), used to score fuzzy similarity. See [search](./search#fuzzy-trigram-scoring).

**Fuzzy search** — Typo-tolerant matching via trigram similarity (`fuzzy: "fuzzy"` or
`"token_sort"`), scored 0–100 against a `threshold`.

**Adapter** — The thin, per-language layer that maps host objects / ORM rows to the
plain data the core understands and selects results by index. The ORM lives here, never
in the core. See [architecture](./architecture).

**Marshalling** — Converting host data into the core's `Value` model to cross the FFI
boundary. The cost the engine is designed to minimize — see
[architecture](./architecture#marshalling-build-once-query-many).

**Value** — The small JSON-like enum the core speaks (`Null | Bool | Int | Float | Str |
List | Map`, plus typed scalars). Nothing host-specific crosses the boundary. See
[Rust design](../rust/design#the-value-model).

**Index-based return** — `filter` / `sort` / `search` return a list of indices; the
adapter selects your original objects, so rows are never copied through the core.

**Columnar fast path** — A dense, typed projection (`Columns`) built once for a resident
`Dataset`, accelerating the filter and sort stages. See [performance](../rust/performance).

**Dataset (resident)** — An in-memory dataset marshalled into the core once, then queried
many times. **Build once, query many.** See [Python](../python/pagination#the-resident-dataset)
/ [TypeScript](../typescript/pagination#the-resident-dataset).

**Parity** — The guarantee that every language package returns identical results and
byte-identical cursors, pinned by a golden fixture in CI. See [parity](./parity).

**`MAX_LIMIT`** — The shared maximum page size (a DoS guard), defined once in the core
and exposed by every package.
