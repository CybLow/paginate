---
sidebar_position: 2.5
title: How it compares
description: How paginate differs from focused alternatives like fastapi-pagination, fastapi-filter, and sqlalchemy-pagination — a unified API, a shared Rust core, and cross-language parity.
---

# How it compares

The Python ecosystem has several good, focused pagination and filtering libraries. This
page is an honest map of where **paginate** sits relative to them — not a takedown. If
you only need one of these capabilities in one language, a focused tool may be the
simpler choice; paginate's value is **unifying** them and making them **identical across
languages**.

## What's distinctive about paginate

1. **One unified API for pagination + filtering + sorting + search.** Most tools do one
   of these; paginate does all four through the same specs and the same engine.
2. **Cross-language parity.** The Python and TypeScript packages share a Rust core, so
   they return identical results and **byte-identical cursors** — a Python service and a
   TypeScript client can share one keyset scheme. No other library in this space spans
   languages. See [parity](./parity) and the [polyglot recipe](../recipes/polyglot-cursors).
3. **Typed specs from one schema.** Filter/sort/search/param shapes are generated from a
   single JSON Schema, so Python and TypeScript can't drift.
4. **Both offset and keyset (cursor)**, with the cursor a portable, typed wire format.

## Feature comparison

A high-level map (capabilities evolve — check each project for current details):

| | **paginate** | fastapi-pagination | fastapi-filter | sqlalchemy-pagination |
|---|:--:|:--:|:--:|:--:|
| Offset pagination | ✅ | ✅ | — | ✅ |
| Keyset / cursor pagination | ✅ | ✅ | — | — |
| Filtering (operators + groups) | ✅ (20 ops, And/Or) | — | ✅ | — |
| Sorting (multi-key, nulls) | ✅ | — | ✅ (ordering) | — |
| Ranked / fuzzy search | ✅ (trigram) | — | — | — |
| In-memory **and** DB | ✅ | DB-focused | DB-focused | DB-focused |
| Framework adapters | FastAPI, SQLAlchemy, Django | FastAPI (many backends) | FastAPI + SQLAlchemy/Mongo | SQLAlchemy |
| **TypeScript / Node** | ✅ (`@cyblow/paginate`) | — | — | — |
| **Cross-language parity** | ✅ | — | — | — |
| Native (Rust) engine | ✅ | — | — | — |

## When a focused tool is the better fit

- You're **Python-only**, want **just** request-param pagination for FastAPI with broad
  backend support, and don't need filtering/search in the same package →
  **fastapi-pagination** is excellent at exactly that.
- You want **just** declarative filtering/ordering from query params for FastAPI →
  **fastapi-filter** is purpose-built.
- You want a **minimal** offset helper for SQLAlchemy → **sqlalchemy-pagination** or a
  plain `LIMIT/OFFSET` is hard to beat for simplicity.

## When paginate is the better fit

- You run a **polyglot stack** and need a Python service and a TypeScript client/service
  to agree on filters, sort order, and **cursors**.
- You want **one** consistent vocabulary for pagination, filtering, sorting, and search
  across endpoints (and across in-memory and database data).
- You want the spec shapes **typed and generated**, so they can't drift between
  services or languages.

:::note On raw speed
paginate's value is consistency, not a blanket speed claim — for a single in-memory
filter/sort over data your host already holds, your language's own array operations are
often faster. The native win is the cursor codec and the resident
[`Dataset`](../python/pagination#the-resident-dataset) pipeline. See
[performance](../rust/performance) for the measured trade-offs.
:::
