# Cursor/Keyset Pagination

Keyset pagination (also called cursor-based pagination) uses unique column values instead of offsets, providing constant-time performance regardless of page depth.

!!! tip "When to Use"
    Keyset pagination is best for **large datasets** (100k+ rows), **infinite scroll** UIs, and **real-time data streams** where consistent performance matters.

## Overview

Instead of using page numbers, keyset pagination uses the last item's value as a reference point:

```sql
-- Traditional offset (slow on deep pages)
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 100000;

-- Keyset pagination (constant time)
SELECT * FROM users WHERE id > 100000 ORDER BY id LIMIT 20;
```

## When to Use Keyset Pagination

| Use Case | Recommendation |
|----------|----------------|
| Large datasets (100k+ rows) | Keyset |
| Infinite scroll UI | Keyset |
| Real-time data streams | Keyset |
| Need page numbers | Offset |
| Random page access | Offset |
| Small datasets | Either |

## Basic Usage

```python
from pypaginate.core import KeysetPageParams
from pypaginate.engines import KeysetPaginator
from sqlalchemy import select

async def list_users(session, cursor: str | None = None, limit: int = 20):
    # Create parameters
    params = KeysetPageParams(
        limit=limit,
        after=cursor,  # Cursor from previous page (or None for first page)
    )
    
    # Query must be ordered
    stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
    
    # Paginate
    paginator = KeysetPaginator()
    result = await paginator.paginate(session, stmt, params)
    
    return {
        "items": result.items,
        "next_cursor": result.next_page,  # Token for next page
        "prev_cursor": result.previous_page,  # Token for previous page
        "has_next": result.next_page is not None,
        "has_previous": result.previous_page is not None,
    }
```

## KeysetPageParams

### Creating Parameters

```python
from pypaginate.core import KeysetPageParams

# First page
params = KeysetPageParams(limit=20)

# Next page (using cursor from previous response)
params = KeysetPageParams(limit=20, after="eyJpZCI6MTAwfQ==")

# Previous page
params = KeysetPageParams(limit=20, before="eyJpZCI6ODF9")

# Go to specific page (if you have the cursor)
params = KeysetPageParams(limit=20, page="eyJwYWdlIjoxMH0=")
```

### Validation

Only one of `after`, `before`, or `page` can be specified:

```python
# This raises an error
params = KeysetPageParams(
    limit=20,
    after="cursor1",
    before="cursor2",  # Error! Can't use both
)
```

## How Cursors Work

Cursors are opaque tokens that encode the position in the result set:

```python
# Under the hood, cursors contain:
# - Values of ORDER BY columns
# - Direction information

# For a query ordered by (created_at DESC, id DESC):
# Cursor might encode: {"created_at": "2024-01-15T10:00:00", "id": 100}

# The paginator converts this to:
# WHERE (created_at, id) < ('2024-01-15T10:00:00', 100)
```

!!! note "Cursor Opacity"
    Treat cursors as opaque strings. Don't parse or construct them manually.

## Ordering Requirements

Keyset pagination requires:

1. **Consistent ordering**: Same ORDER BY clause for all pages
2. **Unique ordering**: Include a unique column (like `id`) to break ties

```python
# Bad: Non-unique ordering
stmt = select(User).order_by(User.name)  # Two "John"s - which comes first?

# Good: Unique tiebreaker
stmt = select(User).order_by(User.name, User.id)

# Best for time-series: Timestamp + ID
stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
```

## API Response Pattern

A typical keyset-paginated API:

??? example "Complete FastAPI Example"
    ```python
    from fastapi import FastAPI, Query
    from pydantic import BaseModel

    app = FastAPI()

    class CursorPageResponse(BaseModel):
        items: list[UserSchema]
        next_cursor: str | None
        prev_cursor: str | None
        has_next: bool
        has_previous: bool

    @app.get("/users", response_model=CursorPageResponse)
    async def list_users(
        session: AsyncSession = Depends(get_session),
        cursor: str | None = Query(None, description="Pagination cursor"),
        limit: int = Query(20, ge=1, le=100),
    ):
        params = KeysetPageParams(limit=limit, after=cursor)
        stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
        
        paginator = KeysetPaginator()
        result = await paginator.paginate(session, stmt, params)
        
        return CursorPageResponse(
            items=result.items,
            next_cursor=result.next_page,
            prev_cursor=result.previous_page,
            has_next=result.next_page is not None,
            has_previous=result.previous_page is not None,
        )
    ```

Client usage:

```javascript
// First request
GET /users?limit=20

// Response includes next_cursor
{
    "items": [...],
    "next_cursor": "eyJpZCI6MTAwfQ==",
    "has_next": true
}

// Next page
GET /users?limit=20&cursor=eyJpZCI6MTAwfQ==
```

## Performance Benefits

### Offset vs Keyset at Scale

| Rows | Page | Offset Time | Keyset Time |
|------|------|-------------|-------------|
| 1M | 1 | 10ms | 10ms |
| 1M | 100 | 50ms | 10ms |
| 1M | 10,000 | 500ms | 10ms |
| 1M | 100,000 | 5s | 10ms |

### Why Keyset is Faster

```sql
-- Offset: Database must count and skip rows
SELECT * FROM users ORDER BY id OFFSET 100000 LIMIT 20;
-- Internal: Count 100,000 rows, skip them, return 20

-- Keyset: Direct index lookup
SELECT * FROM users WHERE id > 100000 ORDER BY id LIMIT 20;
-- Internal: Seek to id=100000 in index, return 20
```

## Handling Data Changes

Keyset pagination handles concurrent modifications better than offset:

### With Offset Pagination

```python
# User on page 5 (items 81-100)
# Another user deletes item 50
# User goes to page 6: MISSES item 100 (now at position 99)
```

### With Keyset Pagination

```python
# User has cursor pointing to item 100
# Another user deletes item 50
# User fetches next page: Gets items after 100 correctly
```

## Limitations

1. **No random page access**: Can't jump to "page 50"
2. **No total count**: By design (counting defeats the purpose)
3. **Must have stable ordering**: Changes to ORDER BY break cursors

### Workaround: Approximate Counts

If you need approximate totals:

??? example "PostgreSQL Approximate Count"
    ```python
    from sqlalchemy import func, text

    async def get_approximate_count(session, table_name: str) -> int:
        """Get approximate count using table statistics (PostgreSQL)."""
        result = await session.execute(
            text(f"""
                SELECT reltuples::bigint 
                FROM pg_class 
                WHERE relname = :table
            """),
            {"table": table_name}
        )
        return result.scalar() or 0
    ```

## Indexed Columns

Ensure your ORDER BY columns are indexed:

```sql
-- Create composite index for efficient keyset queries
CREATE INDEX idx_users_created_id 
ON users (created_at DESC, id DESC);
```

```python
# SQLAlchemy model with index
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_users_created_id', created_at.desc(), id.desc()),
    )
```

## Next Steps

- [Offset Pagination](offset.md) - When you need page numbers
- [In-Memory Pagination](memory.md) - For collections
- [SQLAlchemy Integration](../integrations/sqlalchemy.md) - Advanced patterns
