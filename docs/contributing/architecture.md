# Architecture Guide

How pypaginate is structured and why.

---

## Hexagonal Architecture

pypaginate follows a **hexagonal (ports and adapters)** architecture. The core
domain defines protocols (ports), and adapters implement them for specific
backends (SQLAlchemy, FastAPI, in-memory).

```
                    ┌──────────────────────────┐
                    │    FastAPI Adapters       │
                    │  OffsetDep, FilterDep,    │
                    │  SortDep, SearchDep       │
                    └────────────┬─────────────┘
                                 │
┌───────────────┐    ┌───────────┴───────────┐    ┌──────────────────┐
│  SA Adapters  │    │      Engine Layer      │    │  Memory Adapters │
│  Backend,     ├───►│  Paginator, Pipeline,  │◄───┤  MemoryBackend,  │
│  Filter,      │    │  CursorPaginator       │    │  FilterEngine,   │
│  Sort, Search │    └───────────┬───────────┘    │  SortEngine      │
└───────────────┘                │                 └──────────────────┘
                     ┌───────────┴───────────┐
                     │     Domain Layer       │
                     │  Specs, Params, Pages, │
                     │  Protocols, Enums,     │
                     │  Exceptions            │
                     └────────────────────────┘
```

---

## Directory Structure

```
src/pypaginate/
├── __init__.py          # Public API (exports paginate, pages, params, specs)
├── _dispatch.py         # Universal paginate() -- type overloads + auto-detection
│
├── domain/              # Pure domain -- Pydantic models + protocols
│   ├── enums.py         # SortDirection, FilterLogic, FuzzyMode, SearchFieldMode, etc.
│   ├── exceptions.py    # PaginationError hierarchy
│   ├── pages.py         # OffsetPage, CursorPage (result types)
│   ├── fast_pages.py    # msgspec.Struct pages (optional acceleration)
│   ├── params.py        # OffsetParams, CursorParams (input types)
│   ├── protocols.py     # PaginationBackend, CursorBackend, FilterBackend, etc.
│   └── specs.py         # FilterSpec, SortSpec, SearchSpec, FilterGroup
│
├── engine/              # Core orchestration (backend-agnostic)
│   ├── paginator.py     # Paginator, AsyncPaginator (offset)
│   ├── pipeline.py      # SyncPipeline, AsyncPipeline (filter+sort+search+paginate)
│   └── cursor.py        # AsyncCursorPaginator (keyset)
│
├── filtering/           # In-memory filter engine (native delegator)
│   ├── accessor.py      # compile_accessor() -- field path resolution
│   └── engine.py        # FilterEngine -- thin delegator to the native _core engine
│
├── sorting/             # In-memory sort engine
│   └── engine.py        # SortEngine (stable multi-key)
│
├── search/              # In-memory search engine
│   ├── engine.py        # SearchEngine (token-based relevance)
│   ├── matching.py      # matches_field(), fuzzy_score()
│   └── parser.py        # TokenParser (shlex-based)
│
├── text/                # Text utilities
│   └── normalize.py     # normalize_text() -- LRU cached + ASCII fast path
│
└── adapters/            # Backend implementations
    ├── memory/          # In-memory (list, tuple) -- MemoryBackend
    ├── sqlalchemy/      # SQLAlchemy ORM (sync + async)
    │   ├── backend.py   # SQLAlchemyBackend, SyncSQLAlchemyBackend
    │   ├── cursor.py    # SQLAlchemyCursorBackend, SyncSQLAlchemyCursorBackend
    │   ├── filters.py   # SQLAlchemyFilterBackend
    │   ├── sorting.py   # SQLAlchemySortBackend
    │   ├── search.py    # SQLAlchemySearchBackend
    │   └── columns.py   # resolve_column() -- ORM column resolution
    └── fastapi/         # FastAPI dependency injection
        ├── dependencies.py  # OffsetDep, CursorDep
        ├── filters.py       # FilterDep, FilterField
        ├── sorting.py       # SortDep
        └── search.py        # SearchDep
```

---

## Layer Rules

| Layer | May Import | Must Not Import |
|---|---|---|
| **Domain** | pydantic only | Engine, Adapters, Text |
| **Engine** | Domain | Adapters |
| **Filtering/Sorting/Search** | Domain, Text | Adapters |
| **Adapters** | Domain, Filtering, Sorting, Search | Engine (uses protocols) |
| **Dispatch** | Domain, Engine, Adapters | -- |

These rules are enforced by `tests/architecture/test_imports.py`.

**Key principle:** The domain layer has **zero** external dependencies beyond
Pydantic. It defines protocols that adapters implement. The engine layer depends
only on domain abstractions, never on concrete adapters.

---

## Key Design Patterns

### Protocol-Based Backends (Dependency Inversion)

Backends implement protocols, not base classes. Any class with matching method
signatures satisfies the protocol -- no inheritance required.

```python
# domain/protocols.py -- the contract
class PaginationBackend(Protocol[T]):
    async def count(self, query: object) -> int: ...
    async def fetch(self, query: object, offset: int, limit: int) -> list[T]: ...

# adapters/sqlalchemy/backend.py -- one implementation
class SQLAlchemyBackend(Generic[ItemT]):
    async def count(self, query: object) -> int: ...
    async def fetch(self, query: object, offset: int, limit: int) -> list[ItemT]: ...
```

Six protocols are defined in `domain/protocols.py`:

| Protocol | Methods | Implementations |
|---|---|---|
| `PaginationBackend[T]` | `count`, `fetch` (async) | `SQLAlchemyBackend` |
| `SyncPaginationBackend[T]` | `count`, `fetch` (sync) | `SyncSQLAlchemyBackend`, `MemoryBackend` |
| `CursorBackend[T]` | `fetch_page` (async) | `SQLAlchemyCursorBackend` |
| `FilterBackend` | `apply_filters` | `SQLAlchemyFilterBackend` |
| `SortBackend` | `apply_sorting` | `SQLAlchemySortBackend` |
| `SearchBackend` | `apply_search` | `SQLAlchemySearchBackend` |

### Elysia-Style Type Inference

The `paginate()` function uses input type to determine output type:

```python
paginate(source, OffsetParams(...))            # -> OffsetPage[T]
paginate(source, CursorParams(...), backend=b) # -> CursorPage[T]
```

This is implemented via `@overload` signatures in `_dispatch.py`.

### Compile-Once, Apply-N (Strategy Pattern)

Specs are compiled into closures once, then applied to every item:

```python
accessor = compile_accessor("user.profile.email")  # O(1) -- splits once
for item in items:
    value = accessor(item)  # O(1) per call, no string split
```

### Optional Acceleration

Optional dependencies follow the try/except import pattern:

```python
try:
    from rapidfuzz import fuzz as _fuzz
    _HAS_RAPIDFUZZ = True
except ImportError:
    _HAS_RAPIDFUZZ = False
```

Used for: `rapidfuzz` (search), `msgspec` (page construction), `google-re2` (regex safety).

---

## Adding a New Feature

1. **Read** existing code in the target module
2. **Check** similar implementations for patterns to follow
3. **Keep** functions <=15 lines, files <=250 lines (code only)
4. **Add** `__slots__` to any new class with instance attributes
5. **Write** tests in the matching `tests/unit/` directory
6. **Run** all quality checks:
   ```bash
   uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest tests/ --ignore=tests/perf -q
   ```
