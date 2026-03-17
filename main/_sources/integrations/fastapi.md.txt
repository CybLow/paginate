# FastAPI Integration

The `pypaginate.adapters.fastapi` package provides **Annotated** dependency types
that parse query parameters into pypaginate domain objects with zero boilerplate.

## Installation

```bash
uv add pypaginate[fastapi]
```

## Exports at a Glance

```python
from pypaginate.adapters.fastapi import (
    OffsetDep,     # Annotated[OffsetParams, Depends(...)]
    CursorDep,     # Annotated[CursorParams, Depends(...)]
    FilterDep,     # Base class for declarative filter models
    FilterField,   # Field descriptor with operator metadata
    SortDep,       # Parses ?sort=name,-age into SortSpec list
    SearchDep,     # Parses ?q=alice&search_fields=name,email into SearchSpec
)
```

---

## Pagination Parameters

### OffsetDep

Parses `?page=` and `?limit=` into an `OffsetParams` instance.

| Query Param | Type | Default | Constraints |
|---|---|---|---|
| `page` | int | 1 | >= 1 |
| `limit` | int | 20 | >= 1, <= 1000 |

```python
from pypaginate import OffsetPage, paginate
from pypaginate.adapters.fastapi import OffsetDep

@app.get("/users")
async def list_users(params: OffsetDep) -> OffsetPage[UserSchema]:
    return paginate(users, params)
```

**Example requests:**

```
GET /users                    # page=1, limit=20
GET /users?page=3             # page=3, limit=20
GET /users?page=2&limit=50    # page=2, limit=50
```

The `OffsetParams` object exposes:

- `params.page` -- current page number
- `params.limit` -- items per page
- `params.offset` -- computed zero-based offset `(page - 1) * limit`

### CursorDep

Parses `?limit=`, `?after=`, and `?before=` into a `CursorParams` instance.

| Query Param | Type | Default | Constraints |
|---|---|---|---|
| `limit` | int | 20 | >= 1, <= 1000 |
| `after` | str | None | Cursor for the next page |
| `before` | str | None | Cursor for the previous page |

`after` and `before` are mutually exclusive -- providing both raises a `ValidationError`.

```python
from pypaginate import CursorPage, paginate
from pypaginate.adapters.fastapi import CursorDep
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend

@app.get("/users/scroll")
async def scroll_users(
    params: CursorDep,
    session: AsyncSession = Depends(get_session),
) -> CursorPage[UserSchema]:
    query = select(User).order_by(User.id)
    backend = SQLAlchemyCursorBackend(session)
    return await paginate(query, params, backend=backend)
```

---

## Declarative Filters

### FilterDep and FilterField

Subclass `FilterDep` and annotate fields with `FilterField()` to declare filter
parameters. Non-`None` fields are automatically converted to `FilterSpec` objects
when the pipeline calls `to_specs()`.

```python
from typing import Annotated
from fastapi import Query
from pypaginate.adapters.fastapi import FilterDep, FilterField

class UserFilters(FilterDep):
    name: str | None = FilterField(None, operator="contains")
    age_min: int | None = FilterField(None, field="age", operator="gte")
    age_max: int | None = FilterField(None, field="age", operator="lte")
    role: str | None = FilterField(None, operator="eq")
```

**`FilterField` parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `default` | Any | None | Default value. `None` means the filter is not applied. |
| `operator` | str | `"eq"` | Filter operator: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `contains`, `starts_with`, `ends_with`, `like`, `ilike`, `between`, `is_null`, `is_not_null`, `regex`. |
| `field` | str | None | Target field name on the model. Defaults to the attribute name. |

**Endpoint usage:**

```python
@app.get("/users")
async def list_users(
    params: OffsetDep,
    filters: Annotated[UserFilters, Query()],
    session: AsyncSession = Depends(get_session),
) -> OffsetPage[UserSchema]:
    page = await pipeline.execute(
        select(User).order_by(User.id),
        params,
        filters=filters,
    )
    return page
```

**Example request:**

```
GET /users?name=alice&age_min=18&role=admin
```

This generates three `FilterSpec` objects:

1. `FilterSpec(field="name", operator="contains", value="alice")`
2. `FilterSpec(field="age", operator="gte", value=18)`
3. `FilterSpec(field="role", operator="eq", value="admin")`

---

## Sort Parsing

### SortDep

Parses `?sort=name,-age` into a list of `SortSpec` objects.

- No prefix or `+` prefix means ascending
- `-` prefix means descending

```python
from pypaginate.adapters.fastapi import SortDep

@app.get("/users")
async def list_users(
    params: OffsetDep,
    sort: SortDep,
    session: AsyncSession = Depends(get_session),
) -> OffsetPage[UserSchema]:
    page = await pipeline.execute(
        select(User).order_by(User.id),
        params,
        sorting=sort,
    )
    return page
```

**Example requests:**

```
GET /users?sort=name              # ORDER BY name ASC
GET /users?sort=-created_at       # ORDER BY created_at DESC
GET /users?sort=role,-age,name    # ORDER BY role ASC, age DESC, name ASC
```

---

## Search Parsing

### SearchDep

Parses `?q=` and `?search_fields=` into a `SearchSpec` (or `None` if `q` is empty).

| Query Param | Type | Default | Description |
|---|---|---|---|
| `q` | str | None | Search text |
| `search_fields` | str | `""` | Comma-separated field names to search |

Both `q` and `search_fields` must be provided for a search to execute.

```python
from pypaginate.adapters.fastapi import SearchDep

@app.get("/users")
async def list_users(
    params: OffsetDep,
    search: SearchDep,
    session: AsyncSession = Depends(get_session),
) -> OffsetPage[UserSchema]:
    page = await pipeline.execute(
        select(User).order_by(User.id),
        params,
        search=search,
    )
    return page
```

**Example request:**

```
GET /users?q=alice&search_fields=name,email
```

---

## Pipeline Auto-Conversion

The `AsyncPipeline` and `SyncPipeline` automatically detect `FilterDep`, `SortDep`,
and `SearchDep` objects via the protocol methods `to_specs()` and `to_spec()`.
You pass them directly -- no manual conversion needed:

```python
from pypaginate.engine.pipeline import AsyncPipeline
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend,
    SQLAlchemyFilterBackend,
    SQLAlchemySortBackend,
    SQLAlchemySearchBackend,
)

# Build once at startup
def create_pipeline(session: AsyncSession) -> AsyncPipeline:
    backend = SQLAlchemyBackend(session)
    paginator = AsyncPaginator(backend)
    return AsyncPipeline(
        paginator,
        filter_backend=SQLAlchemyFilterBackend(),
        sort_backend=SQLAlchemySortBackend(),
        search_backend=SQLAlchemySearchBackend(),
    )
```

Then in endpoints, pass FastAPI deps directly:

```python
pipeline.execute(query, params, filters=filters, sorting=sort, search=search)
```

The pipeline calls `filters.to_specs()`, `sort.to_specs()`, and `search.to_spec()`
internally, then delegates to the SQLAlchemy backends.

---

## Complete Endpoint Example

A full endpoint combining all features:

```python
from typing import Annotated

from fastapi import Depends, FastAPI, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import OffsetPage
from pypaginate.adapters.fastapi import (
    FilterDep, FilterField, OffsetDep, SearchDep, SortDep,
)
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend,
    SQLAlchemyFilterBackend,
    SQLAlchemySearchBackend,
    SQLAlchemySortBackend,
)
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline

app = FastAPI(title="User API")


# --- Filter model ---
class UserFilters(FilterDep):
    name: str | None = FilterField(None, operator="contains")
    role: str | None = FilterField(None, operator="eq")
    age_min: int | None = FilterField(None, field="age", operator="gte")


# --- Endpoint ---
@app.get("/users")
async def list_users(
    params: OffsetDep,
    filters: Annotated[UserFilters, Query()],
    sort: SortDep,
    search: SearchDep,
    session: AsyncSession = Depends(get_session),
) -> OffsetPage[UserSchema]:
    backend = SQLAlchemyBackend(session)
    pipeline = AsyncPipeline(
        AsyncPaginator(backend),
        filter_backend=SQLAlchemyFilterBackend(),
        sort_backend=SQLAlchemySortBackend(),
        search_backend=SQLAlchemySearchBackend(),
    )
    query = select(User).order_by(User.id)
    return await pipeline.execute(
        query,
        params,
        filters=filters,
        sorting=sort,
        search=search,
    )
```

**Example request combining all features:**

```
GET /users?page=2&limit=10&name=al&role=admin&sort=-age,name&q=alice&search_fields=name,email
```

---

## Error Handling

pypaginate raises typed exceptions that map cleanly to HTTP status codes:

```python
from pypaginate import PaginationError, ValidationError, FilterError

@app.exception_handler(ValidationError)
async def validation_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(FilterError)
async def filter_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "field": exc.field},
    )

@app.exception_handler(PaginationError)
async def pagination_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

---

## OpenAPI Documentation

All dependencies generate proper OpenAPI schemas automatically:

- `OffsetDep` / `CursorDep` expose query parameters with types and constraints
- `FilterDep` subclasses expose each filter field as a query parameter
- `SortDep` exposes `?sort=` as an optional string
- `SearchDep` exposes `?q=` and `?search_fields=`

Access your docs at `/docs` (Swagger UI) or `/redoc` (ReDoc).

---

## See Also

- [SQLAlchemy Integration](sqlalchemy.md) -- backend configuration and cursor pagination
- API Reference -- see the `adapters` section in the generated API docs
