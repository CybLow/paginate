---
sidebar_position: 1
title: Overview
description: paginate-core is the pure, language-agnostic Rust engine the Python and TypeScript packages wrap — embed it directly or read how it works.
---

# Rust core — `paginate-core`

[`paginate-core`](https://crates.io/crates/paginate-core) is the pure,
language-agnostic engine behind the whole project. The Python (`pypaginate`) and
TypeScript (`@cyblow/paginate`) packages are thin native bindings over it — so this
crate is where the actual algorithms live.

```toml
[dependencies]
paginate-core = "0.1"
```

➡️ **API reference: [docs.rs/paginate-core](https://docs.rs/paginate-core)** — the
canonical, auto-published Rust documentation.

## What it owns

Everything computational, exactly once:

- **Cursor codec** — `encode_cursor` / `decode_cursor`, a typed, URL-safe wire format.
- **Pagination math** — offset / pages / `has_next`, and the keyset predicate structure.
- **Filtering** — the 20 operators, flat AND/OR, and nested groups (`FilterSpec`,
  `FilterGroup`, `FilterOp`).
- **Sorting** — stable multi-key with null placement (`SortSpec`, `SortDirection`,
  `NullsPosition`).
- **Search** — token matching and ranked trigram fuzzy scoring (`SearchSpec`,
  `TrigramIndex`, `FuzzyMode`).
- **Text normalization** — `normalize_text`, shared by search and matching.
- **The columnar fast path** — `Columns`, a dense typed projection that accelerates the
  filter and sort stages.

The public surface is **re-exported flat** from the crate root
(`paginate_core::FilterSpec`, never `paginate_core::filter::types::FilterSpec`), so the
module layout can change without breaking callers.

## Design in one sentence

The core speaks only **plain data** — a small JSON-like [`Value`](./design#the-value-model)
enum — has **zero binding dependencies**, and returns **indices** (never cloned rows),
so the exact same crate links natively into Python (PyO3) and Node/TypeScript
(napi-rs) and compiles unchanged to WebAssembly. See [design](./design).

## When to use it directly

- You're building a **Rust service** and want pagination / filtering / sorting / search
  with the same semantics (and cursor format) as your Python or TypeScript services.
- You're writing **another language binding** — wrap this crate rather than
  re-implementing the engine, and inherit [parity](../general/parity) for free.

If you're in Python or TypeScript, you don't depend on this crate directly — you
install the [`pypaginate`](../python/installation) or
[`@cyblow/paginate`](../typescript/installation) package, which bundles it.

## Status

`paginate-core` is published on crates.io and documented on docs.rs. It is
`#![forbid(unsafe_code)]`, carries `#![warn(missing_docs)]`, and is verified against the
Python codec with byte-identical golden vectors plus property tests — see
[design → parity](./design#how-parity-is-verified).

## Next

- [Using the core](./usage) — the `Value` model, feature flags, and a cursor example.
- [Design](./design) — fat core / thin adapters, in depth.
- [Performance](./performance) — where the native boundary pays off (measured).
