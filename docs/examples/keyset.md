# Keyset Pagination Example

This example demonstrates keyset (cursor-based) pagination for efficient handling of large datasets.

## Why Keyset Pagination?

Offset pagination has performance issues with large datasets:

```sql
-- Offset pagination: gets slower as offset increases
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 100000;
-- Database must scan 100,000 rows before returning 20
```

Keyset pagination uses a cursor to resume from the last item:

```sql
-- Keyset pagination: consistent performance
SELECT * FROM users WHERE id > 100000 ORDER BY id LIMIT 20;
-- Database uses index, much faster
```

## Complete Example

```python
"""Keyset pagination example with pypaginate."""
import asyncio
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from pypaginator.core import KeysetPageParams
from pypaginator.engines.sql import SqlPaginator


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./keyset.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Event(id={self.id}, name={self.name})"


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data():
    """Create 10,000 events for testing."""
    async with async_session() as session:
        result = await session.execute(select(Event).limit(1))
        if result.scalar():
            return
        
        # Batch insert for performance
        batch_size = 1000
        for batch in range(10):
            events = [
                Event(name=f"Event {batch * batch_size + i}")
                for i in range(batch_size)
            ]
            session.add_all(events)
            await session.commit()
        
        print("Created 10,000 events")


async def keyset_paginate_all():
    """Paginate through all events using keyset pagination."""
    async with async_session() as session:
        paginator = SqlPaginator(session, clamp=False)
        
        # First page - no cursor
        params = KeysetPageParams(limit=100)
        stmt = select(Event).order_by(Event.id)
        
        page_num = 1
        total_fetched = 0
        
        while True:
            snapshot = await paginator.paginate_keyset(
                stmt, params, unique=False, scalars=True
            )
            
            items = snapshot.items
            total_fetched += len(items)
            
            print(f"Page {page_num}: fetched {len(items)} items "
                  f"(total: {total_fetched})")
            
            if items:
                print(f"  First: {items[0]}")
                print(f"  Last: {items[-1]}")
            
            # Check if there are more pages
            if not snapshot.next_marker:
                print("\nReached end of data")
                break
            
            # Get next page using cursor
            params = KeysetPageParams(limit=100, after=snapshot.next_marker)
            page_num += 1
            
            # Safety limit for example
            if page_num > 5:
                print(f"\n(Stopping after 5 pages for demo)")
                break
    
    return total_fetched


async def bidirectional_navigation():
    """Demonstrate forward and backward navigation."""
    async with async_session() as session:
        paginator = SqlPaginator(session, clamp=False)
        stmt = select(Event).order_by(Event.id)
        
        # Go to page 3
        params = KeysetPageParams(limit=10)
        cursors = []
        
        print("=== Navigating Forward ===")
        for i in range(3):
            snapshot = await paginator.paginate_keyset(
                stmt, params, unique=False, scalars=True
            )
            print(f"Page {i+1}: {snapshot.items[0]} to {snapshot.items[-1]}")
            
            cursors.append({
                'next': snapshot.next_marker,
                'prev': snapshot.prev_marker,
            })
            
            if snapshot.next_marker:
                params = KeysetPageParams(limit=10, after=snapshot.next_marker)
        
        print("\n=== Navigating Backward ===")
        # Go back to page 2
        if cursors[-1]['prev']:
            params = KeysetPageParams(limit=10, before=cursors[-1]['prev'])
            snapshot = await paginator.paginate_keyset(
                stmt, params, unique=False, scalars=True
            )
            print(f"Back to page 2: {snapshot.items[0]} to {snapshot.items[-1]}")


async def main():
    await create_tables()
    await seed_data()
    
    print("\n=== Keyset Pagination Demo ===\n")
    await keyset_paginate_all()
    
    print("\n=== Bidirectional Navigation Demo ===\n")
    await bidirectional_navigation()


if __name__ == "__main__":
    asyncio.run(main())
```

## Output

```
Created 10,000 events

=== Keyset Pagination Demo ===

Page 1: fetched 100 items (total: 100)
  First: Event(id=1, name=Event 0)
  Last: Event(id=100, name=Event 99)
Page 2: fetched 100 items (total: 200)
  First: Event(id=101, name=Event 100)
  Last: Event(id=200, name=Event 199)
Page 3: fetched 100 items (total: 300)
  First: Event(id=201, name=Event 200)
  Last: Event(id=300, name=Event 299)
Page 4: fetched 100 items (total: 400)
  First: Event(id=301, name=Event 300)
  Last: Event(id=400, name=Event 399)
Page 5: fetched 100 items (total: 500)
  First: Event(id=401, name=Event 400)
  Last: Event(id=500, name=Event 499)

(Stopping after 5 pages for demo)

=== Bidirectional Navigation Demo ===

Page 1: Event(id=1, name=Event 0) to Event(id=10, name=Event 9)
Page 2: Event(id=11, name=Event 10) to Event(id=20, name=Event 19)
Page 3: Event(id=21, name=Event 20) to Event(id=30, name=Event 29)

Back to page 2: Event(id=11, name=Event 10) to Event(id=20, name=Event 19)
```

## Key Concepts

### KeysetPageParams

```python
from pypaginator.core import KeysetPageParams

# First page (no cursor)
params = KeysetPageParams(limit=20)

# Next page (using cursor from previous response)
params = KeysetPageParams(limit=20, after=cursor)

# Previous page
params = KeysetPageParams(limit=20, before=cursor)
```

### Cursor Markers

```python
snapshot = await paginator.paginate_keyset(stmt, params, ...)

# Access markers
next_cursor = snapshot.next_marker  # Cursor for next page
prev_cursor = snapshot.prev_marker  # Cursor for previous page

# Check if more pages exist
has_more = snapshot.next_marker is not None
```

## FastAPI Integration

```python
from fastapi import FastAPI, Query
from pypaginator.core import KeysetPageParams
from pypaginator.engines.sql import SqlPaginator

app = FastAPI()

@app.get("/events")
async def list_events(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
    after: str | None = Query(None, description="Cursor for next page"),
    before: str | None = Query(None, description="Cursor for previous page"),
):
    paginator = SqlPaginator(session, clamp=False)
    
    params = KeysetPageParams(limit=limit, after=after, before=before)
    stmt = select(Event).order_by(Event.id)
    
    snapshot = await paginator.paginate_keyset(
        stmt, params, unique=False, scalars=True
    )
    
    return {
        "items": [EventSchema.from_orm(e) for e in snapshot.items],
        "next_cursor": snapshot.next_marker,
        "prev_cursor": snapshot.prev_marker,
        "has_next": snapshot.next_marker is not None,
        "has_previous": snapshot.prev_marker is not None,
    }
```

## When to Use Keyset Pagination

| Scenario | Recommendation |
|----------|----------------|
| Small dataset (<10k rows) | Offset pagination |
| Large dataset (>10k rows) | Keyset pagination |
| Random page access needed | Offset pagination |
| Sequential navigation only | Keyset pagination |
| Real-time data (insertions) | Keyset pagination |
| Analytics/reporting | Offset pagination |

## Best Practices

1. **Always use indexed columns** for ordering
2. **Use unique columns** (like ID) as the final sort key
3. **Include all sort columns** in the cursor
4. **Make cursors opaque** (encode/encrypt in production)
5. **Set reasonable limits** (max 100-500 per page)

## Next Steps

- [Offset Pagination](../user-guide/pagination/offset.md) - Standard pagination
- [Performance Guide](../user-guide/pagination/index.md) - Optimization tips
