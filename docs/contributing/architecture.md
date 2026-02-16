# Architecture

pypaginate is organized into distinct layers with clear responsibilities and minimal coupling.

## Directory Structure

```
pypaginate/
├── core/              # Core data types and protocols
├── engines/           # Pagination strategy implementations
├── query/             # Query construction and execution
├── filters/           # Filtering and search
│   ├── predicates/    # JSON Logic filtering (24 operators)
│   └── search/        # Text search engines
├── sorting/           # Sorting utilities
├── text/              # Text processing
├── database/          # Database utilities
├── integrations/      # Framework integrations
│   └── fastapi.py     # FastAPI integration
└── exceptions.py      # Custom exceptions (9 classes)
```

## Core Principles

### 1. Framework Agnostic Core

The core pagination logic has zero dependencies on web frameworks or ORMs:

- Lightweight for simple use cases
- Easy to integrate with any framework
- Testable without external dependencies

### 2. Optional Dependencies

Features are organized with optional dependencies:

```python
# Core (no dependencies)
from pypaginate.core import PageParams, Page
from pypaginate.engines import MemoryPaginator

# SQLAlchemy support (optional)
uv add pypaginate[sqlalchemy]
from pypaginate.query import paginate_entities

# All features
uv add pypaginate[all]
```

### 3. Immutable Data Types

All core types are currently immutable frozen dataclasses:

```python
@dataclass(frozen=True, slots=True)
class PageParams:
    page: int = 1
    limit: int = 20
```

Benefits:
- Thread-safe
- Hashable
- Predictable behavior

```{admonition} Planned Change (v0.1.1)
:class: warning

`Page[T]` will be migrated from a frozen dataclass to a **frozen Pydantic model**.
This eliminates the separate `PagedResponse[T]` wrapper needed for FastAPI and lets
`Page[T]` work directly as `response_model`. `PageParams` remains a frozen dataclass.
```

### 4. Protocol-Based Design

Core interfaces use Protocols for duck typing. Currently 5 protocols are defined
in `types.py`:

| Protocol | Purpose | Key Members |
|----------|---------|-------------|
| `PageParamsProtocol` | Pagination parameters | `page`, `limit`, `offset`, `model_copy()` |
| `PageProtocol` | Paginated result | `items`, `total`, `page`, `limit` |
| `SupportsTotalOrdering` | Sortable types | `__lt__`, `__le__`, `__gt__`, `__ge__` |
| `SqlClause` | SQL composability | `__and__`, `__or__` |
| `SqlStringExpression` | SQL string operations | `in_()`, `like()` |

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
```

This allows custom implementations without inheritance.

```{admonition} Planned Addition (v0.1.1)
:class: note

Three new backend protocols will be added to enable multi-ORM support:
`PaginationBackend`, `FilterBackend`, `SortBackend`. See the
[Roadmap](roadmap.md#v011--architecture-refactoring) for details.
```

## Layered Architecture

```
┌────────────────────────────────────────┐
│  Public API (pypaginate.__init__)     │
│  - Page, PageParams, paginate_*        │
│  - 14 exported names                   │
└─────────────────┬──────────────────────┘
                  │
┌─────────────────▼──────────────────────┐
│  Query Layer (query/)                  │
│  - Orchestrates pagination             │
│  - High-level async API                │
└────────┬──────────────────┬────────────┘
         │                  │
┌────────▼────────┐   ┌────▼────────────┐
│  Engines        │   │  Execution      │
│  - SqlPaginator │   │  - Async exec   │
│  - Memory       │   │  - Builders     │
│  - Keyset       │   │                 │
└────────┬────────┘   └─────────────────┘
         │
┌────────▼───────────────────────────────┐
│  Utilities                             │
│  - filters/ (JSON Logic + SQL adapter) │
│  - filters/search/ (fuzzy, SQL, mem)   │
│  - sorting/ (SortEngine + SQL adapter) │
│  - text/ (UTF-8, patterns)             │
│  - database/ (type aliases)            │
└────────────────────────────────────────┘
         │
┌────────▼───────────────────────────────┐
│  Core Types (core/)                    │
│  - Page, PageParams (frozen dataclass) │
│  - 5 Protocols (types.py)              │
│  - Context, Snapshots                  │
│  - 9 Exception classes                 │
└────────────────────────────────────────┘
```

## Key Components

### Core Types (`core/`)

**pages.py**: Main data structures
- `PageParams`: Pagination parameters (page, limit) — frozen dataclass
- `Page[T]`: Generic paginated result container — frozen dataclass
- `KeysetPageParams`: Cursor-based pagination params — frozen dataclass

**context.py**: Execution context
- `PaginationContext`: Carries parameters and options
- `clamp_page_params`: Clamp to valid range

**snapshots.py**: Internal result containers
- `PaginationSnapshot`: Results with metadata

### Engines (`engines/`)

**SqlPaginator**: Database pagination
- Offset-based pagination for SQL databases
- Works with SQLAlchemy Select statements
- Automatic COUNT query generation
- Keyset pagination support (via sqlakeyset)

**MemoryPaginator**: In-memory pagination
- Fast pagination for Python collections
- No database required
- Supports predicate-based filtering

**KeysetPaginator** (in `keyset.py`): Cursor-based pagination
- Better performance for large datasets
- Stable pagination (no page drift)
- Requires indexed sort column

### Filtering (`filters/`)

**Predicates** (`filters/predicates/`):
- JSON Logic-based filtering
- 24 operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `notin`,
  `between`, `range`, `contains`, `icontains`, `startswith`, `istartswith`,
  `endswith`, `iendswith`, `like`, `ilike`, `regex`, `iregex`, `is_null`,
  `is_not_null`, `empty`, `not_empty`
- Type-safe operator validation via factory classes

**SQL Adapter** (`filters/sql_adapter.py`):
- Generates SQLAlchemy WHERE clauses
- 14 operators (with 6 aliases): `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`,
  `not_in`, `like`, `ilike`, `is_null`, `contains`, `startswith`, `endswith`
- 10 predicate operators not yet ported to SQL (planned for v0.1.1)

**Search** (`filters/search/`):
- Full-text search with fuzzy matching (RapidFuzz)
- SQL and in-memory implementations
- Token parsing (AND/OR/FUZZY modes)
- UTF-8 text normalization, accent-insensitive search

### Query Layer (`query/`)

**async_api.py**: High-level async functions
- `paginate_entities()`: Paginate ORM entities
- `paginate_rows()`: Paginate raw SQL rows
- Automatic count query optimization

### FastAPI Integration (`integrations/fastapi.py`)

**Current:**
- `PagedResponse[T]`: Pydantic wrapper for Page (eliminated in v0.1.1)
- `get_pagination_params()`: FastAPI dependency for PageParams

## Design Patterns

### Facade Pattern

`FilterEngine` provides a simplified interface over the complex predicate
subsystem (`OperatorRegistry`, `JsonLogicPredicateBuilder`, `FieldAccessor`,
`CompiledFilter`):

```python
# Users interact with one simple class
engine = FilterEngine()
results = engine.apply(items, {"age": {"gte": 18}})

# Internally, FilterEngine coordinates:
# - OperatorRegistry (24 operators)
# - JsonLogicPredicateBuilder (spec → predicate)
# - FieldAccessor (dot-path resolution)
# - CompiledFilter (accessor + predicate pair)
```

### Strategy Pattern

The search subsystem uses a proper Strategy pattern with a shared Protocol and
Context:

```python
class ConditionStrategy(Protocol):
    def collect(self, context: ConditionContext) -> list[SqlClause]: ...

# Three interchangeable strategies
class IdConditionStrategy:       # Matches ID patterns
    def collect(self, context): ...

class PhraseConditionStrategy:   # Matches quoted phrases
    def collect(self, context): ...

class TermConditionStrategy:     # Matches individual terms
    def collect(self, context): ...
```

`SqlConditionBuilder` iterates over these strategies — they can be added,
removed, or reordered without changing the builder.

**Pagination engines (Partial Strategy — v0.1.0):**

Pagination engines follow a **similar convention** but do **not** yet share a
common Protocol or Context class. Their signatures differ:

```python
class SqlPaginator:
    async def paginate(self, query, context, *, scalars): ...  # async

class MemoryPaginator:
    def paginate(self, items, params): ...  # sync
```

```{admonition} Not a True Strategy Yet
:class: warning

The pagination engines cannot be swapped — one is async with
`(query, context)`, the other is sync with `(items, params)`. The planned
`PaginationBackend` protocol (v0.1.1) will unify them into a proper
Strategy pattern like the search conditions above.
```

### Simple Factory + Registry Pattern

Search services use **Simple Factory** functions for creation (not GoF Factory Method
— no subclass polymorphism is involved):

```python
service = create_memory_search_service(options)
service = create_sql_search_service(options)
```

Operator registration uses the **Registry Pattern** with factory objects:

```python
registry.register(names=["eq"], factory=EqualityFactory())
registry.register(names=["gt"], factory=OrderingFactory("gt", operator.gt))
```

`OperatorRegistry` (`filters/predicates/registry.py`) maps operator names to callable
factory objects, enabling runtime extensibility. `EqualityFactory`, `OrderingFactory`,
etc. are Factory Objects — callable classes that produce predicates on demand.

### Context Object Pattern

`PaginationContext` (`core/context.py`) and `ConditionContext`
(`filters/search/strategies.py`) bundle related parameters into immutable objects
to avoid long parameter lists:

```python
context = PaginationContext(params=page_params, options=options)
page = await paginator.paginate(query, context, scalars=True)
```

This satisfies the **Introduce Parameter Object** technique (`guru-refactor-calls`).

### Utility Functions (Count Queries)

Count query construction uses module-level utility functions (not a Builder
pattern — there is no step-by-step construction):

```python
from pypaginate.query.builders.count_builder import build_count_statement

count_stmt = build_count_statement(query, explicit=None, unique=False)
```

### Adapter Pattern

Framework integrations adapt pypaginate to specific APIs:

```python
from pypaginate.integrations.fastapi import (
    PagedResponse,       # Adapts Page → Pydantic
    get_pagination_params  # Adapts Query → PageParams
)
```

## Extension Points

### Adding a New Operator

1. Create operator factory in `filters/predicates/operators/`
2. Register in `operators/__init__.py` via `register_default_operators()`
3. Optionally add SQL counterpart in `filters/sql_adapter.py`
4. Add tests
5. Update documentation

### Adding a New Pagination Engine

1. Create class in `engines/`
2. Implement `paginate()` method returning `Page[T]`
3. Add to `engines/__init__.py`
4. Add tests and examples

### Adding a Framework Integration

1. Create module in `integrations/`
2. Add optional dependency to `pyproject.toml`
3. Provide helpful ImportError if missing
4. Add examples and documentation

## Performance Considerations

### SQL Pagination

- **Offset pagination**: Good for small-medium datasets
  - Simple implementation
  - Stable page numbers
  - Slower for deep pagination (page 1000+)

- **Keyset pagination**: Best for large datasets
  - Constant-time pagination
  - No page drift
  - Requires indexed sort column

### Memory Pagination

- Fast for collections < 10k items
- No database roundtrips
- Entire dataset must fit in memory

### Filtering

- In-memory filtering: O(n) per filter
- SQL filtering: Pushed to database (indexed)
- Combine filters before pagination when possible

## Thread Safety

- All core types are immutable (thread-safe)
- Engine instances are stateless (thread-safe)
- Session/connection handling is caller's responsibility

## Known Technical Debt (v0.1.0)

These issues are being addressed in v0.1.1:

| Issue | Count | Impact |
|-------|-------|--------|
| Boolean parameters in API | 52 instances (17 unique names) | Violates AGENTS.md standards |
| Files over 200 lines | 11 files | Maintenance burden |
| Functions over 12 body lines | 11 violations | Complexity risk |
| French comments | 19 lines across 5 files | Consistency |
| Untested modules | 8 of 42 modules | Quality risk |
| SQL adapter operator gap | 10 missing operators | Incomplete SQL support |
| Dual Page/PagedResponse | 2 representations | API confusion |
| `__all__` inconsistency | 3 imported but unexported | Public API unclear |
| No backend abstractions | Engines coupled to SQLAlchemy | Violates Dependency Inversion |

```{note}
Three exception classes (`FilterValidationError`, `SearchQueryError`,
`SearchNormalizationError`) are imported in `__init__.py` but not listed
in `__all__`. Users can access them, but they are not part of the
documented public API. This will be resolved in v0.1.1.
```

See the [Roadmap](roadmap.md) for the full remediation plan.

## Quality Standards

All code must maintain:

- 100% type coverage (`mypy --strict`)
- Zero linting issues (`ruff check`)
- Consistent formatting (`ruff format`)
- Minimum 85% test coverage (`fail_under = 85` in pyproject.toml)
- Zero boolean parameters in public API (enforced from v0.1.1)

## Architecture Principles

This section maps pypaginate's architecture to the principles defined in the
`arch-principles` skill. These are the rules that guide all refactoring decisions
in v0.1.1 and beyond.

### Layered Architecture Mapping

The `arch-principles` skill defines a standard 4-layer model:

| Standard Layer | pypaginate Equivalent | Actual Modules |
|---------------|----------------------|----------------|
| **Presentation / Interface** | Public API + Integration | `__init__.py`, `integrations/fastapi.py` |
| **Application** | Query Layer | `query/async_api.py`, `query/execution/` |
| **Domain** | Engines + Filters + Sorting + Core | `engines/`, `filters/`, `sorting/`, `core/` |
| **Infrastructure** | Database + External I/O | `database/`, SQLAlchemy calls in `engines/sql.py` |

**Current violations of the Dependency Rule** (source code dependencies must point
inward toward higher-level policies):

- `engines/sql.py` imports SQLAlchemy directly — infrastructure leaks into domain
- `filters/sql_adapter.py` imports SQLAlchemy directly — same violation
- `sorting/sql_adapter.py` imports SQLAlchemy directly — same violation

**Resolution (v0.1.1):** Introduce `PaginationBackend`, `FilterBackend`, and
`SortBackend` protocols. SQL-specific code becomes an infrastructure adapter
implementing these protocols, satisfying the **Dependency Inversion Principle**.

### Dependency Inversion Principle

Per `arch-principles`: *"High-level modules should not depend on low-level modules.
Both should depend on abstractions."*

| Abstraction | Current State | v0.1.1 Target |
|-------------|--------------|---------------|
| Pagination backend | `SqlPaginator` directly uses `AsyncSession` | `PaginationBackend` Protocol |
| Filter backend | `SqlFilterAdapter` directly uses SQLAlchemy Column | `FilterBackend` Protocol |
| Sort backend | `SqlSortAdapter` directly uses SQLAlchemy Column | `SortBackend` Protocol |

### Separation of Concerns

Per `arch-principles`: *"Each module should have a single reason to change."*

**Current violations:**

- `_cli.py` (390 lines) mixes command parsing, subprocess execution, output
  formatting, and help text rendering — 4 reasons to change
- `filters/search/memory_search.py` (448 lines) mixes scoring, matching, and
  engine orchestration — 3 reasons to change

### Exception Hierarchy

The existing exception hierarchy (9 classes rooted at `PaginatorException`) follows
the `arch-principles` recommendation to "design a consistent exception hierarchy that
reflects your domain." The hierarchy correctly separates pagination, filter, search,
and sort exceptions.

### Public API Design

Per `arch-principles`: *"Use `__all__` to be explicit about public API."*

**Current issue:** 3 exception classes are imported in `__init__.py` but not in
`__all__`. This violates the "explicit exports" principle. Resolved in v0.1.1.

### Dependency Injection

Per `arch-principles`: *"Depend on abstractions, inject dependencies through
constructors."*

pypaginate uses **constructor injection** for its primary components:

```python
# SqlPaginator receives its session dependency via constructor
paginator = SqlPaginator(session, clamp=True)  # v0.1.0 — bool; v0.1.1 → enum

# Search services are created via factory functions that inject options
service = create_memory_search_service(options)
service = create_sql_search_service(options)
```

**Current state:**

| Component | Injection Method | Status |
|-----------|-----------------|--------|
| `SqlPaginator` | Constructor (`session`) | ✅ Correct pattern |
| `MemoryPaginator` | No dependencies | ✅ N/A (pure logic) |
| `FilterEngine` | No external dependencies | ✅ N/A (self-contained) |
| Search services | Factory functions | ✅ Correct pattern |
| `SqlFilterAdapter` | `@staticmethod` (no injection) | ⚠️ Cannot be extended |

**v0.1.1 improvement:** When `PaginationBackend` Protocol is introduced, the
composition root (the user's application code or FastAPI dependency) will inject the
concrete backend:

```python
# v0.1.1 — backend injected at composition root
backend = SqlAlchemyBackend(session)
page = await paginate(query, params, backend=backend)
```

### Async/Await Patterns

Per `arch-principles`: *"Choose sync or async consistently within a layer."*

**Current inconsistency:**

| Layer | Sync | Async | Issue |
|-------|------|-------|-------|
| Public API (`query/async_api.py`) | — | ✓ | OK — async-only layer |
| `SqlPaginator` | — | ✓ | OK — database I/O |
| `MemoryPaginator` | ✓ | — | ⚠️ Same layer, different paradigm |
| `FilterEngine` | ✓ | — | OK — pure computation |
| `SortEngine` | ✓ | — | OK — pure computation |

The engines layer mixes async (`SqlPaginator`) and sync (`MemoryPaginator`). This
means they cannot share a Protocol without `async def` everywhere or a sync/async
split.

**v0.1.1 decision needed:** Either:
1. Make `PaginationBackend` Protocol async-only (force `MemoryPaginator` to be async)
2. Create separate `SyncPaginationBackend` and `AsyncPaginationBackend` Protocols
3. Use `async def` in Protocol but allow sync implementations via trivial `await`

Option 1 is simplest and matches the public API layer (already all-async). The
cost is that in-memory pagination gains an unnecessary `async` wrapper.

### Anti-Patterns Checklist

Per `arch-principles`, these anti-patterns must be actively avoided:

| Anti-Pattern | Status | Evidence |
|--------------|--------|----------|
| **God Class** | ⚠️ Active | `_cli.py` (390 lines, 4 concerns) — being split in v0.1.1 |
| **Anemic Domain Model** | ✅ N/A | Domain types (`Page`, `PageParams`) have behavior (properties, computed fields) |
| **Circular Dependencies** | ✅ None found | Layers depend downward only |
| **Leaky Abstractions** | ⚠️ Active | SQLAlchemy types leak into engine/filter/sort layers |

---

## Code Smell Reference (v0.1.0)

This section maps every known v0.1.0 code quality issue to its `guru-smells`
category. Each issue has a prescribed `guru-refactor-*` technique that must be
applied during v0.1.1 refactoring.

### Bloaters

#### Long Method (guru-smells)

11 functions exceed the 12 body-line limit. Per `guru-smells`: *"Methods with too
many lines that do too much."*

| Body Lines | File | Function | Prescribed Technique |
|------------|------|----------|---------------------|
| 37 | `_cli.py:271` | `cmd_clean` | **Extract Method** (`guru-refactor-methods`) — pull subprocess calls into helper |
| 35 | `filters/sql_adapter.py:22` | `build_condition` | **Replace Conditional with Polymorphism** (`guru-refactor-conditionals`) — strategy dict replaces match/case |
| 32 | `_cli.py:312` | `_show_help` | **Extract Method** — extract help text into template |
| 31 | `_cli.py:216` | `cmd_quality_strict` | **Parameterize Method** (`guru-refactor-calls`) — merge with `cmd_quality` using config |
| 30 | `_cli.py:182` | `cmd_quality` | **Parameterize Method** — merge with `cmd_quality_strict` |
| 16 | `_cli.py:251` | `cmd_build` | **Extract Method** — extract build steps |
| 16 | `filters/predicates/jsonlogic_evaluator.py:105` | `_patched_json_logic_env` | **Extract Method** — extract env setup |
| 15 | `_cli.py:71` | `_run` | **Extract Method** — extract output handling |
| 14 | `_cli.py:164` | `cmd_test_cov` | **Extract Method** — extract test configuration |
| 13 | `_cli.py:372` | `main` | **Replace Conditional with Polymorphism** — extract command dispatch dict |
| 13 | `filters/search/options.py:174` | `_coerce_mode_option` | **Decompose Conditional** (`guru-refactor-conditionals`) — extract validation branches |

#### Large Class (guru-smells)

11 files exceed the 200-line limit. Per `guru-smells`: *"Classes with too many fields,
methods, or lines of code."*

| File | Lines | Prescribed Technique |
|------|-------|---------------------|
| `filters/search/memory_search.py` | 448 | **Extract Class** (`guru-refactor-moving`) → `memory_engine.py`, `memory_scoring.py`, `memory_matching.py` |
| `_cli.py` | 390 | **Extract Class** → `_cli/commands.py`, `_cli/runner.py`, `_cli/output.py` |
| `filters/search/helpers.py` | 302 | **Extract Class** → `search/sql_helpers.py`, `search/field_helpers.py` |
| `filters/search/options.py` | 298 | **Extract Class** → `search/config.py`, `search/validation.py` |
| `query/async_api.py` | 289 | **Extract Class** → `query/options.py` |
| `engines/sql.py` | 287 | **Extract Class** → `engines/sql_count.py`, `engines/sql_fetch.py` |
| `filters/search/parser.py` | 245 | **Extract Class** → `search/tokens.py` |
| `core/snapshots.py` | 228 | **Extract Class** → `core/serialization.py` |
| `sorting/engine.py` | 217 | **Extract Class** → `sorting/null_handling.py` |
| `filters/predicates/field_accessor.py` | 206 | **Extract Class** → `predicates/path_resolver.py` |
| `engines/memory.py` | 199 | Borderline — monitor after other splits |

#### Primitive Obsession (guru-smells)

52 boolean parameter instances across 17 unique names. Per `guru-smells`:
*"Using primitives instead of small objects for simple tasks."*

**Prescribed techniques:**

- **Replace Type Code with Class** (`guru-refactor-data`) — create enums:
  `OverflowStrategy`, `ResultMode`, `ReturnType`, `SearchFieldMode`, `CaseTransform`,
  `SortDirection`, `CaseSensitivity`
- **Replace Parameter with Explicit Methods** (`guru-refactor-calls`) — where only
  two behaviors exist: `sort_ascending()` / `sort_descending()` instead of `reverse`

See [Roadmap: Boolean Parameter Elimination](roadmap.md#boolean-parameter-elimination)
for the complete replacement inventory.

#### Long Parameter List (guru-smells)

Related to the boolean parameters above. Per `guru-smells`: *"More than 4 parameters."*

**Prescribed technique:** **Introduce Parameter Object** (`guru-refactor-calls`) —
group related parameters into configuration dataclasses.

### Object-Orientation Abusers

#### Switch Statements (guru-smells)

`SqlFilterAdapter.build_condition` is a 35-line `match`/`case` dispatching 14
operators. Per `guru-smells`: *"Complex switch/match statements that switch on type
codes."*

**Prescribed technique:** **Replace Conditional with Polymorphism**
(`guru-refactor-conditionals`) — replace with strategy dict mapping operator names
to callable builders.

#### Alternative Classes with Different Interfaces (guru-smells)

`SqlPaginator` and `MemoryPaginator` serve the same purpose (pagination) but have
incompatible signatures:

- `SqlPaginator.paginate(query, context, *, scalars)` — async, takes query + context
- `MemoryPaginator.paginate(items, params)` — sync, takes items + params

Per `guru-smells`: *"Two classes that perform identical functions but have different
method names or signatures."*

**Prescribed technique:** **Extract Superclass** (`guru-refactor-generalization`) —
introduce `PaginationBackend` Protocol with a unified `paginate()` signature (v0.1.1).

### Change Preventers

#### Divergent Change (guru-smells)

`_cli.py` changes for 4 different reasons: new commands, new runner behavior, output
format changes, help text updates. Per `guru-smells`: *"One class is commonly changed
for different reasons."*

**Prescribed technique:** **Extract Class** (`guru-refactor-moving`) — split into
`_cli/commands.py`, `_cli/runner.py`, `_cli/output.py`.

#### Shotgun Surgery (guru-smells)

Multiple issues require coordinated changes across many files:

- 52 boolean parameters across 21 files — changing the parameter style requires
  editing every call site simultaneously
- Re-export inconsistencies across `__init__.py` files — adding a public name
  requires updating both the module and the package re-exports

Per `guru-smells`: *"Making a modification requires changing many different classes at
the same time."*

**Prescribed technique:** **Inline Class** (`guru-refactor-moving`) for re-export
consolidation + **Replace Type Code with Class** (`guru-refactor-data`) to eliminate
booleans with enums that centralize the type definition.

### Dispensables

#### Comments — French Comments (guru-smells)

19 lines of French comments across 5 files. Per `guru-smells`: *"Comments that
explain what code does instead of why"* — these comments are in the wrong language
entirely.

**Prescribed technique:** Delete or translate to English. No refactoring technique
needed — this is a simple find-and-replace.

#### Duplicate Code (guru-smells)

`Page[T]` (frozen dataclass) and `PagedResponse[T]` (Pydantic wrapper) represent
the same concept in two forms. Per `guru-smells`: *"Same code structure in multiple
places."*

**Prescribed technique:** **Inline Class** (`guru-refactor-moving`) — merge into a
single `Page[T]` Pydantic model, eliminating `PagedResponse` entirely.

#### Speculative Generality (guru-smells)

10 predicate operators are built and registered but have no SQL adapter counterpart:
`between`, `range`, `icontains`, `istartswith`, `iendswith`, `regex`, `iregex`,
`is_not_null`, `empty`, `not_empty`. These operators work only for in-memory filtering
— any user expecting SQL support will hit a runtime error.

Per `guru-smells`: *"Code that was created 'just in case' to support anticipated future
features that never materialized."*

**Prescribed technique:** **Introduce Foreign Method** (`guru-refactor-moving`) — add
the 10 missing SQL implementations to make these operators fully functional. If an
operator truly has no SQL equivalent (unlikely), mark it as in-memory-only explicitly.

#### Dead Code (guru-smells) — INVESTIGATION NEEDED

8 untested modules may contain dead code paths. Without test coverage, unreachable
code cannot be detected with confidence. Per `guru-smells`: *"Code that is never
executed."*

**Prescribed action:** Run `vulture` dead-code detection (`dead-code` tool) on the
untested modules after adding test coverage. Flag and remove confirmed dead code.

### Couplers

#### Inappropriate Intimacy (guru-smells)

`_cli.py` (390 lines) has 4 tightly coupled concerns: command parsing, subprocess
execution, output formatting, and help rendering. These concerns access each other's
internal details — the command functions directly call `_run()` which mixes output
capture and subprocess invocation.

Per `guru-smells`: *"One class uses the internal fields and methods of another class."*

**Prescribed technique:** **Extract Class** (`guru-refactor-moving`) — split into
`_cli/commands.py`, `_cli/runner.py`, `_cli/output.py` with clean interfaces between
them. This is the same split prescribed for the Large Class smell above.

#### Incomplete Library Class (guru-smells)

The SQL adapter has only 14 operators while the predicate engine has 24. Per
`guru-smells`: *"A library class doesn't provide functionality you need."*

**Prescribed technique:** **Introduce Foreign Method** (`guru-refactor-moving`) —
add the 10 missing SQL operator implementations to `SqlFilterAdapter`.

---

## Refactoring Techniques Reference

This section provides a quick reference of all `guru-refactor-*` techniques used
in the v0.1.1 refactoring plan, grouped by skill.

### guru-refactor-methods (Composing Methods)

| Technique | Used For |
|-----------|----------|
| **Extract Method** | 8 CLI functions, `_patched_json_logic_env`, `_coerce_mode_option` |

### guru-refactor-moving (Moving Features)

| Technique | Used For |
|-----------|----------|
| **Extract Class** | All 11 oversized files — split into focused modules |
| **Inline Class** | Merge `PagedResponse` into `Page` |
| **Introduce Foreign Method** | Add 10 missing SQL adapter operators |

### guru-refactor-data (Organizing Data)

| Technique | Used For |
|-----------|----------|
| **Replace Type Code with Class** | 52 boolean params → enums (`OverflowStrategy`, `ResultMode`, etc.) |

### guru-refactor-conditionals (Simplifying Conditionals)

| Technique | Used For |
|-----------|----------|
| **Replace Conditional with Polymorphism** | `build_condition` match/case → strategy dict; CLI `main` dispatch |
| **Decompose Conditional** | `_coerce_mode_option` validation branches |

### guru-refactor-calls (Simplifying Method Calls)

| Technique | Used For |
|-----------|----------|
| **Parameterize Method** | Merge `cmd_quality` + `cmd_quality_strict` |
| **Replace Parameter with Explicit Methods** | `reverse=True/False` → `sort_ascending()` / `sort_descending()` |
| **Introduce Parameter Object** | Group related function parameters |

### guru-refactor-generalization (Dealing with Generalization)

| Technique | Used For |
|-----------|----------|
| **Extract Superclass** | Unify `SqlPaginator` + `MemoryPaginator` under `PaginationBackend` Protocol |

---

## See Also

- [Code Style](code-style.md) — Coding standards
- [Testing Guide](testing.md) — Testing practices
- [Roadmap](roadmap.md) — Future plans
- [Concepts: Architecture](../concepts/architecture.md) — User-facing architecture overview
