# Query Module

The query module provides high-level async functions for paginating SQLAlchemy queries. These functions abstract the complexity of query execution, count queries, and snapshot handling.

## Overview

| Function | Returns | Use Case |
|----------|---------|----------|
| `paginate_entities` | `tuple[list[T], int]` | ORM entities with total count |
| `paginate_entities_to_page` | `Page[T]` | ORM entities wrapped in Page |
| `paginate_rows` | `tuple[list[T], int]` | Raw rows with total count |
| `paginate_rows_to_page` | `Page[T]` | Raw rows wrapped in Page |

## paginate_entities

Paginate ORM entities, returning items and total count.

```{eval-rst}
.. autofunction:: pypaginate.query.paginate_entities
```

## paginate_entities_to_page

Paginate ORM entities, returning a `Page` object.

```{eval-rst}
.. autofunction:: pypaginate.query.paginate_entities_to_page
```

## paginate_rows

Paginate raw rows (tuples), returning items and total count.

```{eval-rst}
.. autofunction:: pypaginate.query.paginate_rows
```

## paginate_rows_to_page

Paginate raw rows, returning a `Page` object.

```{eval-rst}
.. autofunction:: pypaginate.query.paginate_rows_to_page
```

## Usage Examples

### Paginating ORM Entities

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.core import PageParams
from pypaginate.query import paginate_entities, paginate_entities_to_page


async def list_users(session: AsyncSession) -> None:
    params = PageParams(page=1, limit=20)
    
    # Get entities as tuple
    users, total = await paginate_entities(
        session, 
        select(User), 
        params
    )
    print(f"Found {total} users, showing {len(users)}")
    
    # Or get a Page object directly
    page = await paginate_entities_to_page(
        session, 
        select(User), 
        params
    )
    print(f"Page {page.page} of {page.pages}")
```

### Paginating Raw Rows

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.core import PageParams
from pypaginate.query import paginate_rows, paginate_rows_to_page


async def list_user_names(session: AsyncSession) -> None:
    params = PageParams(page=1, limit=20)
    
    # Select specific columns
    query = select(User.id, User.name, User.email)
    
    # Get rows as tuple
    rows, total = await paginate_rows(session, query, params)
    for user_id, name, email in rows:
        print(f"{name} ({email})")
    
    # Or get a Page object
    page = await paginate_rows_to_page(session, query, params)
    print(f"Has next page: {page.has_next}")
```

### Using Optional Parameters

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.core import PageParams
from pypaginate.query import paginate_entities


async def list_unique_users(session: AsyncSession) -> None:
    params = PageParams(page=1, limit=20)
    
    # Custom count query for complex scenarios
    count_query = select(func.count()).select_from(User)
    
    users, total = await paginate_entities(
        session,
        select(User),
        params,
        count_query=count_query,  # Override automatic count
        unique=True,               # Deduplicate results
        clamp=True,                # Clamp page to valid range
    )
```

## Parameters Reference

All pagination functions accept these optional keyword arguments:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count_query` | `Select[tuple[int]] \| None` | `None` | Custom count query (auto-generated if not provided) |
| `unique` | `bool` | `False` | Deduplicate rows before counting |
| `clamp` | `bool` | `False` | Clamp page params to valid bounds |
