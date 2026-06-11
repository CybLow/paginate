---
sidebar_position: 1
title: Why paginate?
---

# Why paginate?

Pagination looks trivial until you do it well across a real stack. The same list of
records gets sliced into pages on the server, filtered and sorted from query
parameters, searched by a text box, and scrolled with a cursor on the client — and
the moment two services are written in different languages, the *rules* start to
drift. A filter that means one thing in Python means something subtly different in
TypeScript; a cursor minted by one service can't be read by another.

**paginate** solves that by implementing the whole thing **once**, in a Rust core,
and exposing it through thin native packages for each language.

## What it does

- **Pagination** — offset (page/limit) and keyset (cursor) models, with the page
  metadata derived for you.
- **Filtering** — 20 operators (`eq`, `gte`, `contains`, `between`, `in`, `regex`, …)
  with flat `AND`/`OR` lists and nested `And()` / `Or()` groups.
- **Sorting** — stable, multi-key, with per-key direction and null placement.
- **Search** — ranked full-text with token matching and trigram **fuzzy** scoring.
- **Integrations** — SQLAlchemy, Django, FastAPI (Python); Express, Prisma, Drizzle
  (TypeScript).

## What makes it different

- **One implementation, no drift.** Every operator, the sort comparator, the search
  ranker, and the cursor codec exist exactly once. The packages delegate; they never
  re-implement. See [architecture](./architecture).
- **Cross-language parity.** Python and TypeScript return the same filtered / sorted /
  ranked order and **byte-identical cursors**, pinned by a frozen golden fixture
  asserted in CI. See [parity](./parity).
- **Native, but honest about it.** The engine is Rust, shipped inside the wheel / npm
  addon — no toolchain to install. It wins big on the [resident `Dataset`](./architecture)
  pipeline and the cursor codec; for one-shot in-memory ops over data your host
  already holds, the packages are typed, correct, and convenient rather than a raw
  speed play. The [benchmarks](../rust/performance) are candid about where the
  boundary pays off.
- **Typed end to end.** The spec / param / page shapes are generated from a single
  JSON Schema emitted by the core, so the Python dataclasses and TypeScript
  interfaces can't disagree with each other or with Rust.

## When to reach for it

- A **polyglot system** where a Python backend and a TypeScript frontend (or service)
  must agree on filters, sort order, and cursors.
- An API that needs **consistent, well-defined** filtering / sorting / search
  semantics without hand-rolling them per endpoint.
- An in-memory dataset served by many paginated requests — an **in-memory cache**, a
  config table, a search index — where a resident [`Dataset`](./architecture) amortizes
  the work.
- Anywhere you want **cursor pagination** that survives a switch of implementation
  language.

## When you might not need it

- A single-language app doing one trivial `LIMIT/OFFSET` query may not need a
  dedicated engine — though the framework integrations still save boilerplate.
- Hot, one-shot filtering/sorting of a list your host language already holds in
  memory is often fastest in the host's own array operations; reach for `paginate`
  there for *consistency*, and for the fused [`Dataset`](./architecture) pipeline when
  you query the same data repeatedly.

## Next

- [Choosing a package](./choosing-a-package) for your stack.
- [Architecture](./architecture) — how the core and adapters fit together.
