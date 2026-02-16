# Architecture

This page describes pypaginate's internal architecture — both what exists today (v0.1.0)
and the target architecture being built toward.

**Important:** Sections marked **[CURRENT]** describe what is implemented and working.
Sections marked **[PLANNED]** describe the target design for upcoming releases.

---

## Current Architecture (v0.1.0) {#current}

### High-Level Overview

```{mermaid}
graph TB
    subgraph "Public API"
        PA["paginate_entities()<br/>paginate_rows()"]
    end

    subgraph "Engines"
        SP[SqlPaginator]
        MP[MemoryPaginator]
        KP[KeysetPaginator]
    end

    subgraph "Filters"
        FE[FilterEngine<br/>JSON Logic]
        SA[SqlFilterAdapter]
        SE[Search Engines]
    end

    subgraph "Sorting"
        SO[SortEngine]
        SSA[SqlSortAdapter]
    end

    subgraph "Core"
        Page["Page[T]<br/>(frozen dataclass)"]
        PP[PageParams]
        KPP[KeysetPageParams]
    end

    PA --> SP
    PA --> MP
    PA --> KP

    SP --> Page
    MP --> Page
    KP --> Page

    FE -.->|"independent"| SA
    SE -.->|"independent"| SO

    SP --> PP
    KP --> KPP
```

**Current reality:** The public API, engines, and filters are functional but
**not integrated** into a single `paginate()` call. Users must compose them manually.

### Layer Overview [CURRENT]

| Layer | Purpose | Actual Classes |
|-------|---------|----------------|
| **Public API** | Async pagination functions | `paginate_entities()`, `paginate_rows()` |
| **Engines** | Pagination strategy | `SqlPaginator`, `MemoryPaginator`, `KeysetPaginator` |
| **Filters** | In-memory + SQL filtering | `FilterEngine`, `SqlFilterAdapter` |
| **Search** | Text search | `SqlSearchService`, `MemorySearchEngine` |
| **Sorting** | Multi-column sorting | `SortEngine`, `SqlSortAdapter` |
| **Core** | Data types | `Page[T]`, `PageParams`, `KeysetPageParams` |
| **Integration** | FastAPI adapter | `PagedResponse[T]`, `get_pagination_params()` |

### Core Types [CURRENT]

The core data types are **frozen dataclasses** (not Pydantic models — this changes
in v0.1.1):

```python
@dataclass(frozen=True, slots=True)
class PageParams:
    """Pagination parameters."""
    page: int = 1
    limit: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

@dataclass(frozen=True, slots=True)
class Page(Generic[ItemT]):
    """Generic paginated result container."""
    items: Sequence[ItemT]
    total: int
    page: int
    limit: int

    @property
    def pages(self) -> int: ...

    @property
    def has_next(self) -> bool: ...

    @property
    def has_previous(self) -> bool: ...

@dataclass(frozen=True, slots=True)
class KeysetPageParams:
    """Cursor-based pagination parameters."""
    limit: int = 20
    page: str | None = None
    after: str | None = None
    before: str | None = None
```

**Known issue:** `Page[T]` is a frozen dataclass, but FastAPI needs a Pydantic model
for `response_model`. This forces a separate `PagedResponse[T]` wrapper in
`integrations/fastapi.py`. This dual representation is eliminated in v0.1.1.

### Protocols [CURRENT]

Five protocols are defined in `types.py`:

```python
@runtime_checkable
class PageParamsProtocol(Protocol):
    page: int
    limit: int
    @property
    def offset(self) -> int: ...
    def model_copy(
        self,
        *,
        update: Mapping[str, int] | None = None,
        deep: bool = False,
    ) -> PageParamsProtocol: ...

@runtime_checkable
class PageProtocol(Protocol):
    items: Sequence[object]
    total: int
    page: int
    limit: int

@runtime_checkable
class SupportsTotalOrdering(Protocol):
    def __lt__(self, _other: object) -> bool: ...
    def __le__(self, _other: object) -> bool: ...
    def __gt__(self, _other: object) -> bool: ...
    def __ge__(self, _other: object) -> bool: ...

@runtime_checkable
class SqlClause(Protocol):
    def __and__(self, other: SqlClause) -> SqlClause: ...
    def __or__(self, other: SqlClause) -> SqlClause: ...

@runtime_checkable
class SqlStringExpression(Protocol):
    def in_(self, values: Sequence[str]) -> SqlClause: ...
    def like(self, pattern: str, *, escape: str) -> SqlClause: ...
```

**What's missing:** No `PaginationBackend`, `FilterBackend`, or `SortBackend`
protocols exist yet. These are planned for v0.1.1 to enable multi-backend support.

### Pagination Engines [CURRENT]

```{mermaid}
classDiagram
    class SqlPaginator~ItemT~ {
        +__init__(session, *, clamp)
        +paginate(query, context, *, scalars) Page
        +paginate_keyset(session, stmt, params) Page
        -_fetch_page(session, stmt, offset, limit)
        -_count_total(session, stmt)
    }

    class MemoryPaginator {
        +paginate(items, params) Page
        +filter_iter(items, predicate) Iterator
    }

    class KeysetPaginator {
        +select_keyset_page(session, stmt, params) Page
    }
```

| Engine | Data Source | Strategy | Class |
|--------|-------------|----------|-------|
| `SqlPaginator` | SQLAlchemy | LIMIT/OFFSET or keyset | `engines/sql.py` |
| `MemoryPaginator` | Python collections | List slicing | `engines/memory.py` |
| `KeysetPaginator` | SQLAlchemy (via sqlakeyset) | WHERE + cursor | `engines/keyset.py` |

### Filter Engine [CURRENT]

The filter system has two independent subsystems:

**1. JSON Logic Predicate Engine** — in-memory filtering with 24 operators:

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()
results = engine.apply(items, {"age": {"gte": 18}})
```

Operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `notin`,
`between`, `range`, `contains`, `icontains`, `startswith`, `istartswith`,
`endswith`, `iendswith`, `like`, `ilike`, `regex`, `iregex`, `is_null`,
`is_not_null`, `empty`, `not_empty`

**2. SQL Filter Adapter** — generates SQLAlchemy WHERE clauses with 14 operators:

```python
from pypaginate.filters.sql_adapter import SqlFilterAdapter

condition = SqlFilterAdapter.build_condition(User.age, "gte", 18)
stmt = select(User).where(condition)
```

Operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `like`,
`ilike`, `is_null`, `contains`, `startswith`, `endswith` (plus 6 aliases)

### Search Engine [CURRENT]

```python
# SQL-based search
from pypaginate.filters.search import SqlSearchService
from pypaginate.filters.search.options import SearchOptions

service = SqlSearchService(
    search_fields=["name", "email"],
    options=SearchOptions(fuzzy=True, min_similarity=0.7),
)

# In-memory search
from pypaginate.filters.search import MemorySearchEngine

engine = MemorySearchEngine(fields=["name", "email"])
results = engine.search(items, "john")
```

### Sort Engine [CURRENT]

```python
from pypaginate.sorting.engine import SortEngine

engine = SortEngine()
sorted_items = engine.sort(
    items, sort_field="name", reverse=False,
    nulls_position="last", tie_breaker_field=None,
)
```

### Exception Hierarchy [CURRENT]

```{mermaid}
classDiagram
    class PaginatorException {
        +message: str
    }

    class PaginationConfigurationError {
        +field: str
        +value: Any
        +reason: str
    }

    class FilterException {
        +field: str
    }

    class FilterValidationError {
        +details: dict
    }

    class SearchException

    class SearchQueryError {
        +details: dict
    }

    class SearchNormalizationError {
        +details: dict
    }

    class SortException

    class ValidationException {
        +field: str
        +value: Any
        +reason: str
    }

    PaginatorException <|-- PaginationConfigurationError
    PaginatorException <|-- FilterException
    FilterException <|-- FilterValidationError
    PaginatorException <|-- SearchException
    SearchException <|-- SearchQueryError
    SearchException <|-- SearchNormalizationError
    PaginatorException <|-- SortException
    PaginatorException <|-- ValidationException
```

### Public API Exports [CURRENT]

The `__init__.py` exports 14 names:

```python
__all__ = [
    "FilterException",
    "KeysetPageParams",
    "Page",
    "PageParams",
    "PaginationConfigurationError",
    "PaginatorException",
    "SearchException",
    "SortException",
    "ValidationException",
    "__version__",
    "paginate_entities",
    "paginate_entities_to_page",
    "paginate_rows",
    "paginate_rows_to_page",
]
```

```{note}
Three additional exception classes (`FilterValidationError`, `SearchQueryError`,
`SearchNormalizationError`) are imported in `__init__.py` but **not** included in
`__all__`. They are accessible but not part of the documented public API.
This inconsistency will be resolved in v0.1.1.
```

### Data Flow [CURRENT]

```{mermaid}
sequenceDiagram
    participant Client as FastAPI Endpoint
    participant Params as get_pagination_params()
    participant Paginator as SqlPaginator
    participant DB as Database

    Client->>Params: Parse page & limit from query
    Params->>Client: PageParams

    Note over Client: User manually builds<br/>WHERE/ORDER BY

    Client->>Paginator: paginate(query, context, *, scalars)
    Paginator->>DB: SELECT COUNT(*)
    DB->>Paginator: total
    Paginator->>DB: SELECT ... LIMIT/OFFSET
    DB->>Paginator: rows
    Paginator->>Client: Page[T]

    Note over Client: Convert Page → PagedResponse<br/>(eliminated in v0.1.1)
```

### Module Structure [CURRENT]

```
pypaginate/
├── __init__.py             # Public API (14 exports)
├── types.py                # 5 Protocol definitions
├── exceptions.py           # 9 exception classes
├── _cli.py                 # CLI tool (untested)
├── core/
│   ├── pages.py            # Page, PageParams, KeysetPageParams (frozen dataclasses)
│   ├── context.py          # PaginationContext
│   └── snapshots.py        # PaginationSnapshot
├── engines/
│   ├── sql.py              # SqlPaginator (offset + keyset)
│   ├── memory.py           # MemoryPaginator
│   └── keyset.py           # Keyset helpers (via sqlakeyset)
├── filters/
│   ├── sql_adapter.py      # SqlFilterAdapter (14 operators)
│   ├── predicates/         # JSON Logic engine (24 operators)
│   │   ├── engine.py       # FilterEngine
│   │   ├── operators/      # Operator factories
│   │   ├── field_accessor.py
│   │   └── jsonlogic_evaluator.py
│   └── search/             # Search subsystem
│       ├── memory_search.py  # MemorySearchEngine
│       ├── sql_search.py     # SqlSearchService
│       ├── parser.py         # Query token parser
│       ├── options.py        # SearchOptions config
│       ├── helpers.py        # SQL clause helpers
│       ├── strategies.py     # Search strategies
│       ├── conditions.py     # Condition builders
│       ├── factories.py      # Service factories
│       └── fuzzy.py          # RapidFuzz integration
├── sorting/
│   ├── engine.py           # SortEngine
│   └── sql_adapter.py      # SqlSortAdapter
├── text/
│   ├── utf8.py             # UTF-8 normalization
│   └── patterns.py         # Regex utilities
├── database/
│   └── types.py            # SQLAlchemy type aliases
├── query/
│   ├── async_api.py        # paginate_entities(), paginate_rows()
│   ├── builders/           # Query builders (count)
│   └── execution/          # Async executor
└── integrations/
    └── fastapi.py          # PagedResponse, get_pagination_params
```

---

## Target Architecture (v0.2.0+) {#target}

The following describes the **planned** architecture. Nothing in this section exists
in the codebase yet.

### Unified paginate() API [PLANNED — v0.2.0]

```python
from pypaginate import paginate, Page, PageParams

# Single function that integrates pagination + filters + search + sort
page = await paginate(
    session,
    select(User),
    params=PageParams(page=1, limit=20),
    filters=user_filters,       # FilterModel instance
    ordering=ordering_params,   # OrderingParams instance
    search=search_term,         # Search string
)
```

### Backend Protocols [PLANNED — v0.1.1]

```python
class PaginationBackend(Protocol[T]):
    """Interface for pagination engines across ORMs."""
    async def count(self, query: Any) -> int: ...
    async def fetch(self, query: Any, offset: int, limit: int) -> list[T]: ...

class FilterBackend(Protocol):
    """Interface for filter application across ORMs."""
    def apply_filters(self, query: Any, filters: FilterValues) -> Any: ...

class SortBackend(Protocol):
    """Interface for sort application across ORMs."""
    def apply_sorting(self, query: Any, sorting: SortValues) -> Any: ...
```

SQLAlchemy becomes one adapter among many:

```{mermaid}
classDiagram
    class PaginationBackend {
        <<protocol>>
        +count(query) int
        +fetch(query, offset, limit) list
    }

    class SqlAlchemyBackend {
        +count(query) int
        +fetch(query, offset, limit) list
    }

    class TortoiseBackend {
        +count(query) int
        +fetch(query, offset, limit) list
    }

    class BeanieBackend {
        +count(query) int
        +fetch(query, offset, limit) list
    }

    PaginationBackend <|.. SqlAlchemyBackend
    PaginationBackend <|.. TortoiseBackend
    PaginationBackend <|.. BeanieBackend
```

### Page as Pydantic Model [PLANNED — v0.1.1]

```python
class Page(BaseModel, Generic[T]):
    """Paginated result — works directly as FastAPI response_model."""
    model_config = ConfigDict(frozen=True)

    items: list[T]
    total: int
    page: int
    limit: int

    @computed_field
    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.limit) if self.limit else 0

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
```

This eliminates the `PagedResponse` wrapper entirely.

### Declarative FastAPI Integration [PLANNED — v0.2.0]

```{mermaid}
graph TB
    subgraph "FastAPI Integration"
        FD[FilterDepends]
        OD[OrderingDepends]
        SD[SearchDepends]
    end

    subgraph "Models"
        FM[FilterModel]
        OP[OrderingParams]
    end

    subgraph "Backends"
        SQL[SQLAlchemy]
        TORT[Tortoise]
        BEAN[Beanie]
    end

    FD --> FM
    OD --> OP
    FM --> SQL
    FM --> TORT
    FM --> BEAN
    OP --> SQL
    OP --> TORT
    OP --> BEAN
```

### Multiple Pagination Formats [PLANNED — v0.3.0]

```{mermaid}
classDiagram
    class Page~T~ {
        +items: list[T]
        +total: int
        +page: int
        +limit: int
    }

    class LimitOffsetPage~T~ {
        +items: list[T]
        +total: int
        +limit: int
        +offset: int
    }

    class CursorPage~T~ {
        +items: list[T]
        +next_cursor: str
        +prev_cursor: str
        +has_next: bool
        +has_prev: bool
    }

    class PageWithLinks~T~ {
        +items: list[T]
        +total: int
        +links: Links
    }
```

### Configuration System [PLANNED — v0.3.0]

```python
from pypaginate import configure

configure(
    default_page_size=20,
    max_page_size=100,
    default_engine="offset",
    adapters={
        "sqlalchemy": SqlAlchemyBackend,
        "tortoise": TortoiseBackend,
    },
)
```

### Custom Operators [Extension Point — PLANNED]

```python
from pypaginate.filters.predicates.registry import OperatorRegistry

# Register custom operators
registry = OperatorRegistry()
registry.register(
    names=["near"],
    factory=GeolocationFactory(default_radius=1000),
)
```

### Custom Adapters [Extension Point — PLANNED]

```python
class MongoBackend:
    """Adapter for MongoDB collections."""

    async def count(self, query):
        return await query.count_documents({})

    async def fetch(self, query, offset, limit):
        return await query.skip(offset).limit(limit).to_list()
```

---

## Performance Considerations

### Engine Selection [CURRENT]

```{mermaid}
flowchart TD
    Q[Query Type?] --> SQL{SQLAlchemy?}
    SQL -->|Yes| Size{Dataset Size?}
    SQL -->|No| MEM[MemoryPaginator]

    Size -->|Large / deep pages| KS[KeysetPaginator]
    Size -->|Small-medium| OFF["SqlPaginator (offset)"]
```

### Lazy Evaluation [CURRENT]

```python
# Query is NOT executed yet
query = select(User).where(User.status == "active")

# Still not executed — just building SQL
filtered = query.where(User.age >= 18)

# NOW executed when paginate runs COUNT + SELECT
page = await paginate_entities(session, filtered, params)
```

### Connection Management [CURRENT]

```python
# Good: Uses connection pool via session
async with async_session() as session:
    page = await paginate_entities(session, query, params)

# Bad: No session context
page = await paginate_entities(None, query, params)  # Will fail
```

---

## Testing Architecture [CURRENT]

```{mermaid}
graph TB
    subgraph "Test Layers"
        Unit["Tests<br/>642 total (617 passed, 25 skipped)"]
        Integration["Integration Tests<br/>Component interaction"]
        E2E["E2E Tests<br/>Full request/response"]
    end

    subgraph "Test Fixtures"
        Mock[Mock Adapters]
        Mem[In-Memory DB]
        Real[Real Database]
    end

    Unit --> Mock
    Integration --> Mem
    E2E --> Real
```

**Test statistics:** 642 tests across 51 files (617 passed, 25 skipped; 7,887 test LOC covering 3,564 source LOC).

**Coverage target:** 85% (`fail_under` in `pyproject.toml`).

---

## Design Patterns [CURRENT]

This section documents the design patterns used in pypaginate, mapped to the
`guru-patterns-*` skill references. Understanding these patterns helps contributors
work within the existing architecture and guides future refactoring decisions.

### Facade (guru-patterns-structural)

**Where:** `FilterEngine` in `filters/predicates/engine.py`

The `FilterEngine` is a **Facade** that provides a simplified interface to the
filter subsystem. Internally it coordinates:

- `OperatorRegistry` — operator lookup and factory resolution
- `JsonLogicPredicateBuilder` — JSON Logic expression parsing
- `FieldAccessor` — nested field path resolution
- `CompiledFilter` — optimized filter execution

Users interact only with `FilterEngine.apply(items, filters)` without knowing
about these internal collaborators.

**Why Facade:** The filter subsystem has 4+ interacting classes. Without the Facade,
users would need to understand registry lookup, predicate compilation, and field
access — all internal concerns.

### Strategy (guru-patterns-behavioral)

**Where:** Search condition strategies in `filters/search/strategies.py`

The search subsystem uses the **Strategy pattern** with a `ConditionStrategy` Protocol
and three concrete implementations:

- `IdConditionStrategy` — search by ID field
- `PhraseConditionStrategy` — exact phrase matching
- `TermConditionStrategy` — individual term matching

Each strategy receives a `ConditionContext` and produces SQL conditions differently.
The search engine selects the appropriate strategy based on the parsed query tokens.

**Why Strategy:** Different search query types (IDs, phrases, individual terms) require
fundamentally different SQL generation logic. The Strategy pattern allows adding new
search modes without modifying existing code (Open/Closed Principle).

**Planned extension (v0.1.1):** The pagination engines (`SqlPaginator`,
`MemoryPaginator`, `KeysetPaginator`) follow similar conventions but lack a shared
`PaginationBackend` Protocol. Adding this Protocol will make pagination a true
Strategy pattern, enabling backend-agnostic pagination.

### Simple Factory + Registry (guru-patterns-creational)

**Where:** Multiple locations:

```{admonition} Not GoF Factory Method
:class: warning

These are **Simple Factories** (static creation functions) and a **Registry Pattern**
(name-to-factory mapping), not the GoF **Factory Method** pattern. The GoF Factory
Method requires subclass-based polymorphic instantiation — pypaginate uses none of
that. The distinction matters because Factory Method implies an inheritance hierarchy
that does not exist here.
```

**1. Simple Factory — Search service creation** in `filters/search/factories.py`:

- `create_memory_search_service(options)` — creates configured `MemorySearchEngine`
- `create_sql_search_service(options)` — creates configured `SqlSearchService`

These are plain functions that encapsulate complex object construction. They do not
use subclass polymorphism — they directly instantiate a known concrete class.

**2. Registry Pattern — Operator registration** in `filters/predicates/`:

The `OperatorRegistry` (`filters/predicates/registry.py`) maintains a mapping of
operator names to factory objects:

```python
# Registry maps names → factory callables
registry = OperatorRegistry()
registry.register(names=["eq"], factory=EqualityFactory())
registry.register(names=["gt"], factory=OrderingFactory("gt", operator.gt))

# Lookup by name at runtime
factory = registry.get("eq")
predicate = factory.create(value)
```

`EqualityFactory`, `OrderingFactory`, etc. are **Factory Objects** — callable classes
that produce predicates. The Registry enables runtime operator extensibility.

**Why these patterns:** Search services require complex configuration; factory
functions encapsulate this setup. The operator registry allows lazy instantiation,
parameterized creation, and user-extensible operator sets.

### Context Object

**Where:** `PaginationContext` in `core/context.py` and `ConditionContext` in
`filters/search/strategies.py`

Both classes bundle related parameters into immutable objects passed through call
chains, avoiding long parameter lists:

```python
# PaginationContext bundles pagination state
context = PaginationContext(params=page_params, options=options)
page = await paginator.paginate(query, context, scalars=True)

# ConditionContext bundles search state for strategies
context = ConditionContext(columns=columns, tokens=tokens, options=options)
conditions = strategy.collect(context)
```

**Why Context Object:** Without these, `paginate()` and `collect()` would need 5+
individual parameters. The Context Object satisfies the **Introduce Parameter Object**
refactoring technique (`guru-refactor-calls`).

### Adapter (guru-patterns-structural)

**Where:** FastAPI integration in `integrations/fastapi.py`

Two adapters bridge pypaginate's domain types to FastAPI's requirements:

1. **`PagedResponse[T]`** — adapts `Page[T]` (frozen dataclass) to a Pydantic model
   that FastAPI can serialize as `response_model`. This adapter is eliminated in v0.1.1
   when `Page` becomes a Pydantic model directly.

2. **`get_pagination_params()`** — adapts FastAPI query parameters (`page`, `limit`)
   into pypaginate's `PageParams` dataclass.

**Why Adapter:** FastAPI requires Pydantic models for response serialization, but
pypaginate's core uses frozen dataclasses for immutability. The Adapter bridges this
interface mismatch without coupling the core to FastAPI.

### Planned Patterns

#### Strategy for Backends (v0.1.1)

The `PaginationBackend`, `FilterBackend`, and `SortBackend` Protocols will formalize
the Strategy pattern for backend selection:

```python
class PaginationBackend(Protocol[T]):
    async def count(self, query: Any) -> int: ...
    async def fetch(self, query: Any, offset: int, limit: int) -> list[T]: ...
```

SQLAlchemy becomes one strategy among many. New backends (Tortoise, Beanie) implement
the same Protocol.

#### Builder for FilterModel (v0.2.0)

The planned `FilterModel` / `FilterSet` system may use the **Builder pattern**
(`guru-patterns-creational`) to construct complex filter configurations step by step,
with composability via `subset()` and `extract()`.

```{admonition} Pattern Not Yet Confirmed
:class: note

The actual pattern will depend on implementation. `FilterModel` may turn out to be
**Prototype** (clone-and-modify via `subset()`) or simply Pydantic model composition
rather than a true Builder with step-by-step construction. This will be clarified
during v0.2.0 implementation.
```

### Pattern Summary

| Pattern | Skill Reference | Current Implementation | Status |
|---------|----------------|----------------------|--------|
| **Facade** | `guru-patterns-structural` | `FilterEngine` | ✅ Implemented |
| **Strategy** | `guru-patterns-behavioral` | `ConditionStrategy` + 3 strategies | ✅ Implemented |
| **Simple Factory** | `guru-patterns-creational` | `create_*_search_service()` functions | ✅ Implemented |
| **Registry** | — (not in GoF) | `OperatorRegistry` + factory objects | ✅ Implemented |
| **Context Object** | — (Introduce Parameter Object) | `PaginationContext`, `ConditionContext` | ✅ Implemented |
| **Adapter** | `guru-patterns-structural` | `PagedResponse`, `get_pagination_params` | ✅ Implemented (PagedResponse removed in v0.1.1) |
| **Strategy (backends)** | `guru-patterns-behavioral` | `PaginationBackend` Protocol | 🔲 Planned v0.1.1 |
| **Builder or Prototype** | `guru-patterns-creational` | `FilterModel` / `FilterSet` | 🔲 Planned v0.2.0 (pattern TBD) |

---

## Further Reading

- [Pagination Strategies](pagination-strategies.md) — Understanding pagination
- [Filter Expressions](filter-expressions.md) — Filter system details
- [Search & Relevance](search-relevance.md) — Search implementation
- [Contributing: Architecture](../contributing/architecture.md) — Development details
- [Roadmap](../contributing/roadmap.md) — Release plan and target architecture timeline
