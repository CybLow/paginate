# Framework Integrations

pypaginate provides adapter packages for FastAPI and SQLAlchemy that translate between
framework-specific concepts and the library's domain types.

:::{tip} Installation
```bash
uv add pypaginate[fastapi]      # FastAPI dependencies
uv add pypaginate[sqlalchemy]   # SQLAlchemy
uv add pypaginate[all]          # Everything
```
:::

## Available Integrations

| Integration | Description | Import Path |
|---|---|---|
| [FastAPI](fastapi.md) | Annotated deps, declarative filters, sort/search parsing | `pypaginate.adapters.fastapi` |
| [SQLAlchemy](sqlalchemy.md) | Async/sync offset + cursor backends, filter/sort/search | `pypaginate.adapters.sqlalchemy` |

## How It Fits Together

```
  FastAPI Endpoint
        |
  OffsetDep / CursorDep          ← query params → OffsetParams / CursorParams
  FilterDep, SortDep, SearchDep  ← query params → FilterSpec / SortSpec / SearchSpec
        |
  AsyncPipeline.execute()        ← applies specs to the SA Select
        |
  SQLAlchemyBackend              ← COUNT + OFFSET/LIMIT
  SQLAlchemyCursorBackend        ← built-in keyset cursor
        |
  OffsetPage[T] / CursorPage[T] ← returned to caller
```

### FastAPI Integration

The FastAPI adapter provides **Annotated** dependency types that parse query parameters
directly into pypaginate domain objects:

```python
from pypaginate.adapters.fastapi import (
    OffsetDep, CursorDep,
    FilterDep, FilterField,
    SortDep, SearchDep,
)
```

### SQLAlchemy Integration

The SQLAlchemy adapter provides async and sync backends for all four concerns:

```python
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend, SyncSQLAlchemyBackend,       # offset pagination
    SQLAlchemyCursorBackend, SyncSQLAlchemyCursorBackend,  # cursor pagination
    SQLAlchemyFilterBackend,                         # WHERE clauses
    SQLAlchemySortBackend,                           # ORDER BY clauses
    SQLAlchemySearchBackend,                         # ILIKE search
)
```

## Minimal End-to-End Example

```python
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import OffsetPage, paginate
from pypaginate.adapters.fastapi import OffsetDep
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

app = FastAPI()

@app.get("/users")
async def list_users(
    params: OffsetDep,
    session: AsyncSession = Depends(get_session),
) -> OffsetPage[UserSchema]:
    query = select(User).order_by(User.id)
    backend = SQLAlchemyBackend(session)
    return await paginate(query, params, backend=backend)
```

## Next Steps

- [FastAPI Integration](fastapi.md) -- pagination deps, declarative filters, sorting, and search
- [SQLAlchemy Integration](sqlalchemy.md) -- backend configuration, cursor pagination, deduplication
