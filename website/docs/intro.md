---
slug: /
title: Overview
sidebar_position: 1
---

# paginate

Fast pagination, filtering, sorting, and search with **one Rust core** and **native
Python & TypeScript packages** that return byte-for-byte identical results.

## Packages

| Language | Package | Install |
|---|---|---|
| Python | `pypaginate` | `pip install pypaginate` |
| TypeScript / Node | `@cyblow/paginate` | `npm i @cyblow/paginate` |
| Rust | `paginate-core` | `cargo add paginate-core` ([docs.rs](https://docs.rs/paginate-core)) |

## Why

- **One implementation.** Filtering (20 operators + nested And/Or), stable multi-key
  sorting with null placement, ranked + fuzzy (trigram) search, the cursor codec, the
  keyset predicate, and pagination math all live once in the Rust core. The Python and
  TS packages are thin, typed adapters over it.
- **Cross-language parity.** A frozen golden fixture asserts the Rust, Python, and TS
  engines produce identical results and **byte-identical cursors**.
- **Typed & fast.** Native speed; full type hints (Python) and types (TS) — generated
  from one schema, so they can't drift.

## Next

- [Install](./getting-started/installation)
- [Quickstart](./getting-started/quickstart)
- [Architecture](./concepts/architecture)
