# Engines Module

The engines module provides pagination implementations for different data sources.

## SqlPaginator

The main SQL pagination engine for SQLAlchemy queries.

::: pypaginator.engines.sql.SqlPaginator
    options:
      show_source: true
      members:
        - __init__
        - paginate
        - paginate_keyset

## MemoryPaginator

In-memory pagination for Python collections.

::: pypaginator.engines.memory.MemoryPaginator
    options:
      show_source: true

## Keyset Pagination

::: pypaginator.engines.keyset
    options:
      show_source: true
      members:
        - select_keyset_page

## Strategy Selection

::: pypaginator.engines.sql.get_pagination_strategy
    options:
      show_source: true

## Query API

High-level async pagination functions.

::: pypaginator.query.async_api.paginate_entities
    options:
      show_source: true

::: pypaginator.query.async_api.paginate_entities_to_page
    options:
      show_source: true

::: pypaginator.query.async_api.paginate_rows
    options:
      show_source: true

::: pypaginator.query.async_api.paginate_rows_to_page
    options:
      show_source: true

## Usage Examples

### Basic SQL Pagination

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginator.engines.sql import SqlPaginator
from pypaginator.core import PageParams
from pypaginator.core.context import PaginationContext

async def paginate_users(session: AsyncSession):
    paginator = SqlPaginator(session, clamp=True)
    
    context = PaginationContext(
        params=PageParams(page=1, limit=20),
        count_query=None,
        unique=False,
    )
    
    stmt = select(User).order_by(User.id)
    snapshot = await paginator.paginate(stmt, context, scalars=True)
    
    return snapshot.items, snapshot.total
```

### Using Query API (Recommended)

```python
from pypaginator.query import paginate_entities_to_page
from pypaginator.core import PageParams

async def list_users(session: AsyncSession):
    stmt = select(User).order_by(User.created_at.desc())
    params = PageParams(page=1, limit=20)
    
    page = await paginate_entities_to_page(session, stmt, params)
    return page
```

### Keyset Pagination

```python
from pypaginator.engines.sql import SqlPaginator
from pypaginator.core import KeysetPageParams

async def keyset_paginate(session: AsyncSession):
    paginator = SqlPaginator(session, clamp=False)
    
    params = KeysetPageParams(limit=20)
    stmt = select(User).order_by(User.id)
    
    snapshot = await paginator.paginate_keyset(
        stmt, params, unique=False, scalars=True
    )
    
    # Use snapshot.next_marker for next page
    return snapshot

```

### In-Memory Pagination

```python
from pypaginator.engines.memory import MemoryPaginator
from pypaginator.core import PageParams

def paginate_list(items: list, page: int, limit: int):
    paginator = MemoryPaginator()
    params = PageParams(page=page, limit=limit)
    
    return paginator.paginate(items, params)
```
