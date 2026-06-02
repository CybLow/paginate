# Architecture

pypaginate v0.2 uses a **hexagonal architecture** (ports and adapters) with three layers:
the domain layer (pure types), the engine layer (orchestration), and the adapter layer
(backend implementations).

---

## Layer Overview

```{mermaid}
graph TB
    subgraph "Domain Layer (zero deps except Pydantic)"
        Specs["specs.py — FilterSpec, SortSpec, SearchSpec, And, Or"]
        Params["params.py — OffsetParams, CursorParams"]
        Pages["pages.py — OffsetPage, CursorPage"]
        Protocols["protocols.py — PaginationBackend, FilterBackend, ..."]
        Enums["enums.py — SortDirection, FuzzyMode, FilterLogic, ..."]
        Exceptions["exceptions.py — PaginationError hierarchy"]
    end

    subgraph "Engine Layer (orchestration)"
        Dispatch["_dispatch.py — paginate() universal entry point"]
        Paginator["paginator.py — Paginator, AsyncPaginator"]
        CursorPag["cursor.py — AsyncCursorPaginator"]
        Pipeline["pipeline.py — SyncPipeline, AsyncPipeline"]
        FilterEng["filtering/engine.py — FilterEngine"]
        SearchEng["search/engine.py — SearchEngine"]
        SortEng["sorting/engine.py — SortEngine"]
    end

    subgraph "Adapter Layer (backend implementations)"
        MemAdapt["adapters/memory/ — MemoryBackend, MemoryFilterBackend, ..."]
        SAAdapt["adapters/sqlalchemy/ — SQLAlchemyBackend, SQLAlchemyFilterBackend, ..."]
        FAAdapt["adapters/fastapi/ — OffsetDep, CursorDep, FilterDep, SortDep, SearchDep"]
    end

    Dispatch --> Paginator
    Dispatch --> CursorPag
    Pipeline --> Paginator
    Pipeline --> FilterEng
    Pipeline --> SearchEng
    Paginator --> Protocols
    CursorPag --> Protocols
    MemAdapt -.->|implements| Protocols
    SAAdapt -.->|implements| Protocols
    FAAdapt --> Params
```

**Rules:**

1. Domain has **no external dependencies** except Pydantic (for model validation).
2. Engine depends only on domain.
3. Adapters implement domain protocols and may depend on external libraries (SQLAlchemy, FastAPI).
4. Dependencies always point **inward** (adapters -> engine -> domain).

---

## Module Structure

```
src/pypaginate/
├── __init__.py              # Public API: paginate, OffsetParams, CursorParams, ...
├── _dispatch.py             # paginate() — universal entry point with type overloads
├── _detection.py            # Backend auto-detection helpers
├── py.typed                 # PEP 561 marker
│
├── domain/                  # Pure types, zero external deps (except Pydantic)
│   ├── enums.py             # SortDirection, FuzzyMode, FilterLogic, ...
│   ├── exceptions.py        # PaginationError, FilterError, SearchError, ...
│   ├── fast_pages.py        # FastOffsetPage, FastCursorPage (msgspec structs)
│   ├── pages.py             # OffsetPage, CursorPage (Pydantic models)
│   ├── params.py            # OffsetParams, CursorParams, MAX_LIMIT
│   ├── protocols.py         # PaginationBackend, CursorBackend, FilterBackend, ...
│   └── specs.py             # FilterSpec, SortSpec, SearchSpec, And, Or, FilterGroup
│
├── engine/                  # Orchestration
│   ├── paginator.py         # Paginator (sync), AsyncPaginator (async)
│   ├── cursor.py            # AsyncCursorPaginator
│   └── pipeline.py          # SyncPipeline, AsyncPipeline (filter→sort→search→paginate)
│
├── filtering/               # In-memory filter engine (native delegator)
│   ├── engine.py            # FilterEngine — thin delegator to the native _core engine
│   └── accessor.py          # compile_accessor — nested field path resolution
│
├── search/                  # In-memory search engine (native delegator)
│   └── engine.py            # SearchEngine — thin delegator to the native _core engine
│
├── sorting/                 # In-memory sort support
│   └── engine.py            # SortEngine — multi-key stable sorting
│
├── text/                    # Text processing utilities
│   └── normalize.py         # Unicode normalization, accent removal
│
└── adapters/                # Backend implementations
    ├── memory/              # In-memory backends
    │   ├── backend.py       # MemoryBackend (PaginationBackend)
    │   ├── filters.py       # MemoryFilterBackend (FilterBackend)
    │   ├── search.py        # MemorySearchBackend (SearchBackend)
    │   └── sorting.py       # MemorySortBackend (SortBackend)
    │
    ├── sqlalchemy/          # SQLAlchemy backends
    │   ├── backend.py       # SQLAlchemyBackend, SyncSQLAlchemyBackend
    │   ├── cursor.py        # SQLAlchemyCursorBackend (built-in keyset)
    │   ├── filters.py       # SQLAlchemyFilterBackend
    │   ├── search.py        # SQLAlchemySearchBackend
    │   ├── sorting.py       # SQLAlchemySortBackend
    │   ├── columns.py       # Column resolution helpers
    │   └── types.py         # SQLAlchemy type aliases
    │
    └── fastapi/             # FastAPI integration
        ├── dependencies.py  # OffsetDep, CursorDep (Annotated types)
        ├── filters.py       # FilterDep, FilterField
        ├── sorting.py       # SortDep
        └── search.py        # SearchDep
```

---

## Protocols (Ports)

The domain layer defines six protocols that backends must satisfy. All are `@runtime_checkable`.

```python
from pypaginate.domain.protocols import (
    PaginationBackend,      # async count + fetch (offset mode)
    SyncPaginationBackend,  # sync count + fetch (offset mode)
    CursorBackend,          # async fetch_page (cursor mode)
    FilterBackend,          # apply_filters(query, specs)
    SortBackend,            # apply_sorting(query, specs)
    SearchBackend,          # apply_search(query, spec)
)
```

| Protocol | Methods | Used By |
|----------|---------|---------|
| `PaginationBackend[T]` | `count(query)`, `fetch(query, offset, limit)` | `AsyncPaginator` |
| `SyncPaginationBackend[T]` | `count(query)`, `fetch(query, offset, limit)` | `Paginator` |
| `CursorBackend[T]` | `fetch_page(query, *, limit, after, before)` | `AsyncCursorPaginator` |
| `FilterBackend` | `apply_filters(query, filters)` | `Pipeline` |
| `SortBackend` | `apply_sorting(query, sorting)` | `Pipeline` |
| `SearchBackend` | `apply_search(query, spec)` | `Pipeline` |

---

## The `paginate()` Function

The universal entry point uses **Elysia-style type inference**: the params type
determines the return type.

```python
from pypaginate import paginate, OffsetParams, CursorParams

# OffsetParams → OffsetPage (sync for lists, async for SA)
page = paginate(users_list, OffsetParams(page=1, limit=20))

# CursorParams → Awaitable[CursorPage] (always async)
page = await paginate(query, CursorParams(after="abc"), backend=backend)
```

Detection logic:

1. **List + OffsetParams + no backend** -- fast path: slice the list directly, no backend allocation.
2. **OffsetParams + async backend** -- returns `Awaitable[OffsetPage]`.
3. **OffsetParams + sync backend** -- returns `OffsetPage`.
4. **CursorParams** -- requires an async `CursorBackend`, returns `Awaitable[CursorPage]`.

---

## Pipeline Composition

The `SyncPipeline` and `AsyncPipeline` compose filter, sort, search, and pagination
into a single call:

```{mermaid}
graph LR
    Q["query"] --> F["FilterBackend.apply_filters"]
    F --> S["SortBackend.apply_sorting"]
    S --> SR["SearchBackend.apply_search"]
    SR --> P["Paginator.paginate"]
    P --> R["OffsetPage"]
```

```python
from pypaginate.engine.pipeline import AsyncPipeline
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend, SQLAlchemyFilterBackend,
    SQLAlchemySortBackend, SQLAlchemySearchBackend,
)

backend = SQLAlchemyBackend(session)
pipeline = AsyncPipeline(
    AsyncPaginator(backend),
    filter_backend=SQLAlchemyFilterBackend(),
    sort_backend=SQLAlchemySortBackend(),
    search_backend=SQLAlchemySearchBackend(),
)

result = await pipeline.execute(
    select(User),
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="age", operator="gte", value=18)],
    sorting=[SortSpec(field="name")],
    search=SearchSpec(query="john", fields=("name", "email")),
)
```

---

## Page Types

Two separate page types with no null leakage:

| Field | `OffsetPage[T]` | `CursorPage[T]` |
|-------|-----------------|-----------------|
| `items` | `list[T]` | `list[T]` |
| `limit` | `int` | `int` |
| `has_next` | `bool` | `bool` |
| `has_previous` | `bool` | `bool` |
| `total` | `int` | -- |
| `page` | `int` | -- |
| `pages` | `int` | -- |
| `next_cursor` | -- | `str \| None` |
| `previous_cursor` | -- | `str \| None` |

When `pypaginate[fast]` is installed, page construction uses `msgspec.Struct` for
near-zero overhead. The returned object duck-types as a Pydantic model with
`.model_dump()` and `.to_pydantic()`.

---

## Exception Hierarchy

```{mermaid}
classDiagram
    class PaginationError
    class ConfigurationError {
        +details: dict
    }
    class ValidationError {
        +field: str | None
        +details: dict
    }
    class FilterError {
        +field: str | None
        +details: dict
    }
    class FilterValidationError
    class SearchError {
        +details: dict
    }
    class SearchQueryError
    class SortError {
        +details: dict
    }

    PaginationError <|-- ConfigurationError
    PaginationError <|-- ValidationError
    PaginationError <|-- FilterError
    FilterError <|-- FilterValidationError
    PaginationError <|-- SearchError
    SearchError <|-- SearchQueryError
    PaginationError <|-- SortError
```

All exceptions carry structured `details` dicts for programmatic handling.

---

## Design Patterns

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Ports & Adapters** | `domain/protocols.py` + `adapters/` | Backend-agnostic orchestration |
| **Strategy** | `PaginationBackend`, `FilterBackend`, `SortBackend`, `SearchBackend` | Swap backends without changing engine code |
| **Facade** | `paginate()` function | Single entry point hiding detection + dispatch |
| **Native core** | `_core` engine | The 20 filter operators are implemented in the bundled native engine |
| **Compile-once** | `FilterEngine`, `SearchEngine` | Compile specs to closures once, evaluate N times |
| **Type inference** | `paginate()` overloads | Input type determines output type (Elysia-style) |

---

## Extending pypaginate

To add a new backend (e.g., MongoDB):

```python
from pypaginate.domain.protocols import PaginationBackend

class MongoBackend:
    """Satisfies PaginationBackend[T] protocol."""

    def __init__(self, collection) -> None:
        self._collection = collection

    async def count(self, query: object) -> int:
        return await self._collection.count_documents(query)

    async def fetch(self, query: object, offset: int, limit: int) -> list:
        cursor = self._collection.find(query).skip(offset).limit(limit)
        return await cursor.to_list(length=limit)
```

Then use it with the standard `paginate()` function:

```python
from pypaginate import paginate, OffsetParams

page = await paginate(query_filter, OffsetParams(page=1), backend=MongoBackend(collection))
```

No registration needed -- the protocol is structural (duck typing).
