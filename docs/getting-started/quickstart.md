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
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import paginate, OffsetPage
from pypaginate.adapters.fastapi import OffsetDep
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

app = FastAPI()


@app.get("/users")
async def list_users(params: OffsetDep, session: AsyncSession = Depends(get_session)) -> OffsetPage:
    query = select(User).order_by(User.id)
    backend = SQLAlchemyBackend(session)
    return await paginate(query, params, backend=backend)
```

Your API now accepts `?page=1&limit=20` query parameters automatically.

## Core Concepts

| Concept | Description | Details |
|---------|-------------|---------|
| `OffsetParams` | Immutable pagination input (`page`, `limit`, computed `offset`) | [Basic Pagination](../examples/basic-pagination.md#offsetparams) |
| `OffsetPage` | Result with `items`, `total`, `page`, `pages`, `has_next`, `has_previous` | [Basic Pagination](../examples/basic-pagination.md#offsetpage) |
| `CursorParams` | Cursor input (`limit`, `after`, `before`) | [Keyset Pagination](../examples/keyset.md#cursorparams-and-cursorpage) |
| `CursorPage` | Result with `items`, `next_cursor`, `previous_cursor` (no `total`/`page`) | [Keyset Pagination](../examples/keyset.md#cursorparams-and-cursorpage) |

## Next Steps

- [First Steps](first-steps.md) -- Filtering, sorting, and search examples
- [Examples](../examples/index.md) -- Complete runnable examples
- [API Reference](../api/overview.md) -- Full API documentation
