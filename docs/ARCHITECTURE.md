# pypaginate Architecture

> **v0.2.0** — Layered architecture with DDD + Hexagonal (Ports & Adapters)

---

## Overview

pypaginate uses a **layered architecture** inspired by Domain-Driven Design and Hexagonal Architecture. Dependencies flow inward — adapters depend on engines, engines depend on domain, domain depends on nothing.

```
┌───────────────────────────────────────────────────────────┐
│                    USER APPLICATION                       │
│                                                           │
│   from pypaginate import paginate, OffsetParams           │
│   page = paginate(users, OffsetParams(page=1, limit=20)) │
└─────────────────────┬─────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────────────────┐
│                    PUBLIC API                             │
│                 _dispatch.py                              │
│                                                           │
│   • Universal paginate() entry point                      │
│   • Auto-detects sync/async backend                       │
│   • Input type → output type (Elysia-style inference)     │
│     OffsetParams → OffsetPage                             │
│     CursorParams → CursorPage                             │
└─────────────────────┬─────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────────────────┐
│                   ENGINE LAYER                            │
│               engine/*.py                                 │
│                                                           │
│   • Paginator / AsyncPaginator — count → clamp → fetch    │
│   • SyncPipeline / AsyncPipeline — filter → sort → search │
│   • AsyncCursorPaginator — keyset pagination              │
│   • Backend-agnostic orchestration via protocols           │
└─────────────────────┬─────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐
│  FILTERING   │ │ SORTING  │ │ SEARCH   │
│ filtering/   │ │sorting/  │ │search/   │
│              │ │          │ │          │
│ • Engine     │ │ • Engine │ │ • Engine │
│ • Accessor   │ │          │ │ • Match  │
│ (→ _core)    │ │ (→_core) │ │ • Parser │
│              │ │          │ │ (pure)   │
│              │ │          │ │          │
└──────┬───────┘ └────┬─────┘ └────┬─────┘
       │              │            │
       └──────────────┼────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────────────────┐
│                   DOMAIN LAYER                            │
│                 domain/*.py                                │
│                                                           │
│   • Specs: FilterSpec, SortSpec, SearchSpec (Pydantic)     │
│   • Models: OffsetPage, CursorPage, OffsetParams           │
│   • Enums: SortDirection, FilterLogic, FuzzyMode, etc.     │
│   • Protocols: PaginationBackend, FilterBackend, etc.      │
│   • Exceptions: PaginationError hierarchy                  │
│   • NO external dependencies (except Pydantic)             │
└───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────────────────┐
│                  ADAPTERS LAYER                           │
│               adapters/{backend}/                         │
│                                                           │
│   memory/     — In-memory sequences (list, tuple)         │
│   sqlalchemy/ — SQLAlchemy ORM (sync + async)             │
│   fastapi/    — FastAPI dependency injection               │
│                                                           │
│   Each adapter implements domain Protocols                │
└───────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
src/pypaginate/
├── __init__.py              # Public API (23 exports)
├── _dispatch.py             # Universal paginate() with type overloads
├── _native.py               # Bridge: domain specs → _core tuples + index select
├── _core.pyi                # Type stubs for the bundled Rust extension
├── _core*.so                # Compiled Rust engine (maturin builds it from ../../rust/)
│
├── domain/                  # Pure domain — no external deps except Pydantic
│   ├── enums.py             # SortDirection, FilterLogic, FuzzyMode, etc.
│   ├── exceptions.py        # PaginationError hierarchy (8 classes)
│   ├── models.py            # Re-export hub for params + pages
│   ├── pages.py             # OffsetPage, CursorPage (Pydantic models)
│   ├── fast_pages.py        # FastOffsetPage, FastCursorPage (msgspec.Struct)
│   ├── params.py            # OffsetParams, CursorParams
│   ├── protocols.py         # PaginationBackend, FilterBackend, etc.
│   └── specs.py             # FilterSpec, SortSpec, SearchSpec
│
├── engine/                  # Core orchestration — backend-agnostic
│   ├── paginator.py         # Paginator, AsyncPaginator
│   ├── pipeline.py          # SyncPipeline, AsyncPipeline
│   └── cursor.py            # AsyncCursorPaginator
│
├── filtering/               # Filter adapter (delegates to _core)
│   ├── accessor.py          # compile_accessor() — field path resolution (search)
│   └── engine.py            # FilterEngine — flat specs + nested groups via _core
│
├── sorting/                 # Sort adapter (delegates to _core)
│   └── engine.py            # SortEngine — multi-key sort via _core
│
├── search/                  # Search engine (pure-Python fuzzy island, core #10)
│   ├── engine.py            # SearchEngine (token-based relevance scoring)
│   ├── matching.py          # matches_field(), fuzzy_score() (pre-normalized)
│   └── parser.py            # TokenParser (shlex-based)
│
├── text/                    # Text utilities
│   └── normalize.py         # normalize_text() with LRU cache + ASCII fast path
│
└── adapters/                # Backend implementations
    ├── memory/              # In-memory sequences
    │   ├── backend.py       # MemoryBackend (count=len, fetch=slice)
    │   ├── filters.py       # MemoryFilterBackend (compiled predicates)
    │   ├── sorting.py       # MemorySortBackend (partition-sort)
    │   └── search.py        # MemorySearchBackend (normalize + match)
    │
    ├── sqlalchemy/          # SQLAlchemy ORM
    │   ├── backend.py       # SQLAlchemyBackend (async), SyncSQLAlchemyBackend
    │   ├── filters.py       # SQLAlchemyFilterBackend (WHERE clauses)
    │   ├── sorting.py       # SQLAlchemySortBackend (ORDER BY)
    │   ├── search.py        # SQLAlchemySearchBackend (LIKE/ILIKE)
    │   ├── cursor.py        # Keyset pagination cursor encoding
    │   ├── columns.py       # Column resolution for ORM models
    │   └── types.py         # SQLAlchemy type mapping
    │
    └── fastapi/             # FastAPI integration
        ├── dependencies.py  # OffsetDep, CursorDep (Annotated dependencies)
        ├── filters.py       # FilterDep, FilterField (declarative filters)
        ├── sorting.py       # SortDep (sort parsing)
        └── search.py        # SearchDep (search parsing)
```

---

## Design Principles

### 1. Input Type → Output Type (Elysia-style)

```python
paginate(users, OffsetParams(...))  # → OffsetPage (sync)
paginate(query, OffsetParams(...), backend=sa_backend)  # → Awaitable[OffsetPage] (async)
paginate(query, CursorParams(...), backend=cursor_backend)  # → Awaitable[CursorPage]
```

The return type is inferred from the params type. No mode flags, no string arguments.

### 2. Protocol-Based Backends

All backends implement protocols from `domain/protocols.py`:

```python
class PaginationBackend(Protocol[T]):
    async def count(self, query: object) -> int: ...
    async def fetch(self, query: object, offset: int, limit: int) -> list[T]: ...

class FilterBackend(Protocol):
    def apply_filters(self, query: object, filters: Sequence[FilterSpec]) -> object: ...

class SortBackend(Protocol):
    def apply_sorting(self, query: object, sorting: Sequence[SortSpec]) -> object: ...

class SearchBackend(Protocol):
    def apply_search(self, query: object, spec: SearchSpec) -> object: ...
```

### 3. Compile-Once, Apply-N Strategy

All specs (filter, sort, search) are **static for a given query**. The engines compile them into fast callables ONCE, then apply N times:

- `compile_accessor("user.name")` — splits path once, returns reusable closure
- `_compile_predicate(FilterSpec)` — resolves operator + accessor + value once
- `classify_like("%value%")` — classifies pattern once at compile time
- `normalize_text(token)` — cached via `@lru_cache(8192)`

### 4. Separate Sync and Async

No scattered `if async:` conditionals. Completely separate code paths:

- `Paginator` (sync) and `AsyncPaginator` (async)
- `SyncPipeline` and `AsyncPipeline`
- `SyncSQLAlchemyBackend` and `SQLAlchemyBackend`

Detection happens exactly once in `_dispatch.py`.

### 5. `__slots__` on All Stateful Classes

Every class with instance attributes uses `__slots__`. Prevents `__dict__` allocation, faster attribute access:

```python
class FilterEngine:
    __slots__ = ("_registry",)
```

### 6. Optional Acceleration

Performance-critical optional dependencies:

| Extra | Package | Purpose |
|---|---|---|
| `pypaginate[fast]` | `msgspec>=0.18.0` | Near-zero page construction via msgspec.Struct |
| `pypaginate[search]` | `rapidfuzz>=3.0.0` | Fast fuzzy string matching |
| `pypaginate[security]` | `google-re2>=1.0` | ReDoS-safe regex filtering |

---

## Native Rust Core (`_core`)

pypaginate bundles a compiled Rust extension, **`pypaginate._core`** (PyO3,
`abi3-py311`, built with maturin), that shares its engine crate
(`paginate-core`) with the JS/TS port. **One engine, three languages** — cursor
encoding, filtering, sorting and exact/ranked search behave *identically*
across Python, Node and the browser, from a single implementation.

`_core` is the **single in-memory engine**: all filtering (flat specs *and*
nested `And`/`Or`/`FilterGroup` trees), all sorting, the cursor codec, and
exact/ranked search run through it. The adapters — `FilterEngine`,
`MemoryFilterBackend`, `SortEngine`, `MemorySortBackend` — are thin: they
translate domain specs to the engine's tuple form, call it, and select rows by
the returned indices (all via `_native.py`, which also normalizes the engine's
`KeyError`/`ValueError` into `FilterError`/`SortError`). The **only** execution
still in pure-Python is fuzzy / token-sort search, pending rapidfuzz parity in
the core (task #10).

### Build for speed (release, not debug)

The numbers below depend entirely on an optimized build. A debug build
(`maturin develop`) is roughly **10× slower**; build and ship with **release**
(LTO + `codegen-units = 1` + `opt-level = 3`, already set in `Cargo.toml`):
`maturin develop --release` locally, and the wheel CI builds release by default.

### Measured: the resident `Dataset` is the fast path

Filter-then-sort, median over 200 runs, **release** build (Apple Silicon,
CPython 3.11):

| N | pure-Python (former) | per-stage one-shot | resident `Dataset` |
|---:|---:|---:|---:|
| 100 | 14 µs | 31 µs | **2.1 µs — 6.5× faster** |
| 1,000 | 190 µs | 236 µs | **9.7 µs — 19.6× faster** |
| 10,000 | 1.45 ms | 2.0 ms | **53 µs — 27× faster** |
| 100,000 | 14.6 ms | 34 ms | **576 µs — 25× faster** |

The **resident `pypaginate.Dataset`** marshals a sequence into Rust *once*, then
answers repeated `filter → sort → paginate` queries by index — 6.5–27× faster
than the former pure-Python path, and the recommended way to paginate an
in-memory collection you query more than once. A single per-stage one-shot call
re-marshals the whole sequence each time, so it roughly *ties* pure-Python at
realistic sizes (tens of µs); that per-call marshalling is exactly what the
resident `Dataset` amortizes away. Equivalence between the resident pipeline and
the per-stage path is property-tested in `tests/property/test_dataset_parity.py`.

---

## Data Flow

### Paginate (simplest)

```
paginate(users, OffsetParams(page=2, limit=20))
  → _dispatch.py: detect backend type (Sequence → MemoryBackend)
    → Paginator.paginate(users, params)
      → backend.count(users) → len(users) → 100
      → backend.fetch(users, offset=20, limit=20) → users[20:40]
      → OffsetPage.create(items, total=100, params)
        → FastOffsetPage(...) if msgspec installed
        → OffsetPage(...) if not
```

### Full Pipeline

```
pipeline.execute(data, params, filters=[...], sorting=[...], search=SearchSpec(...))
  → _apply_specs(data, filters, sorting, search, backends...)
    → filter_backend.apply_filters(data, filters) → filtered list
    → sort_backend.apply_sorting(filtered, sorting) → sorted list
    → search_backend.apply_search(sorted, spec) → searched list
  → paginator.paginate(searched, params) → OffsetPage
```

---

## Exception Hierarchy

```
PaginationError (base)
├── ValidationError        # Invalid params
├── ConfigurationError     # Misconfigured backend
├── FilterError            # Field resolution / operator failure
│   └── FilterValidationError  # Invalid filter spec
├── SortError              # Sort failure
├── SearchError            # Search failure
│   └── SearchQueryError   # Invalid search query
```

---

## Adding a New Backend

1. Create `adapters/myorm/backend.py`
2. Implement `PaginationBackend[T]` (or `SyncPaginationBackend[T]`)
3. Optionally implement `FilterBackend`, `SortBackend`, `SearchBackend`
4. Register in `_dispatch.py` if auto-detection is needed
5. Add tests in `tests/unit/adapters/myorm/`

```python
class MyORMBackend:
    __slots__ = ("_session",)

    def __init__(self, session: MySession) -> None:
        self._session = session

    async def count(self, query: object) -> int:
        return await self._session.count(query)

    async def fetch(self, query: object, offset: int, limit: int) -> list:
        return await self._session.fetch(query, offset, limit)
```

---

## Metrics

| Metric | Value |
|---|---|
| Source files | 55 |
| Source lines | ~4,975 |
| Test files | 116 |
| Test lines | ~15,726 |
| Tests (non-perf) | 837 |
| Benchmark functions | ~388 |
| Core dependency | Pydantic only |
| Optional extras | 5 (sqlalchemy, search, fastapi, fast, security) |
