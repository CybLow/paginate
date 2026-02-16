# Comparative Analysis

pypaginate vs the FastAPI pagination ecosystem — an honest assessment.

## The Ecosystem

Three libraries dominate FastAPI pagination and filtering:

| Library | Author | Stars | Downloads/month | Version | Focus |
|---------|--------|-------|-----------------|---------|-------|
| [fastapi-pagination](https://github.com/uriyyo/fastapi-pagination) | Yurii Karabas | 1,619 | 3.4M | 0.15.10 | Pagination |
| [fastapi-filters](https://github.com/uriyyo/fastapi-filters) | Yurii Karabas | 90 | New | 0.3.1 | Filtering + sorting |
| [fastapi-filter](https://github.com/arthurio/fastapi-filter) | Arthur Rio | 302 | Moderate | 2.0.1 | Filtering + search |

**Key insight**: `fastapi-pagination` and `fastapi-filters` share the **same author** and
are designed to work together as a unified ecosystem.

pypaginate aims to provide **all of this in one library** — pagination, filtering, search,
and sorting — with superior architecture and unique advanced features.

---

## Feature Comparison

### Pagination

| Feature | fastapi-pagination | pypaginate v0.1 | Status |
|---------|-------------------|-----------------|--------|
| Offset (page/size) | `Page[T]`, `Params` | `Page[T]`, `PageParams` | Equivalent |
| Limit/Offset | `LimitOffsetPage[T]` | — | Planned v0.3.0 |
| Cursor-based | `CursorPage[T]` (base64 tokens) | `KeysetPageParams` (via sqlakeyset) | Partial |
| In-memory | `paginate(sequence)` | `MemoryPaginator` | Equivalent |
| `add_pagination(app)` | Auto-detects Page returns | — | Planned v0.3.0 |
| Composable customizers | **22** via `CustomizedPage` | — | Planned v0.3.0 |
| Items Transformer | Post-paginate item transformation | — | Planned v0.3.0 |
| HATEOAS links | Body links + RFC 8288 headers | — | Planned v0.3.0 |
| Page variants | Optional, Iterable, Link pages | — | Planned v0.3.0 |
| Response model | Page IS a Pydantic model | `PagedResponse` wrapper | Refactoring in v0.1.1 |
| Async support | Full (generator-based flow) | Full (async functions) | Equivalent |
| DB backends | **19** (SQLAlchemy, Beanie, Tortoise, Motor, Django, Elasticsearch...) | SQLAlchemy only | Planned v0.4.0 |

### Filtering

| Feature | fastapi-filter | fastapi-filters | pypaginate v0.1 | Status |
|---------|---------------|----------------|-----------------|--------|
| Declarative FilterModel | `BaseFilterModel` (Pydantic) | `FilterSet` (metaclass) | — | Planned v0.2.0 |
| FilterDepends | `FilterDepends(MyFilter)` | `create_filters(name=str)` | — | Planned v0.2.0 |
| Auto SQL WHERE | `.filter(query)` | `apply_filters(stmt)` | Manual via `SqlFilterAdapter` | Planned v0.2.0 |
| Query param format | `?name__ilike=john` (Django `__`) | `?name[eq]=john` (bracket) | No standard format | Both planned |
| Operators (SQL) | 12 | 17 | 14 (+ 6 aliases) | Partial |
| Operators (in-memory) | — | — | 24 (JSON Logic) | **pypaginate** |
| Auto operator detection | No | Yes (str→like, int→gt/lt) | No | Planned v0.4.0 |
| Related/JOIN filters | `with_prefix()` | Not yet | — | Planned v0.4.0 |
| Pydantic validation | Full (`extra="forbid"`) | Via Query params | — | Planned v0.2.0 |
| OpenAPI auto-generation | Full | Full | — | Planned v0.2.0 |
| Filter composability | — | `subset()`, `extract()`, `from_ops()` | — | Planned v0.2.0 |
| ORM auto-filters | — | `create_filters_from_orm()` | — | Planned v0.4.0 |

### Search

| Feature | fastapi-filter | fastapi-filters | pypaginate v0.1 | Winner |
|---------|---------------|----------------|-----------------|--------|
| Basic search field | `search` + `search_model_fields` | Not yet | `SqlSearchService` | pypaginate |
| Fuzzy matching | No | No | RapidFuzz integration | **pypaginate** |
| Token parsing | No | No | AND/OR/FUZZY modes | **pypaginate** |
| Text normalization | No | No | UTF-8, ASCII transliteration | **pypaginate** |
| Accent-insensitive | No | No | PostgreSQL unaccent | **pypaginate** |
| In-memory search | No | No | `MemorySearchEngine` | **pypaginate** |

### Sorting

| Feature | fastapi-filter | fastapi-filters | pypaginate v0.1 | Status |
|---------|---------------|----------------|-----------------|--------|
| Declarative sorting | `order_by` field | `create_sorting()` | `SortEngine` (no FastAPI) | Planned v0.2.0 |
| Direction prefix | `+`/`-` prefix | `+`/`-` prefix | No standard format | Planned v0.2.0 |
| Null positioning | No | `bigger`/`smaller` (`SortingNulls`) | In SortEngine (no FastAPI) | Partial |
| Multi-field sort | Comma-separated | Multiple params | Manual | Planned v0.2.0 |
| Natural ordering | No | No | Yes | **pypaginate** |

### Code Quality

| Metric | fastapi-pagination | fastapi-filters | pypaginate v0.1 |
|--------|-------------------|-----------------|-----------------|
| Type hints | Extensive + `@overload` | Extensive + Protocol | Extensive + mypy strict |
| Docstrings | **None** | Minimal | Google-style |
| `py.typed` (PEP 561) | Yes | Yes | Yes |
| Ruff rules | ALL | ALL | Selected |
| Boolean params | Some | Few | **52 instances** (violations) |
| Pydantic v1+v2 | Full compat layer | v2 only | v2 only |
| Python minimum | 3.10 | 3.10 | 3.11 |

---

## Competitor Deep Dives

Understanding *why* competitors succeed helps us build something better.

### fastapi-pagination: Architecture Innovations

**Generator-based "flow" pattern** — the core innovation that unifies sync and async
through the same code path:

```python
# Generators yield values; runners handle sync/async transparently
def generic_flow():
    total = yield count_flow()
    items = yield items_flow()
    return total, items
```

pypaginate uses explicit async functions — clearer, but lacks sync/async unification.

**22 Composable customizers** via `CustomizedPage[Page, *Customizers]`:
Page customizers use `__class_getitem__` to compose behaviors at the type level.
This enables patterns like `CustomizedPage[Page, UseIncludeTotal(False)]` to create
page types without total count (faster queries).

**Items Transformer system** — post-pagination transformation of items before they
reach the response. Enables lazy loading of related objects, DTO conversion, or
enrichment *after* the database query is paginated.

**ContextVar-based API** — `add_pagination(app)` injects pagination params via
`ContextVar` at the middleware level. Routes just return `paginate(query)` with no
explicit parameter passing. This is why their endpoint code is so minimal.

**19 Database backend extensions** — each backend is a separate package:
`fastapi-pagination[sqlalchemy]`, `[beanie]`, `[tortoise]`, `[motor]`, `[django]`,
`[mongoengine]`, `[bunnet]`, `[ormar]`, `[piccolo]`, `[elasticsearch]`, `[pony]`,
`[databases]`, `[scylla]`, `[gino]`, `[sqlmodel]`, etc.

**RFC 8288 Link headers** — the `links/` subpackage generates both in-body link
objects AND proper HTTP `Link` headers per RFC 8288.

### fastapi-filters: Architecture Innovations

**FilterOpBuilder** — Python operator overloading for filter construction:

```python
# Operators map to filter operations
User.name == "john"       # eq
User.age > 18             # gt
User.tags >> ["python"]   # in_  (right shift = "in")
```

**ConfigVar system** — `ContextVar`-based configuration with `.dependency()` method
that returns a zero-arg FastAPI dependency. This eliminates the need to pass
configuration through every function call.

**CSVList Pydantic type** — custom type that parses `?tags=a,b,c` into `["a", "b", "c"]`
automatically. Handles multi-value query parameters that FastAPI's default Query doesn't.

**FilterSet composability** — `subset()` creates a filtered version of a FilterSet
with fewer fields. `extract()` extracts specific fields. `from_ops()` creates a
FilterSet from operator builders. All return new FilterSet classes.

**`create_filters_from_orm()` — auto-generates filter classes from SQLAlchemy models.
Field remapping via `additional` namespace and custom filter hooks allow overriding
auto-detected behavior.

**SortingNulls** — configurable null positioning (`"bigger"` = nulls last for ASC,
`"smaller"` = nulls first for ASC) that works across databases.

### fastapi-filter: Architecture Innovations

**`with_prefix()` for nested relationship filters** — enables filtering across
SQLAlchemy relationships without manual JOIN code:

```python
class AddressFilter(BaseFilterModel):
    city__ilike: str | None = None

class UserFilter(BaseFilterModel):
    name__ilike: str | None = None
    address: AddressFilter | None = FilterDepends(
        with_prefix("address", AddressFilter)
    )
```

**`extra="forbid"` validation** — Pydantic strict mode rejects unknown query parameters.
Prevents users from passing unsupported filter fields silently.

**Multi-model search** — `search_model_fields` defines which model fields to search
across. A single `?search=john` parameter generates `OR` conditions across all
specified fields using `ilike`.

**MongoEngine backend** — uses MongoDB Q objects for filter generation, proving the
filter model abstraction works across ORMs.

---

## Side-by-Side: Complete Endpoint

### With fastapi-pagination + fastapi-filter

```python
from fastapi import FastAPI
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_filter import FilterDepends

app = FastAPI()
add_pagination(app)

class UserFilter(BaseFilterModel):
    name__ilike: str | None = None
    age__gte: int | None = None
    order_by: list[str] = ["created_at"]

    class Constants(BaseFilterModel.Constants):
        model = User
        search_model_fields = ["name", "email"]

@app.get("/users", response_model=Page[UserSchema])
async def get_users(
    user_filter: UserFilter = FilterDepends(UserFilter),
):
    query = user_filter.filter(select(User))
    query = user_filter.sort(query)
    return await paginate(query)

# URL: /users?page=2&size=20&name__ilike=%john%&age__gte=25&order_by=-created_at
```

**Lines of endpoint code: ~15**

### With pypaginate v0.1.0

```python
from fastapi import FastAPI, Depends, Query
from pypaginate import PageParams, paginate_entities
from pypaginate.integrations.fastapi import get_pagination_params, PagedResponse

app = FastAPI()

@app.get("/users", response_model=PagedResponse[UserSchema])
async def get_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    name: str | None = Query(None, description="Filter by name"),
    min_age: int | None = Query(None, description="Minimum age"),
    sort_by: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="Sort direction"),
):
    stmt = select(User)

    if name:
        stmt = stmt.where(User.name.ilike(f"%{name}%"))  # ⚠ See security note below
    if min_age:
        stmt = stmt.where(User.age >= min_age)

    sort_col = getattr(User, sort_by, User.created_at)  # ⚠ See security note below
    stmt = stmt.order_by(sort_col.desc() if order == "desc" else sort_col)

    return await paginate_entities(session, stmt, params)

# URL: /users?page=2&limit=20&name=john&min_age=25&sort_by=created_at&order=desc
```

**Lines of endpoint code: ~25** (67% more code, no validation, no auto-OpenAPI)

```{admonition} Security Issues in Manual Filtering
:class: danger

The v0.1.0 manual approach above has two security vulnerabilities:

1. **LIKE wildcard injection** (line `f"%{name}%"`): User input is interpolated
   directly into a LIKE pattern. An attacker can pass `%` or `_` wildcards to
   manipulate query results (e.g., `name=___` matches any 3-character name).
   **Mitigation:** Escape `%` and `_` in user input before interpolation.

2. **Arbitrary attribute access** (line `getattr(User, sort_by, ...)`): User input
   selects any model attribute, including private or relationship attributes.
   **Mitigation:** Validate `sort_by` against an explicit allowlist of fields.

Both issues are eliminated in v0.2.0's `FilterDepends` and `OrderingDepends`, which
validate fields against a declared allowlist and escape filter values automatically.
```

### With pypaginate v0.2.0 (planned)

```python
from fastapi import FastAPI, Depends
from pypaginate import Page, PageParams
from pypaginate.integrations.fastapi import (
    FilterDepends, OrderingDepends, SearchDepends, get_pagination_params,
)

app = FastAPI()

class UserFilter(FilterModel):
    name: str | None = FilterField(None, operator="ilike")
    age__gte: int | None = None
    age__lte: int | None = None

    class Config:
        model = User

@app.get("/users", response_model=Page[UserSchema])
async def get_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    filters: UserFilter = FilterDepends(UserFilter),
    ordering: OrderingParams = OrderingDepends(["name", "created_at", "age"]),
    search: str | None = SearchDepends(["name", "email"]),
):
    stmt = select(User)
    stmt = filters.apply(stmt)
    stmt = ordering.apply(stmt)
    if search:
        stmt = search_service.apply(stmt, search)
    return await paginate_entities(session, stmt, params)

# URL: /users?page=2&limit=20&name__ilike=%john%&age__gte=25&order_by=-created_at&search=john
```

**Lines of endpoint code: ~15** — on par with the competition, plus integrated search.

---

## Weighted Score

Features weighted by importance to production FastAPI applications:

| Feature | Weight | fastapi-pagination + filters | pypaginate v0.1 | v0.2.0 target | v0.4.0 target |
|---------|--------|------------------------------|-----------------|---------------|---------------|
| Basic pagination | 10 | 10 | 10 | 10 | 10 |
| Declarative filtering | **15** | 15 | **0** | 15 | 15 |
| OpenAPI auto-generation | **10** | 10 | **2** | 10 | 10 |
| Multiple formats | 8 | 8 | 3 | 3 | 8 |
| Sorting integration | 7 | 7 | 3 | 7 | 7 |
| Multi-backend | 7 | 7 | 2 | 2 | 7 |
| Cursor pagination | 6 | 6 | 3 | 3 | 6 |
| HATEOAS links | 4 | 4 | 0 | 0 | 4 |
| Customization | 5 | 5 | 1 | 2 | 5 |
| Full-text search | 8 | 2 | **8** | **8** | **8** |
| Fuzzy matching | 5 | 0 | **5** | **5** | **5** |
| JSON Logic filters | 5 | 0 | **5** | **5** | **5** |
| Text normalization | 3 | 0 | **3** | **3** | **3** |
| Type safety | 5 | 4 | **5** | **5** | **5** |
| Documentation | 7 | 6 | 3 | 5 | 7 |
| **Total** | **105** | **84 (80%)** | **53 (50%)** | **83 (79%)** | **105 (100%)** |

**Trajectory:**

- **v0.1.0** (current): 50% — strong foundations, critical integration gaps
- **v0.2.0**: 79% — declarative filtering closes the biggest gap
- **v0.3.0** (+ pagination formats, HATEOAS, customizers): ~92%
- **v0.4.0** (+ multi-backend, advanced features): 100% — full ecosystem parity and beyond

---

## Where pypaginate Wins

### 1. Unified Library

One install, one import namespace. No coordinating versions between pagination and filter
libraries:

```python
# Competitors: two libraries, two authors, version coordination
pip install fastapi-pagination fastapi-filter

# pypaginate: everything in one
pip install pypaginate[fastapi]
```

### 2. Advanced Search (Unique)

No competitor offers fuzzy matching, token parsing, or text normalization:

```python
from pypaginate.filters.search import SqlSearchService
from pypaginate.filters.search.options import SearchOptions

service = SqlSearchService(
    search_fields=["name", "email", "bio"],
    options=SearchOptions(
        fuzzy=True,
        min_similarity=0.7,
        accent_sensitive=False,
    ),
)
```

### 3. JSON Logic for Complex Filters (Unique)

Nested AND/OR expressions that competitors cannot express:

```python
from pypaginate.filters.predicates import FilterEngine

filters = {
    "and": [
        {"age": {"gte": 18}},
        {"or": [
            {"country": {"eq": "FR"}},
            {"country": {"eq": "BE"}},
        ]},
    ],
}

engine = FilterEngine()
results = engine.apply(items, filters)
```

### 4. Operator Depth

pypaginate's in-memory predicate engine has **24 operators** — more than any competitor:

| Category | Operators |
|----------|-----------|
| Equality | `eq`, `ne` |
| Ordering | `gt`, `gte`, `lt`, `lte` |
| Membership | `in`, `not_in` (alias: `notin`) |
| Range | `between`, `range` |
| Text (case-sensitive) | `contains`, `startswith`, `endswith` |
| Text (case-insensitive) | `icontains`, `istartswith`, `iendswith` |
| Pattern matching | `like`, `ilike`, `regex`, `iregex` |
| Nullity | `is_null`, `is_not_null` |
| Emptiness | `empty`, `not_empty` |

The SQL adapter currently covers 14 of these; the gap is being closed in v0.1.1.

### 5. Strict Type Safety

pypaginate is the only library in this space with `mypy --strict` compliance and
comprehensive Google-style docstrings.

### 6. Protocol-Based Architecture (In Progress)

Backend-agnostic design via Python Protocols, following the **Dependency Inversion Principle** —
add SQLAlchemy, Tortoise, Beanie, or custom backends without modifying core code.
Five protocols already defined; backend protocols coming in v0.1.1.

---

## Where pypaginate Lags

### 1. No Declarative FastAPI Integration (Critical — severity: BLOCKING)

The biggest gap. Users must write manual filtering, sorting, and parameter handling code.
**This is the #1 reason to choose competitors today.**

What we're missing that competitors have:
- `FilterDepends()` — auto-parse query params into filter objects
- `FilterModel` / `FilterSet` — declarative filter field definitions
- Auto OpenAPI schema generation for filter parameters
- `add_pagination(app)` — zero-configuration middleware injection

### 2. Single Backend (severity: HIGH)

Only SQLAlchemy is supported. Competitors support 3–19 backends.

### 3. One Pagination Format (severity: MEDIUM)

No `LimitOffsetPage` or `CursorPage` with standardized token format. Only basic
`Page[T]` with offset pagination.

### 4. No Auto-Setup (severity: MEDIUM)

No `add_pagination(app)` equivalent for zero-configuration integration. No ContextVar
lifecycle management for request-scoped pagination state.

### 5. No Items Transformer (severity: LOW)

No post-pagination transformation pipeline. Users must transform items manually
before returning from the endpoint.

### 6. Internal Quality Issues (severity: MEDIUM — being fixed in v0.1.1)

52 boolean parameter instances, 11 files exceeding size limits, 11 functions exceeding
line limits, and 8 untested modules undermine the "superior architecture" claim.
These are being systematically addressed in v0.1.1.

---

## What Competitors Have That We Don't (Yet)

A complete inventory of competitor features with no pypaginate equivalent today:

| Feature | Library | Priority | Planned |
|---------|---------|----------|---------|
| `FilterDepends()` | Both filters | Critical | v0.2.0 |
| Declarative FilterModel/FilterSet | Both filters | Critical | v0.2.0 |
| Auto OpenAPI for filters | Both filters | Critical | v0.2.0 |
| `add_pagination(app)` | fastapi-pagination | High | v0.3.0 |
| ContextVar lifecycle management | Both | High | v0.3.0 |
| `LimitOffsetPage[T]` | fastapi-pagination | High | v0.3.0 |
| `CursorPage[T]` (base64 tokens) | fastapi-pagination | High | v0.3.0 |
| Items Transformer | fastapi-pagination | Medium | v0.3.0 |
| 22 composable `CustomizedPage` | fastapi-pagination | Medium | v0.3.0 |
| RFC 8288 Link headers | fastapi-pagination | Medium | v0.3.0 |
| `FilterOpBuilder` (operator overloading) | fastapi-filters | Medium | v0.2.0 |
| `CSVList` (multi-value query params) | fastapi-filters | Medium | v0.2.0 |
| `create_filters_from_orm()` | fastapi-filters | Medium | v0.4.0 |
| Field remapping (`additional`) | fastapi-filters | Low | v0.4.0 |
| `with_prefix()` for JOINs | fastapi-filter | Medium | v0.4.0 |
| MongoEngine Q objects | fastapi-filter | Low | v0.4.0 |
| 19 database backends | fastapi-pagination | Medium | v0.4.0 |

---

## Migration Path

### From fastapi-pagination + fastapi-filter to pypaginate

Once v0.2.0 ships, migration follows these patterns:

#### Import Changes

```python
# Before (fastapi-pagination)
from fastapi_pagination import Page, Params, add_pagination, paginate
from fastapi_pagination.cursor import CursorPage

# After (pypaginate v0.2.0)
from pypaginate import Page, PageParams
from pypaginate.integrations.fastapi import get_pagination_params
```

```python
# Before (fastapi-filter)
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter as BaseFilterModel

# After (pypaginate v0.2.0)
from pypaginate.integrations.fastapi import FilterDepends, FilterModel
```

#### FilterModel Migration

```python
# Before (fastapi-filter)
class UserFilter(BaseFilterModel):
    name__ilike: str | None = None
    age__gte: int | None = None
    order_by: list[str] = ["created_at"]

    class Constants(BaseFilterModel.Constants):
        model = User
        search_model_fields = ["name", "email"]

# After (pypaginate v0.2.0)
class UserFilter(FilterModel):
    name: str | None = FilterField(None, operator="ilike")
    age__gte: int | None = None

    class Config:
        model = User
        search_fields = ["name", "email"]
```

#### Endpoint Migration

```python
# Before
@app.get("/users", response_model=Page[UserSchema])
async def get_users(filters: UserFilter = FilterDepends(UserFilter)):
    query = filters.filter(select(User))
    query = filters.sort(query)
    return await paginate(query)

# After (pypaginate v0.2.0) — nearly identical API surface
@app.get("/users", response_model=Page[UserSchema])
async def get_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    filters: UserFilter = FilterDepends(UserFilter),
    ordering: OrderingParams = OrderingDepends(["name", "created_at"]),
):
    stmt = filters.apply(select(User))
    stmt = ordering.apply(stmt)
    return await paginate_entities(session, stmt, params)
```

The API surface is intentionally similar to minimize migration effort.

---

## Conclusion

pypaginate at v0.1.0 has **strong foundations** — advanced search, JSON Logic, strict type
safety — but **critical gaps** in FastAPI integration that make competitors the better
choice for production use today.

The [roadmap](contributing/roadmap.md) addresses these gaps systematically:

- **v0.1.1**: Fix architecture issues (boolean params, file sizes, Page model)
- **v0.2.0**: Declarative filtering, sorting, search — reach parity (79%)
- **v0.3.0**: Multiple formats, HATEOAS, customizers — exceed parity (92%)
- **v0.4.0**: Multi-backend, advanced features — full ecosystem (100%)

**Target: pypaginate v0.4.0 will be the best-in-class choice for FastAPI pagination,
filtering, search, and sorting — in a single library.**
