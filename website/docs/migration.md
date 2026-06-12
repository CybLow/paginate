---
sidebar_position: 8
title: Migration
---

# Migration guide

Upgrade notes between versions. Most upgrades need **no code change** — the spec /
param shapes and the public helpers are stable.

## → v0.4 — generated types, Pydantic-optional (Python)

The Python package (`pypaginate`) was rebuilt from scratch. Behaviour and the
public-API *shapes* are unchanged, but the **types are now dataclasses generated
from the Rust core** (not Pydantic), and **Pydantic is optional**.

- **Construct specs / params the same way** — `FilterSpec(field=…, operator=…,
  value=…)`, `OffsetParams(page=1, limit=20)`, `And(…)` / `Or(…)` are unchanged.
  Operators / directions / modes are plain strings (`"gte"`, `"desc"`, `"contains"`).
- **Pages are generic containers** — `OffsetPage[T]` / `CursorPage[T]` support
  `len()`, iteration, and indexing, and hold your rows untouched (no per-row coercion).
- **Removed: the Pydantic model APIs.** `.model_dump()` / `.model_validate()` on
  specs and pages are gone. Use the dataclass fields directly or `dataclasses.asdict(…)`.
- **Pydantic is no longer a core dependency.** In-memory / SQLAlchemy / Django users
  don't install it. Opt in for FastAPI: `pip install "pypaginate[fastapi]"` (the
  FastAPI adapter still uses Pydantic for request/response models + OpenAPI).

## → v0.3 — fat core, thin adapters

v0.3 moves **all** computation into the shared Rust core (`paginate-core`): the
cursor codec, offset math, page assembly, filter / sort / search, and the keyset
predicate now have a single implementation that the Python and TypeScript packages
wrap. The headline guarantee is [cross-language parity](./general/parity).

### Python (`pypaginate`)

Most code needs **no change**. Notable points:

- **New one-shot `filter` / `sort` / `search`** for in-memory lists, alongside
  `paginate` — see the [Python quickstart](./python/quickstart).
- **Invalid enum tokens now raise** instead of silently defaulting (canonical
  string↔enum parsing moved into the core): a misspelled operator / direction / mode
  raises `FilterError` / `SortError` / `SearchError`.
- **The native `_core` extension is mandatory** — no pure-Python fallback; install a
  wheel or build with a Rust toolchain (PyPy unsupported).
- **Fuzzy / token-sort search is now trigram-based** (pg_trgm model), not rapidfuzz —
  faster and length-normalized, but **scores/ranking differ** and the default
  `threshold` drops 75 → 30. Tune `threshold` for your data.
- **Removed (dev/internal only):** the `pypaginate` console-script CLI (use the repo's
  `just` recipes) and the internal `pypaginate.filtering` / `sorting` / `search` /
  `text.normalize` import paths (use the public `Dataset` / helpers).
- **New:** the **Django** adapter — `pip install "pypaginate[django]"`.

### TypeScript (`@cyblow/paginate`)

Completed to parity and split into modules. Breaking changes from the 0.1.x preview:

| Before | After |
| --- | --- |
| `filterIndices(items, [{ field, op, value }])` | `[{ field, operator, value }]` (`op` still accepted) |
| `searchIndices(items, query, fields, opts)` | `searchIndices(items, { query, fields, mode, fuzzy, … })` |
| `ds.page(1, 20, opts)` | `ds.page(new OffsetParams({ page: 1, limit: 20 }), opts)` |
| `ds.search(query, fields, opts)` | `ds.search({ query, fields, mode, … })` |

New surface: `OffsetParams` / `CursorParams`, `OffsetPage<T>` / `CursorPage<T>`,
`And()` / `Or()`, a top-level `paginate()`, the error hierarchy, and the `express` /
`prisma` / `drizzle` adapters. See the **API Reference** section (TypeScript, Python,
Rust) in the sidebar for the full surface.
