---
slug: /
title: Overview
sidebar_position: 1
description: Fast pagination, filtering, sorting, and search with one Rust core and native Python & TypeScript packages that return byte-for-byte identical results.
---

# paginate

Fast pagination, filtering, sorting, and search with **one Rust core** and **native
Python & TypeScript packages** that return byte-for-byte identical results.

## Packages

| Language | Package | Install | Reference |
|---|---|---|---|
| Python | [`pypaginate`](https://pypi.org/project/pypaginate/) | `pip install pypaginate` | [Python guide](./python/installation) |
| TypeScript / Node | [`@cyblow/paginate`](https://www.npmjs.com/package/@cyblow/paginate) | `npm i @cyblow/paginate` | [TypeScript guide](./typescript/installation) |
| Rust | [`paginate-core`](https://crates.io/crates/paginate-core) | `cargo add paginate-core` | [Rust core](./rust/overview) · [docs.rs](https://docs.rs/paginate-core) |

## Choose your path

- 🐍 **[Python](./python/installation)** — `paginate()`, one-shot `filter`/`sort`/`search`,
  the resident `Dataset`, and SQLAlchemy / Django / FastAPI integrations.
- 🟦 **[JavaScript / TypeScript](./typescript/installation)** — the same surface, plus
  Express / Prisma / Drizzle adapters and the portable cursor codec.
- 🦀 **[Rust core](./rust/overview)** — embed the engine directly, or read how it works.

## Core ideas

These apply to every language — read them once:

- **[Why paginate?](./general/why)** — what problem it solves and when to reach for it.
- **[Choosing a package](./general/choosing-a-package)** — which install fits your stack.
- **[Architecture](./general/architecture)** — the fat-core / thin-adapter design.
- **[Cross-language parity](./general/parity)** — why results and cursors match exactly.
- **[Pagination models](./general/pagination-models)** — offset vs. keyset (cursor).

## Shared reference

The spec vocabulary is defined once in the core and is identical in every language:

- **[Filtering & operators](./general/filtering)** — the 20 operators and boolean groups.
- **[Sorting semantics](./general/sorting)** — stability, direction, and null placement.
- **[Search & ranking](./general/search)** — match modes, trigram fuzzy scoring, weights.

## Recipes & help

- 🍳 **[Sharing cursors across Python & TypeScript](./recipes/polyglot-cursors)** — the headline feature, end to end.
- 🍳 **[Building a paginated API](./recipes/paginated-api)** — query params → filtered, sorted page.
- ❓ **[FAQ](./general/faq)** · 📖 **[Glossary](./general/glossary)** — common questions and the vocabulary.
