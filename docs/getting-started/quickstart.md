# Quick Start

Get up and running with pypaginate in 5 minutes.

## Installation

```bash
pip install pypaginate
```

## The 3-Line Core

```python
from pypaginate import paginate, OffsetParams

page = paginate([1, 2, 3, 4, 5], OffsetParams(page=1, limit=2))
```

That is it. `paginate()` detects the input type and returns the right page type automatically.

## In-Memory Pagination

Paginate any Python sequence (list, tuple, etc.) with zero setup:

```python
from pypaginate import paginate, OffsetParams

users = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25},
    {"id": 3, "name": "Charlie", "age": 35},
    {"id": 4, "name": "Diana", "age": 28},
    {"id": 5, "name": "Eve", "age": 32},
]

page = paginate(users, OffsetParams(page=1, limit=2))

print(page.items)        # [{"id": 1, ...}, {"id": 2, ...}]
print(page.total)        # 5
print(page.page)         # 1
print(page.pages)        # 3
print(page.has_next)     # True
print(page.has_previous) # False
```

## SQLAlchemy Pagination

Paginate database queries with an async SQLAlchemy backend:

```bash
pip install pypaginate[sqlalchemy]
```

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend


async def list_users(session: AsyncSession):
    query = select(User).order_by(User.created_at.desc())
    backend = SQLAlchemyBackend(session)

    page = await paginate(query, OffsetParams(page=1, limit=20), backend=backend)

    return {
        "items": page.items,
        "total": page.total,
        "page": page.page,
        "pages": page.pages,
    }
```

## FastAPI Integration

Use built-in dependencies for automatic query parameter parsing:

```bash
pip install pypaginate[fastapi]
```

```python
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import paginate, OffsetPage
from pypaginate.adapters.fastapi import OffsetDep
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

app = FastAPI()


@app.get("/users")
async def list_users(params: OffsetDep, session: AsyncSession = Depends(get_session)):
    query = select(User).order_by(User.id)
    backend = SQLAlchemyBackend(session)
    return await paginate(query, params, backend=backend)
```

Your API now accepts `?page=1&limit=20` query parameters automatically.

## Core Concepts

### OffsetParams

Immutable pagination input:

```python
from pypaginate import OffsetParams

params = OffsetParams(page=2, limit=20)

params.page    # 2
params.limit   # 20
params.offset  # 20  (computed: (page - 1) * limit)
```

### OffsetPage

The pagination result:

```python
from pypaginate import OffsetPage

# OffsetPage fields:
# - items: list[T]       -- items for this page
# - total: int           -- total count across all pages
# - page: int            -- current page number
# - pages: int           -- total number of pages
# - limit: int           -- items per page
# - has_next: bool       -- True if more pages exist
# - has_previous: bool   -- True if not on first page
```

### CursorParams / CursorPage

For keyset/cursor pagination (large datasets, real-time feeds):

```python
from pypaginate import CursorParams, CursorPage

params = CursorParams(limit=20)                  # first page
params = CursorParams(limit=20, after="abc123")   # next page
params = CursorParams(limit=20, before="xyz789")  # previous page

# CursorPage fields:
# - items, limit, has_next, has_previous (same as OffsetPage)
# - next_cursor: str | None
# - previous_cursor: str | None
# (no total, no page -- those are offset-only concepts)
```

## Error Handling

```python
from pypaginate import OffsetParams, ValidationError

try:
    params = OffsetParams(page=0, limit=20)  # page must be >= 1
except ValidationError as e:
    print(e)  # "page must be >= 1"
```

## Next Steps

- [First Steps](first-steps.md) -- Filtering, sorting, and search examples
- [Examples](../examples/index.md) -- Complete runnable examples
- [API Reference](../api/overview.md) -- Full API documentation
