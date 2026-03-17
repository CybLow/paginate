# SQLAlchemy Integration

The `pypaginate.adapters.sqlalchemy` package provides async and sync backends for
offset pagination, cursor/keyset pagination, filtering, sorting, and search --
all driven by SQLAlchemy 2.0+ Select statements.

## Installation

SQLAlchemy support is an optional dependency:

```bash
uv add pypaginate[sqlalchemy]   # SQLAlchemy
uv add pypaginate[all]          # Everything
```

## Exports at a Glance

```python
from pypaginate.adapters.sqlalchemy import (
    # Offset pagination
    SQLAlchemyBackend,             # async  -- PaginationBackend[T]
    SyncSQLAlchemyBackend,         # sync   -- SyncPaginationBackend[T]

    # Cursor/keyset pagination
    SQLAlchemyCursorBackend,       # async  -- CursorBackend[T]
    SyncSQLAlchemyCursorBackend,   # sync

    # Query transformation
    SQLAlchemyFilterBackend,       # FilterSpec  → WHERE clauses
    SQLAlchemySortBackend,         # SortSpec   → ORDER BY clauses
    SQLAlchemySearchBackend,       # SearchSpec → ILIKE clauses
)
```

---

## Offset Pagination

### SQLAlchemyBackend (async)

Implements the `PaginationBackend[T]` protocol using `SELECT COUNT(*)` and
`OFFSET/LIMIT`.

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import OffsetParams, paginate
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

async def list_users(session: AsyncSession):
    query = select(User).order_by(User.id)
    backend = SQLAlchemyBackend(session)
    return await paginate(query, OffsetParams(page=1, limit=20), backend=backend)
```

### SyncSQLAlchemyBackend

Same API, but synchronous -- implements `SyncPaginationBackend[T]`.

```python
from sqlalchemy.orm import Session

from pypaginate import OffsetParams, paginate
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyBackend

def list_users(session: Session):
    query = select(User).order_by(User.id)
    backend = SyncSQLAlchemyBackend(session)
    return paginate(query, OffsetParams(page=1, limit=20), backend=backend)
```

### Constructor Parameters

Both `SQLAlchemyBackend` and `SyncSQLAlchemyBackend` accept the same keyword
arguments:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session` | `AsyncSession` / `Session` | *required* | SQLAlchemy session |
| `count_query` | `Select` / `None` | `None` | Custom count query (see below) |
| `unique` | `bool` | `False` | Deduplicate rows via `result.unique()` (see below) |

---

## Custom Count Query

For queries with expensive JOINs, provide an optimized count query that avoids
the joins:

```python
from sqlalchemy import func, select

# Expensive main query with joins and eager loading
query = (
    select(Order)
    .join(Order.customer)
    .join(Order.items)
    .where(Order.status == "completed")
    .options(selectinload(Order.items))
)

# Cheap count -- same WHERE, no joins
count_query = (
    select(func.count(Order.id))
    .where(Order.status == "completed")
)

backend = SQLAlchemyBackend(session, count_query=count_query)
page = await paginate(query, params, backend=backend)
```

Without `count_query`, the backend wraps your main query in
`SELECT COUNT(*) FROM (your_query) AS subquery`, which can be slow for complex
queries.

---

## Deduplication

When JOINs produce duplicate parent rows (e.g., one Author joined to many Books),
pass `unique=True` to call `result.unique().scalars()` instead of
`result.scalars()`:

```python
query = (
    select(Author)
    .join(Author.books)
    .where(Book.genre == "fiction")
)

backend = SQLAlchemyBackend(session, unique=True)
page = await paginate(query, params, backend=backend)
# Authors are deduplicated
```

---

## Cursor/Keyset Pagination

### SQLAlchemyCursorBackend (async)

Uses a built-in cursor implementation for efficient
keyset pagination. Implements the `CursorBackend[T]` protocol.

**Requirement:** The query **must** have an `ORDER BY` clause.

```python
from pypaginate import CursorParams, paginate
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend

async def scroll_users(session: AsyncSession):
    query = select(User).order_by(User.id)
    backend = SQLAlchemyCursorBackend(session)

    # First page
    first = await paginate(
        query,
        CursorParams(limit=20),
        backend=backend,
    )

    # Next page using cursor
    if first.next_cursor:
        second = await paginate(
            query,
            CursorParams(limit=20, after=first.next_cursor),
            backend=backend,
        )
```

### SyncSQLAlchemyCursorBackend

Synchronous equivalent:

```python
from sqlalchemy.orm import Session
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyCursorBackend

def scroll_users(session: Session):
    query = select(User).order_by(User.id)
    backend = SyncSQLAlchemyCursorBackend(session)
    # same fetch_page interface, called synchronously
```

### CursorPage Fields

The returned `CursorPage[T]` has:

| Field | Type | Description |
|---|---|---|
| `items` | `list[T]` | Items for this page |
| `limit` | `int` | Requested page size |
| `has_next` | `bool` | Whether a next page exists |
| `has_previous` | `bool` | Whether a previous page exists |
| `next_cursor` | `str` / `None` | Bookmark for the next page |
| `previous_cursor` | `str` / `None` | Bookmark for the previous page |

---

## Filter Backend

`SQLAlchemyFilterBackend` translates `FilterSpec` objects into SQLAlchemy WHERE
clauses. Implements the `FilterBackend` protocol.

### Supported Operators

| Operator | SQL | Example |
|---|---|---|
| `eq` | `=` | `FilterSpec(field="status", value="active")` |
| `ne` | `!=` | `FilterSpec(field="status", operator="ne", value="deleted")` |
| `gt` | `>` | `FilterSpec(field="age", operator="gt", value=18)` |
| `gte` | `>=` | `FilterSpec(field="age", operator="gte", value=18)` |
| `lt` | `<` | `FilterSpec(field="price", operator="lt", value=100)` |
| `lte` | `<=` | `FilterSpec(field="price", operator="lte", value=100)` |
| `in` | `IN` | `FilterSpec(field="role", operator="in", value=["admin", "mod"])` |
| `not_in` | `NOT IN` | `FilterSpec(field="role", operator="not_in", value=["banned"])` |
| `contains` | `LIKE '%val%'` | `FilterSpec(field="name", operator="contains", value="al")` |
| `starts_with` | `LIKE 'val%'` | `FilterSpec(field="name", operator="starts_with", value="Al")` |
| `ends_with` | `LIKE '%val'` | `FilterSpec(field="email", operator="ends_with", value=".com")` |
| `like` | `LIKE` | `FilterSpec(field="name", operator="like", value="%ice%")` |
| `ilike` | `ILIKE` | `FilterSpec(field="name", operator="ilike", value="%ice%")` |
| `between` | `BETWEEN` | `FilterSpec(field="age", operator="between", value=[18, 65])` |
| `is_null` | `IS NULL` | `FilterSpec(field="deleted_at", operator="is_null")` |
| `is_not_null` | `IS NOT NULL` | `FilterSpec(field="email", operator="is_not_null")` |
| `regex` | `REGEXP` | `FilterSpec(field="code", operator="regex", value="^AB\\d+")` |

### AND/OR Logic

Each `FilterSpec` has a `logic` field (defaults to `FilterLogic.AND`). Specs with
`FilterLogic.OR` are combined with `OR`, everything else with `AND`:

```python
from pypaginate import FilterSpec, FilterLogic

filters = [
    FilterSpec(field="status", value="active"),
    FilterSpec(field="role", value="admin", logic=FilterLogic.OR),
    FilterSpec(field="role", value="moderator", logic=FilterLogic.OR),
]
# WHERE status = 'active' AND (role = 'admin' OR role = 'moderator')
```

### Usage

```python
from pypaginate.adapters.sqlalchemy import SQLAlchemyFilterBackend

filter_backend = SQLAlchemyFilterBackend()
query = filter_backend.apply_filters(query, filter_specs)
```

---

## Sort Backend

`SQLAlchemySortBackend` translates `SortSpec` objects into SQLAlchemy ORDER BY
clauses. Implements the `SortBackend` protocol.

Each `SortSpec` supports:

| Field | Type | Default | Description |
|---|---|---|---|
| `field` | `str` | *required* | Column name |
| `direction` | `SortDirection` | `ASC` | `SortDirection.ASC` or `SortDirection.DESC` |
| `nulls` | `NullsPosition` | `LAST` | `NullsPosition.FIRST` or `NullsPosition.LAST` |

```python
from pypaginate import SortSpec, SortDirection, NullsPosition
from pypaginate.adapters.sqlalchemy import SQLAlchemySortBackend

specs = [
    SortSpec(field="created_at", direction=SortDirection.DESC),
    SortSpec(field="name", nulls=NullsPosition.LAST),
]
query = SQLAlchemySortBackend.apply_sorting(query, specs)
```

---

## Search Backend

`SQLAlchemySearchBackend` translates a `SearchSpec` into ILIKE WHERE clauses.
Implements the `SearchBackend` protocol.

Search behavior:

- The query text is normalized and tokenized (whitespace-split)
- Each token must match at **least one** field (OR across fields)
- All tokens must match (AND across tokens)
- Match mode is controlled by `SearchFieldMode` (PREFIX, CONTAINS, EXACT)

```python
from pypaginate import SearchSpec
from pypaginate.adapters.sqlalchemy import SQLAlchemySearchBackend

spec = SearchSpec(query="alice smith", fields=("name", "email"))
query = SQLAlchemySearchBackend.apply_search(query, spec)
# WHERE (name ILIKE '%alice%' OR email ILIKE '%alice%')
#   AND (name ILIKE '%smith%' OR email ILIKE '%smith%')
```

---

## Pipeline Wiring

The recommended pattern for FastAPI + SQLAlchemy is to wire an `AsyncPipeline`
that composes all backends:

```python
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend,
    SQLAlchemyFilterBackend,
    SQLAlchemySortBackend,
    SQLAlchemySearchBackend,
)

async def get_pipeline(
    session: AsyncSession = Depends(get_session),
) -> AsyncPipeline:
    backend = SQLAlchemyBackend(session)
    return AsyncPipeline(
        AsyncPaginator(backend),
        filter_backend=SQLAlchemyFilterBackend(),
        sort_backend=SQLAlchemySortBackend(),
        search_backend=SQLAlchemySearchBackend(),
    )
```

Then in your endpoint:

```python
from pypaginate.adapters.fastapi import (
    FilterDep, FilterField, OffsetDep, SearchDep, SortDep,
)

class ProductFilters(FilterDep):
    category: str | None = FilterField(None, operator="eq")
    min_price: float | None = FilterField(None, field="price", operator="gte")

@app.get("/products")
async def list_products(
    params: OffsetDep,
    filters: Annotated[ProductFilters, Query()],
    sort: SortDep,
    search: SearchDep,
    pipeline: AsyncPipeline = Depends(get_pipeline),
) -> OffsetPage[ProductSchema]:
    query = select(Product).order_by(Product.id)
    return await pipeline.execute(
        query, params, filters=filters, sorting=sort, search=search,
    )
```

The pipeline auto-converts `FilterDep.to_specs()`, `SortDep.to_specs()`, and
`SearchDep.to_spec()` internally.

---

## Performance Tips

1. **Always include ORDER BY** for consistent pagination across pages
2. **Provide `count_query`** for queries with expensive JOINs or subqueries
3. **Use `unique=True`** only when JOINs produce duplicate parent rows
4. **Use cursor pagination** for large datasets (avoids `OFFSET N` degradation)
5. **Index sort columns** to avoid full table scans on ORDER BY
6. **Limit eager loading** -- use `load_only()` and `selectinload()` to minimize data transfer

---

## Error Handling

```python
from pypaginate import (
    ConfigurationError,  # missing entity, bad field name
    FilterError,         # unsupported operator, bad BETWEEN value
    ValidationError,     # bad page/limit values
)
```

- `ConfigurationError` is raised when column resolution fails (field not found on entity)
- `FilterError` is raised for unsupported operators or malformed filter values
- `ValidationError` is raised for invalid pagination parameters

---

## See Also

- [FastAPI Integration](fastapi.md) -- dependency types and declarative filters
- API Reference -- see the `adapters` section in the generated API docs
