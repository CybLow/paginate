# Cursor/Keyset Pagination

Keyset pagination (cursor-based) uses opaque cursor tokens instead of page numbers, providing constant-time performance regardless of how deep into the result set you go.

:::{tip} When to Use
Keyset pagination is best for **large datasets** (100k+ rows), **infinite scroll** UIs, and **real-time data** where consistent performance matters.
:::

## Overview

Instead of skipping rows with OFFSET, keyset pagination uses the last seen row's values to seek directly to the next page:

```sql
-- Offset (slow on deep pages):
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 100000;

-- Keyset (constant time):
SELECT * FROM users WHERE id > 100000 ORDER BY id LIMIT 20;
```

## CursorParams

```python
from pypaginate import CursorParams

# First page (no cursor)
params = CursorParams(limit=20)

# Next page
params = CursorParams(limit=20, after="cursor_token_from_response")

# Previous page
params = CursorParams(limit=20, before="cursor_token_from_response")
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `20` | Items per page (1-1000) |
| `after` | `str \| None` | `None` | Forward cursor |
| `before` | `str \| None` | `None` | Backward cursor |

`after` and `before` are mutually exclusive -- you cannot specify both.

## CursorPage

```python
page.items            # list[T] -- items for this page
page.limit            # int -- items per page
page.has_next         # bool -- True if next page exists
page.has_previous     # bool -- True if previous page exists
page.next_cursor      # str | None -- pass as `after` for next page
page.previous_cursor  # str | None -- pass as `before` for previous page
```

No `total` or `page` number -- these are offset-only concepts.

## SQLAlchemy Usage (Async)

Keyset pagination requires an ordered query:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import paginate, CursorParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend

async def list_users(
    session: AsyncSession,
    cursor: str | None = None,
    limit: int = 20,
):
    backend = SQLAlchemyCursorBackend(session)

    # Query MUST have ORDER BY (keyset pagination requirement)
    stmt = select(User).order_by(User.created_at.desc(), User.id.desc())

    params = CursorParams(limit=limit, after=cursor)
    page = await paginate(stmt, params, backend=backend)

    return {
        "items": page.items,
        "next_cursor": page.next_cursor,
        "previous_cursor": page.previous_cursor,
        "has_next": page.has_next,
        "has_previous": page.has_previous,
    }
```

## SQLAlchemy Usage (Sync)

```python
from sqlalchemy import select
from sqlalchemy.orm import Session
from pypaginate import CursorParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyCursorBackend

def list_users(session: Session, cursor: str | None = None, limit: int = 20):
    backend = SyncSQLAlchemyCursorBackend(session)
    stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
    params = CursorParams(limit=limit, after=cursor)

    # Sync cursor uses the backend directly (not paginate())
    items, next_cursor, prev_cursor = backend.fetch_page(
        stmt,
        limit=params.limit,
        after=params.after,
        before=params.before,
    )
```

## How Cursors Work

Cursors are opaque tokens that encode the position of the last item in the sort order. Under the hood, pypaginate uses a built-in cursor codec to serialize and deserialize bookmark positions.

```python
# Response from first page:
page.next_cursor  # "eyJpZCI6MTAwfQ=="

# Client sends this back for the next page:
params = CursorParams(limit=20, after="eyJpZCI6MTAwfQ==")
```

:::{note} Cursor Opacity
Treat cursors as opaque strings. Never parse, construct, or modify them manually.
:::

## Ordering Requirements

Keyset pagination requires:

1. **Consistent ordering** -- the same ORDER BY clause for all pages
2. **Unique tail column** -- include a unique column (like `id`) to break ties

```python
# Bad: non-unique ordering (ambiguous position)
stmt = select(User).order_by(User.name)

# Good: unique tiebreaker
stmt = select(User).order_by(User.name, User.id)

# Best for time-series: timestamp + unique ID
stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
```

## Traversal Patterns

### Forward Only (Infinite Scroll)

```python
# First page
page = await paginate(stmt, CursorParams(limit=20), backend=backend)

# Next page
if page.has_next:
    page = await paginate(
        stmt,
        CursorParams(limit=20, after=page.next_cursor),
        backend=backend,
    )
```

### Bidirectional

```python
# Go forward
next_page = await paginate(
    stmt,
    CursorParams(limit=20, after=page.next_cursor),
    backend=backend,
)

# Go back
prev_page = await paginate(
    stmt,
    CursorParams(limit=20, before=page.previous_cursor),
    backend=backend,
)
```

## Performance Benefits

| Rows | Page Depth | Offset Time | Keyset Time |
|------|------------|-------------|-------------|
| 1M | 1 | ~10ms | ~10ms |
| 1M | 100 | ~50ms | ~10ms |
| 1M | 10,000 | ~500ms | ~10ms |
| 1M | 100,000 | ~5s | ~10ms |

Keyset pagination uses an index seek instead of counting and skipping rows.

## Handling Data Changes

Keyset pagination handles concurrent inserts/deletes better than offset:

**Offset problem**: If a row is deleted on page 3 while viewing page 4, one item is skipped.

**Keyset solution**: The cursor points to a specific position, so insertions/deletions before the cursor don't affect the next page.

## Limitations

1. **No random page access** -- cannot jump to "page 50"
2. **No total count** -- by design (counting defeats the purpose)
3. **Requires stable ordering** -- changing ORDER BY invalidates existing cursors
4. **Requires SQLAlchemy** -- the built-in cursor implementation handles bookmark serialization

## Indexed Columns

Ensure ORDER BY columns are indexed for best performance:

```sql
-- Composite index for time-series pagination
CREATE INDEX idx_users_created_id
ON users (created_at DESC, id DESC);
```

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)

    __table_args__ = (
        Index("idx_users_created_id", created_at.desc(), id.desc()),
    )
```

## Choosing Offset vs Cursor

| Feature | Offset | Cursor |
|---------|--------|--------|
| Page numbers in UI | Yes | No |
| Random page access | Yes | No |
| Deep page performance | O(n) | O(1) |
| Total count | Yes | No |
| Concurrent-safe | Partial | Yes |
| Infinite scroll | Awkward | Natural |

## Next Steps

- [Offset Pagination](offset.md) -- When you need page numbers
- [In-Memory Pagination](memory.md) -- For Python collections
