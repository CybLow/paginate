# Roadmap

Development plan for pypaginate — from v0.1.0 to production-ready v1.0.0.

**Current version:** 0.1.0
**Goal:** Unified pagination + filtering + search library that exceeds
fastapi-pagination + fastapi-filters combined.

## Release Overview

| Version | Focus | Key Deliverable |
|---------|-------|-----------------|
| **v0.1.1** | Architecture refactoring | Clean foundation |
| **v0.2.0** | Declarative FastAPI integration | FilterDepends, OrderingDepends |
| **v0.3.0** | Pagination formats & auto-setup | LimitOffsetPage, CursorPage, add_pagination |
| **v0.4.0** | Multi-backend & advanced features | Tortoise, Beanie, JOIN filters |
| **v1.0.0** | Production ready | API stability guarantee |

---

## v0.1.1 — Architecture Refactoring

**Focus:** Fix the foundation before building on it.

The v0.1.0 codebase has significant violations of the project's own standards.
This release fixes them without adding features.

### Boolean Parameter Elimination

> **Smell:** Primitive Obsession (`guru-smells` → Bloaters) + Long Parameter List (`guru-smells` → Bloaters) + Shotgun Surgery (`guru-smells` → Change Preventers)
> **Technique:** Replace Type Code with Class (`guru-refactor-data`), Replace Parameter with Explicit Methods (`guru-refactor-calls`)
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010)
>
> **Note:** The 52 boolean instances across 21 files also constitute **Shotgun Surgery** —
> changing the parameter style requires editing every call site simultaneously.
> Replacing booleans with centralized enum types resolves both smells at once.

**Problem:** 52 boolean parameter instances exist across 17 unique parameter names
in ~21 source files, violating the AGENTS.md ban on boolean parameters.

**Solution:** Replace with separate methods, enums, or strategy objects.

```python
# Before (v0.1.0)
paginator = MemoryPaginator(clamp=True)
engine.sort(items, field="name", reverse=True)
normalizer = Utf8Normalizer(lowercase=True, casefold_output=True)

# After (v0.1.1)
paginator = MemoryPaginator(overflow=OverflowStrategy.CLAMP)
engine.sort_ascending(items, field="name")
engine.sort_descending(items, field="name")
normalizer = Utf8Normalizer(case=CaseTransform.LOWER)
```

**Complete boolean parameter inventory:**

| Parameter | Occurrences | Files | Replacement Strategy |
|-----------|-------------|-------|---------------------|
| `prefix` | 10 | 4 (`search/conditions.py`, `search/fuzzy.py`, `search/helpers.py`, `search/memory_search.py`) | `SearchFieldMode` enum (`PREFIX`/`EXACT`/`CONTAINS`) |
| `unique` | 9 | 4 (`engines/keyset.py`, `engines/sql.py`, `query/builders/count_builder.py`, `query/execution/async_executor.py`) | `ResultMode.UNIQUE` / `ResultMode.ALL` |
| `scalars` | 8 | 4 (`core/snapshots.py`, `engines/sql.py`, `query/async_api.py`, `query/execution/async_executor.py`) | `ReturnType.SCALARS` / `ReturnType.ROWS` |
| `reverse` | 5 | 1 (`sorting/engine.py`) | Separate methods: `sort_ascending()` / `sort_descending()` |
| `predicate` | 3 | 1 (`engines/memory.py`) | `FilterMode.PREDICATE` / `FilterMode.NONE` |
| `clamp` | 3 | 3 (`engines/memory.py`, `engines/sql.py`, `query/execution/async_executor.py`) | `OverflowStrategy.CLAMP` / `OverflowStrategy.ERROR` |
| `deep` | 2 | 2 (`core/pages.py`, `types.py`) | `CopyDepth.SHALLOW` / `CopyDepth.DEEP` |
| `comparator` | 2 | 1 (`filters/predicates/operators/comparison.py`) | Pass the comparator function directly |
| `case_sensitive` | 2 | 1 (`text/patterns.py`) | `CaseSensitivity.SENSITIVE` / `INSENSITIVE` |
| `check` | 1 | 1 (`_cli.py`) | `RunMode.CHECK` / `RunMode.EXECUTE` |
| `capture` | 1 | 1 (`_cli.py`) | `OutputCapture.CAPTURE` / `OutputCapture.PASSTHROUGH` |
| `conditions` | 1 | 1 (`filters/sql_adapter.py`) | Accept conditions list directly |
| `first` | 1 | 1 (`filters/predicates/field_accessor.py`) | `MatchPosition.FIRST` / `MatchPosition.ALL` |
| `flags` | 1 | 1 (`filters/search/memory_search.py`) | Accept `re.RegexFlag` directly |
| `descending` | 1 | 1 (`sorting/sql_adapter.py`) | `SortDirection.ASC` / `SortDirection.DESC` |
| `lowercase` | 1 | 1 (`text/utf8.py`) | `CaseTransform.LOWER` / `NONE` / `FOLD` |
| `casefold_output` | 1 | 1 (`text/utf8.py`) | Merge with `lowercase` into `CaseTransform` enum |

**Priority order:** `prefix` (10) → `unique` (9) → `scalars` (8) → `reverse` (5)
→ remaining single-occurrence params.

### French Comment Removal

> **Smell:** Comments (`guru-smells` → Dispensables)
> **Technique:** Delete or translate — no refactoring technique needed
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010)

**Problem:** 19 lines of French comments across 5 files.

| File | Lines | Content |
|------|-------|---------|
| `sorting/engine.py` | 27, 174, 175, 185, 214 | `← Renommé de SortService`, `← Mis à jour` (×4) |
| `filters/predicates/jsonlogic_evaluator.py` | 3–4, 99, 131, 150 | Docstring in French, `Bypass l'annotation typeshed`, `Évalue une règle`, `Facade fonctionnelle` |
| `filters/search/__init__.py` | 21, 27, 29, 33 | `API publique principale` (×3), `helpers de création` |
| `filters/__init__.py` | 24, 36, 54, 65 | `API principale` (×2), `Filtrage par prédicats JSON Logic`, `Recherche textuelle` |
| `filters/search/helpers.py` | 85 | `Wrapper explicite plutôt que functools.partial` |

**Action:** Replace all with English equivalents or remove where they add no value.

### File Size Reduction

> **Smell:** Large Class (`guru-smells` → Bloaters)
> **Technique:** Extract Class (`guru-refactor-moving`)
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010)

**Problem:** 11 files exceed the 200-line limit.

| File | Lines | Action |
|------|-------|--------|
| `filters/search/memory_search.py` | 448 | Split: `memory_engine.py` (core engine), `memory_scoring.py` (scoring/ranking), `memory_matching.py` (pattern matching) |
| `_cli.py` | 390 | Split: `_cli/commands.py` (subcommands), `_cli/runner.py` (execution), `_cli/output.py` (formatting) |
| `filters/search/helpers.py` | 302 | Split: `search/sql_helpers.py` (SQL clause building), `search/field_helpers.py` (field expression building) |
| `filters/search/options.py` | 298 | Split: `search/config.py` (configuration dataclasses), `search/validation.py` (option validation) |
| `query/async_api.py` | 289 | Extract: `query/options.py` (option building), keep API functions in `async_api.py` |
| `engines/sql.py` | 287 | Extract: `engines/sql_count.py` (count logic), `engines/sql_fetch.py` (fetch/materialize) |
| `filters/search/parser.py` | 245 | Extract: `search/tokens.py` (token types and dataclasses) |
| `core/snapshots.py` | 228 | Extract: `core/serialization.py` (keyset materialization) |
| `sorting/engine.py` | 217 | Extract: `sorting/null_handling.py` (null-aware comparison) |
| `filters/predicates/field_accessor.py` | 206 | Extract: `predicates/path_resolver.py` (nested path resolution) |
| `engines/memory.py` | 199 | Borderline — monitor after other splits |

### Function Length Violations

> **Smell:** Long Method (`guru-smells` → Bloaters) + Switch Statements (`guru-smells` → OO Abusers) for `build_condition`
> **Technique:** Extract Method (`guru-refactor-methods`), Replace Conditional with Polymorphism (`guru-refactor-conditionals`), Parameterize Method (`guru-refactor-calls`)
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010)

**Problem:** 11 functions exceed the 12 body-line limit.

| Body Lines | File | Function | Action |
|------------|------|----------|--------|
| 37 | `_cli.py:271` | `cmd_clean` | Extract subprocess calls into helper |
| 35 | `filters/sql_adapter.py:22` | `SqlFilterAdapter.build_condition` | Extract operator dispatch into strategy dict |
| 32 | `_cli.py:312` | `_show_help` | Extract help text into template |
| 31 | `_cli.py:216` | `cmd_quality_strict` | Extract shared quality logic with `cmd_quality` |
| 30 | `_cli.py:182` | `cmd_quality` | Merge with `cmd_quality_strict` using config |
| 16 | `_cli.py:251` | `cmd_build` | Extract build steps |
| 16 | `filters/predicates/jsonlogic_evaluator.py:105` | `_patched_json_logic_env` | Extract env setup into helper |
| 15 | `_cli.py:71` | `_run` | Extract output handling |
| 14 | `_cli.py:164` | `cmd_test_cov` | Extract test configuration |
| 13 | `_cli.py:372` | `main` | Extract command dispatch |
| 13 | `filters/search/options.py:174` | `_coerce_mode_option` | Extract validation branches |

**Key insight:** 8 of 11 violations are in `_cli.py`, which is also untested.
Splitting and testing the CLI module resolves most function length violations.

The worst non-CLI violation is `SqlFilterAdapter.build_condition` (35 lines) — a
`match`/`case` dispatching 14 operators. Refactoring to a strategy dict eliminates it:

```python
# Before: 35-line match/case (static method)
@staticmethod
def build_condition(column, operator, value):
    match operator:
        case "eq" | "equals": return column == value
        case "ne" | "not_equals": return column != value
        # ... 12 more cases

# After: strategy dict
_OPERATORS: ClassVar[dict[str, Callable]] = {
    "eq": lambda col, val: col == val,
    "ne": lambda col, val: col != val,
    # ...
}

@staticmethod
def build_condition(column, operator, value):
    builder = SqlFilterAdapter._OPERATORS.get(operator)
    if not builder:
        raise ValueError(f"Unknown operator: {operator}")
    return builder(column, value)
```

### Page Model Refactoring

> **Smell:** Duplicate Code (`guru-smells` → Dispensables)
> **Technique:** Inline Class (`guru-refactor-moving`) — merge PagedResponse into Page
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010)

**Problem:** `Page[T]` is a frozen dataclass. FastAPI needs `PagedResponse[T]` (Pydantic).
Users must convert between them. Competitors make Page a Pydantic model directly.

**Solution:** Refactor `Page` to be a Pydantic model:

```python
# Before (v0.1.0)
@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    limit: int

# After (v0.1.1)
class Page(BaseModel, Generic[T]):
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

This eliminates `PagedResponse` entirely — `Page[T]` works directly as a FastAPI
`response_model`.

### Protocol Interfaces for Multi-Backend

> **Smell:** Alternative Classes with Different Interfaces (`guru-smells` → OO Abusers)
> **Principle:** Dependency Inversion Principle (`arch-principles`)
> **Technique:** Extract Superclass (`guru-refactor-generalization`) — introduce `PaginationBackend` Protocol
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010), [Architecture Principles](architecture.md#architecture-principles)

**Problem:** Everything is coupled to SQLAlchemy. Adding Tortoise or Beanie later would
require invasive changes.

**Current protocols** (5 exist in `types.py`):

| Protocol | Purpose |
|----------|---------|
| `PageParamsProtocol` | page, limit, offset, model_copy |
| `PageProtocol` | items, total, page, limit |
| `SupportsTotalOrdering` | __lt__, __le__, __gt__, __ge__ |
| `SqlClause` | __and__, __or__ |
| `SqlStringExpression` | in_, like |

**New protocols needed** (to be added in v0.1.1):

```python
from typing import Protocol, TypeVar, Generic, Any

T = TypeVar("T")

class PaginationBackend(Protocol[T]):
    async def count(self, query: Any) -> int: ...
    async def fetch(self, query: Any, offset: int, limit: int) -> list[T]: ...

class FilterBackend(Protocol):
    def apply_filters(self, query: Any, filters: FilterValues) -> Any: ...

class SortBackend(Protocol):
    def apply_sorting(self, query: Any, sorting: SortValues) -> Any: ...
```

SQLAlchemy implementations become adapters implementing these protocols. New backends
(Tortoise, Beanie) implement the same protocols.

### SQL Filter Adapter Operator Gap

> **Smell:** Incomplete Library Class (`guru-smells` → Couplers)
> **Technique:** Introduce Foreign Method (`guru-refactor-moving`)
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010)

**Problem:** The predicate engine has 24 operators, but the SQL adapter only covers 14.

| Operator | Predicate Engine | SQL Adapter | Gap |
|----------|-----------------|-------------|-----|
| `eq` / `equals` | ✓ | ✓ | — |
| `ne` / `not_equals` | ✓ | ✓ | — |
| `gt` / `greater_than` | ✓ | ✓ | — |
| `gte` / `greater_than_or_equal` | ✓ | ✓ | — |
| `lt` / `less_than` | ✓ | ✓ | — |
| `lte` / `less_than_or_equal` | ✓ | ✓ | — |
| `in` | ✓ | ✓ | — |
| `not_in` / `notin` | ✓ | ✓ | — |
| `like` | ✓ | ✓ | — |
| `ilike` | ✓ | ✓ | — |
| `is_null` | ✓ | ✓ | — |
| `contains` | ✓ | ✓ | — |
| `startswith` | ✓ | ✓ | — |
| `endswith` | ✓ | ✓ | — |
| `between` | ✓ | ✗ | **Add** |
| `range` | ✓ | ✗ | **Add** |
| `icontains` | ✓ | ✗ | **Add** |
| `istartswith` | ✓ | ✗ | **Add** |
| `iendswith` | ✓ | ✗ | **Add** |
| `regex` | ✓ | ✗ | **Add** (PostgreSQL `~`) |
| `iregex` | ✓ | ✗ | **Add** (PostgreSQL `~*`) |
| `is_not_null` | ✓ | ✗ | **Add** |
| `empty` | ✓ | ✗ | **Add** |
| `not_empty` | ✓ | ✗ | **Add** |

**10 operators** need SQL adapter implementations.

### Untested Modules

> **Smell:** No smell category — this is a quality gate issue
> **Technique:** Write tests (no guru-refactor technique applies)
> **Reference:** [Architecture Principles](architecture.md#architecture-principles)

**Problem:** 8 of 42 non-init source modules have no corresponding test coverage.

| Module | Lines | Priority | Risk |
|--------|-------|----------|------|
| `_cli.py` | 390 | **Critical** | Contains 8 of 11 function length violations; will break during refactoring without tests |
| `query/async_api.py` | 289 | **High** | Core async pagination API — used by every SQLAlchemy consumer |
| `query/execution/async_executor.py` | ~120 | **High** | Async execution engine — critical path |
| `filters/search/sql_search.py` | ~100 | **High** | SQL search service — no test validates SQL generation |
| `filters/search/strategies.py` | ~80 | **Medium** | Search strategy selection |
| `filters/search/conditions.py` | ~90 | **Medium** | SQL condition building for search |
| `filters/search/factories.py` | ~60 | **Medium** | Search service factory functions |
| `database/types.py` | ~30 | **Low** | Type definitions only |

**Note:** `_cli.py` is also excluded from coverage measurement in `pyproject.toml`.
It should be included once tests exist.

### Dead Code Detection

> **Smell:** Dead Code (`guru-smells` → Dispensables) — INVESTIGATION NEEDED
> **Technique:** Run `vulture` dead-code detection, then remove confirmed dead code
> **Reference:** [Code Smell Reference](architecture.md#code-smell-reference-v010)

**Problem:** 8 untested modules may contain unreachable code paths. Without test
coverage, dead code cannot be detected with confidence.

**Action:**

1. Add test coverage for untested modules (see above)
2. Run `vulture` dead-code analysis on the entire codebase
3. Flag and remove confirmed dead code
4. Add `vulture` to the CI quality gate to prevent future dead code accumulation

### Other Cleanup

| Task | Details |
|------|---------|
| Flatten module nesting | Reduce 5-level nesting in `filters/predicates/operators/` |
| Define public API | Audit `__init__.py` exports across all modules |
| Add `__all__` to subpackages | Several subpackages export without explicit `__all__` |

### Checklist

- [ ] Zero boolean parameters in public API
- [ ] All files under 200 lines
- [ ] All functions under 12 lines
- [ ] No French comments
- [ ] Page is a Pydantic model (eliminates PagedResponse)
- [ ] 3 new Protocol interfaces (PaginationBackend, FilterBackend, SortBackend)
- [ ] SqlPaginator + MemoryPaginator share PaginationBackend Protocol
- [ ] 10 missing SQL adapter operators implemented
- [ ] Tests for all 8 previously untested modules
- [ ] `_cli.py` included in coverage measurement
- [ ] `vulture` dead-code scan run; confirmed dead code removed
- [ ] All quality checks pass (`ruff format`, `ruff check`, `mypy`, `pytest`)
- [ ] All 14 code smells from [Code Smell Reference](architecture.md#code-smell-reference-v010) addressed

---

## v0.2.0 — Declarative FastAPI Integration

**Focus:** Close the critical gap with competitors.

This is the most important release. Without declarative filtering, pypaginate cannot
compete with fastapi-filter or fastapi-filters for real-world FastAPI applications.

### FilterModel

Pydantic-based declarative filter definitions:

```python
from pypaginate.integrations.fastapi import FilterModel, FilterField

class UserFilter(FilterModel):
    name: str | None = FilterField(None, operator="ilike")
    age__gte: int | None = None
    age__lte: int | None = None
    email: str | None = FilterField(None, operator="eq")
    is_active: Literal[True, False] | None = None

    class Config:
        model = User
        search_fields = ["name", "email", "bio"]
```

**Design decisions:**

- Support **both** query param formats: `?name__ilike=john` (Django `__` style) and
  `?name[ilike]=john` (bracket style), configurable per-app
- Auto-detect operators from field type (str → ilike, int → eq, optional → is_null)
  as an opt-in feature
- Pydantic validation on all filter values
- Full OpenAPI schema generation (all filters visible in Swagger)

**Borrowed from competitors:**
- FilterModel concept from fastapi-filter's `BaseFilterModel`
- FilterSet composability (`subset()`, `extract()`) from fastapi-filters
- `CSVList` type for multi-value query params from fastapi-filters
- `extra="forbid"` strict validation from fastapi-filter

### FilterDepends

FastAPI dependency that auto-parses query parameters:

```python
from pypaginate.integrations.fastapi import FilterDepends

@app.get("/users", response_model=Page[UserSchema])
async def get_users(
    filters: UserFilter = FilterDepends(UserFilter),
):
    stmt = filters.apply(select(User))
    return await paginate(session, stmt)
```

### create_filters() — Functional API

For quick, model-less filter creation:

```python
from pypaginate.integrations.fastapi import create_filters

# No model class needed
user_filters = create_filters(
    name=str,      # Auto: ilike for strings
    age=int,       # Auto: eq for integers
    is_active=bool,
)

@app.get("/users")
async def get_users(filters=Depends(user_filters)):
    stmt = apply_filters(select(User), filters)
    ...
```

### OrderingDepends

Declarative sorting with standard `+`/`-` prefix:

```python
from pypaginate.integrations.fastapi import OrderingDepends, OrderingParams

@app.get("/users")
async def get_users(
    ordering: OrderingParams = OrderingDepends(
        fields=["name", "created_at", "age"],
        default=["-created_at"],
    ),
):
    stmt = ordering.apply(select(User))
    ...

# URL: /users?order_by=-created_at,name
```

Features:

- Multi-field sorting (comma-separated)
- Direction prefix (`+` asc, `-` desc)
- Null positioning (configurable)
- Field validation (only allowed fields)

### SearchDepends

Integrate pypaginate's advanced search into FastAPI:

```python
from pypaginate.integrations.fastapi import SearchDepends

@app.get("/users")
async def get_users(
    search: str | None = SearchDepends(
        fields=["name", "email", "bio"],
        fuzzy=SearchMode.FUZZY,
        min_similarity=0.7,
    ),
):
    if search:
        stmt = search_service.apply(stmt, search)
    ...

# URL: /users?search=john+doe
```

### Auto SQL WHERE Generation

FilterModel produces SQLAlchemy conditions directly:

```python
# Method 1: Apply to statement
stmt = filters.apply(select(User))

# Method 2: Get conditions list
conditions = filters.to_conditions()
stmt = select(User).where(*conditions)

# Method 3: Get as dict (for logging/debugging)
active_filters = filters.active_values()
# {"name__ilike": "%john%", "age__gte": 25}
```

### Expected Impact

| Metric | Before (v0.1) | After (v0.2) |
|--------|---------------|--------------|
| Lines per endpoint | ~25 | ~15 |
| Manual filter code | Required | Eliminated |
| OpenAPI completeness | Partial | Full |
| Filter validation | None | Automatic |
| Weighted feature score | 50% | 79% |

### Checklist

- [ ] FilterModel with Pydantic validation
- [ ] FilterDepends as FastAPI dependency
- [ ] create_filters() functional API
- [ ] OrderingDepends with +/- prefix and null positioning
- [ ] SearchDepends integrating existing search engine
- [ ] Both `__` and `[]` query param formats
- [ ] CSVList type for multi-value params
- [ ] FilterSet composability (subset, extract)
- [ ] Auto OpenAPI generation for all filter/sort/search params
- [ ] apply() method for SQLAlchemy statements
- [ ] Comprehensive tests (unit + integration + e2e with FastAPI TestClient)
- [ ] Documentation with examples
- [ ] Migration guide from manual filtering

---

## v0.3.0 — Pagination Formats & Auto-Setup

**Focus:** Multiple pagination styles and zero-configuration setup.

### Alternative Page Formats

```python
from pypaginate import Page, LimitOffsetPage, CursorPage

# Standard page/size (existing)
@app.get("/users", response_model=Page[User])
async def get_users(): ...

# Limit/Offset style
@app.get("/users", response_model=LimitOffsetPage[User])
async def get_users(): ...

# Cursor-based (base64 tokens)
@app.get("/users", response_model=CursorPage[User])
async def get_users(): ...
```

### add_pagination(app)

Zero-configuration auto-setup:

```python
from pypaginate.integrations.fastapi import add_pagination

app = FastAPI()
add_pagination(app)

# Automatically:
# - Detects routes returning Page[T]
# - Injects pagination params as dependencies
# - Configures response models
```

### CustomizedPage

Composable page customizers (inspired by fastapi-pagination's 22 customizers):

```python
from pypaginate import Page
from pypaginate.customization import UseIncludeTotal, UseFieldAlias

# Page without total count (faster queries)
FastPage = CustomizedPage[Page, UseIncludeTotal(False)]

# Page with custom field names
ApiPage = CustomizedPage[Page, UseFieldAlias(items="data", total="count")]
```

### Items Transformer

Post-pagination item transformation pipeline:

```python
from pypaginate import Page

@app.get("/users", response_model=Page[UserSchema])
async def get_users():
    return await paginate(
        session, stmt, params,
        transformer=lambda items: [UserSchema.from_orm(u) for u in items],
    )
```

### HATEOAS Links

```python
from pypaginate import PageWithLinks

@app.get("/users", response_model=PageWithLinks[User])
async def get_users(): ...

# Response includes:
# {
#   "items": [...],
#   "total": 100,
#   "links": {
#     "first": "/users?page=1&limit=20",
#     "prev": "/users?page=1&limit=20",
#     "next": "/users?page=3&limit=20",
#     "last": "/users?page=5&limit=20"
#   }
# }
```

Plus RFC 8288 `Link` HTTP headers for REST clients.

### ContextVars

Thread-safe request/response lifecycle management:

```python
from pypaginate.context import pagination_ctx

# Access current pagination params anywhere in the call stack
params = pagination_ctx.get_params()
request = pagination_ctx.get_request()
```

### Checklist

- [ ] LimitOffsetPage with limit/offset params
- [ ] CursorPage with base64 token encoding
- [ ] add_pagination(app) auto-setup
- [ ] CustomizedPage with composable customizers
- [ ] Items Transformer pipeline
- [ ] PageWithLinks (HATEOAS — body + RFC 8288 headers)
- [ ] ContextVars for request lifecycle
- [ ] All formats work with FilterDepends/OrderingDepends

---

## v0.4.0 — Multi-Backend & Advanced Features

**Focus:** Backend diversity and advanced filtering.

### Additional Backends

Using the Protocol interfaces defined in v0.1.1:

| Backend | ORM | Priority |
|---------|-----|----------|
| `ext.tortoise` | Tortoise ORM | High |
| `ext.beanie` | Beanie (MongoDB) | High |
| `ext.motor` | Motor (async MongoDB) | Medium |
| `ext.django` | Django ORM | Medium |

```python
# Backend-specific extensions
from pypaginate.ext.tortoise import paginate, apply_filters
from pypaginate.ext.beanie import paginate, apply_filters

# Same FilterModel works across backends
class UserFilter(FilterModel):
    name: str | None = FilterField(None, operator="ilike")
```

### Related/JOIN Filters

Auto-join on relationship paths:

```python
class UserFilter(FilterModel):
    name: str | None = FilterField(None, operator="ilike")
    posts__title: str | None = FilterField(None, operator="ilike")    # Auto JOIN
    posts__tags__name: str | None = FilterField(None, operator="eq")  # Multi-level

    class Config:
        model = User
```

### Operator Auto-Detection

Automatically assign operators based on field type:

```python
class UserFilter(FilterModel):
    name: str | None = None      # Auto: ilike (string field)
    age: int | None = None       # Auto: eq (numeric field)
    score: float | None = None   # Auto: eq (numeric field)
    is_active: bool | None = None  # Auto: eq (boolean field)

    class Config:
        model = User
        auto_operators = True
```

### ORM Auto-Filters

Generate filter classes from ORM models automatically:

```python
from pypaginate.integrations.fastapi import create_filters_from_orm

# Auto-generates FilterModel from SQLAlchemy model
UserFilter = create_filters_from_orm(User, exclude=["password_hash"])
```

### Count Query Caching

TTL-based caching for expensive count queries:

```python
from pypaginate import Page, PaginationConfig

config = PaginationConfig(
    count_cache_ttl=60,  # Cache count for 60 seconds
    count_cache_backend="redis",
)
```

### Advanced SQL Operators

```python
class ProductFilter(FilterModel):
    price__between: tuple[float, float] | None = None
    tags__contains: list[str] | None = None       # Array contains
    tags__overlap: list[str] | None = None         # Array overlap
    metadata__jsonpath: str | None = None           # JSONB path query
```

### Checklist

- [ ] Tortoise ORM backend
- [ ] Beanie (MongoDB) backend
- [ ] Related/JOIN filter resolution
- [ ] Operator auto-detection
- [ ] ORM auto-filter generation (`create_filters_from_orm()`)
- [ ] Count query caching
- [ ] Advanced SQL operators (between, array, JSONB)
- [ ] Field remapping and custom filter hooks
- [ ] Backend-specific optimizations

---

## v1.0.0 — Production Ready

**Focus:** Stability, documentation, and confidence.

### API Stability Guarantee

No breaking changes after v1.0.0. Deprecation cycle for any future changes:
warn in 1.x, remove in 2.0.

### Quality Gates

| Gate | Target |
|------|--------|
| Test coverage | >95% |
| All public APIs documented | 100% |
| Security audit (bandit) | Zero high/critical |
| Performance benchmarks | Published baselines |
| Type coverage (mypy) | 100% strict |
| Zero boolean params | Enforced |
| All files under 200 lines | Enforced |

### Documentation

- Complete API reference (sphinx-autoapi)
- Getting started tutorial
- Migration guides (from fastapi-pagination, fastapi-filter)
- Cookbook with real-world examples
- Architecture guide for contributors

### Checklist

- [ ] API frozen (no breaking changes)
- [ ] >95% test coverage
- [ ] Complete documentation
- [ ] Security audit passed
- [ ] Performance benchmarks published
- [ ] Migration guides written
- [ ] Real-world examples for common patterns
- [ ] Changelog for all versions

---

## Current Strengths

Features where pypaginate already leads or matches competitors:

| Strength | Status | Competitor equivalent |
|----------|--------|---------------------|
| Advanced search (RapidFuzz fuzzy) | Shipped | None |
| JSON Logic filter expressions | Shipped | None |
| 24 in-memory predicate operators | Shipped | None match breadth |
| Text normalization (UTF-8, ASCII) | Shipped | None |
| Accent-insensitive search | Shipped | None |
| In-memory pagination | Shipped | fastapi-pagination |
| In-memory filter engine | Shipped | None |
| Strict mypy compliance | Shipped | None match strictness |
| Google-style docstrings | Shipped | Competitors have none |

---

## Contributing

Priority areas for contributions:

### Immediate (v0.1.1)

1. Boolean parameter elimination — pick a module, refactor its booleans
2. File splitting — take a 300+ line file and decompose it
3. Test coverage — write tests for `_cli.py`, `async_api.py`, or search modules
4. French comment translation — simple find-and-replace across 5 files
5. SQL adapter operators — add missing operators (start with `between`, `is_not_null`)

### High Impact (v0.2.0)

6. FilterModel implementation — core declarative filter system
7. FastAPI integration — FilterDepends, OrderingDepends
8. OpenAPI generation — auto-schema for filter params

See the [Contributing Guide](index.md) to get started.
