# Keyset (Cursor) Pagination

This example demonstrates keyset pagination using `CursorParams` and `CursorPage` for efficient handling of large datasets.

## Why Keyset Pagination?

Offset pagination gets slower as the offset grows:

```sql
-- Offset: database must scan 100,000 rows before returning 20
SELECT * FROM events ORDER BY id LIMIT 20 OFFSET 100000;

-- Keyset: uses index, constant performance regardless of position
SELECT * FROM events WHERE id > 100000 ORDER BY id LIMIT 20;
```

Use keyset pagination for:

- Large datasets (>10k rows)
- Real-time feeds (new rows inserted frequently)
- Infinite scroll UIs

## CursorParams and CursorPage

```python
from pypaginate import CursorParams, CursorPage

# First page (no cursor)
params = CursorParams(limit=20)

# Next page (using cursor from previous response)
params = CursorParams(limit=20, after="eyJpZCI6IDEwMH0=")

# Previous page
params = CursorParams(limit=20, before="eyJpZCI6IDgxfQ==")
```

`CursorPage` has no `total` or `page` -- those are offset-only concepts:

```python
# CursorPage fields:
page.items              # list[T]
page.limit              # int
page.has_next           # bool
page.has_previous       # bool
page.next_cursor        # str | None
page.previous_cursor    # str | None
```

## SQLAlchemy Cursor Pagination

Requires `pypaginate[sqlalchemy]` (includes `sqlakeyset`):

```bash
pip install pypaginate[sqlalchemy]
```

```python
import asyncio

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from pypaginate import CursorParams, paginate
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend


# -- Models ---------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))

    def __repr__(self) -> str:
        return f"Event(id={self.id}, name={self.name})"


# -- Database setup -------------------------------------------------------

DATABASE_URL = "sqlite+aiosqlite:///./keyset.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        result = await session.execute(select(Event).limit(1))
        if not result.scalar():
            for batch in range(10):
                events = [
                    Event(name=f"Event {batch * 1000 + i}")
                    for i in range(1000)
                ]
                session.add_all(events)
            await session.commit()
            print("Created 10,000 events")


# -- Cursor pagination ----------------------------------------------------

async def paginate_forward():
    """Walk forward through events using cursor pagination."""
    async with async_session() as session:
        # Query MUST have ORDER BY (sqlakeyset requirement)
        query = select(Event).order_by(Event.id)
        backend = SQLAlchemyCursorBackend(session)

        params = CursorParams(limit=100)
        page_num = 1

        while True:
            page = await paginate(query, params, backend=backend)

            print(f"Page {page_num}: {len(page)} items", end="")
            if page.items:
                print(f" [{page.items[0]} ... {page.items[-1]}]")
            else:
                print()

            if not page.has_next:
                print("Reached end of data")
                break

            # Use next_cursor to get the next page
            params = CursorParams(limit=100, after=page.next_cursor)
            page_num += 1

            if page_num > 5:
                print("(Stopping after 5 pages for demo)")
                break


async def bidirectional():
    """Navigate forward and backward."""
    async with async_session() as session:
        query = select(Event).order_by(Event.id)
        backend = SQLAlchemyCursorBackend(session)

        # Go forward 3 pages
        params = CursorParams(limit=10)
        cursors = []

        print("=== Forward ===")
        for i in range(3):
            page = await paginate(query, params, backend=backend)
            print(f"Page {i + 1}: {page.items[0]} to {page.items[-1]}")
            cursors.append(page.previous_cursor)

            if page.has_next:
                params = CursorParams(limit=10, after=page.next_cursor)

        # Go back one page
        print("\n=== Backward ===")
        params = CursorParams(limit=10, before=cursors[-1])
        page = await paginate(query, params, backend=backend)
        print(f"Back to: {page.items[0]} to {page.items[-1]}")


async def main():
    await setup()
    print("\n=== Cursor Pagination Demo ===\n")
    await paginate_forward()
    print()
    await bidirectional()


if __name__ == "__main__":
    asyncio.run(main())
```

## Sync Cursor Pagination

For synchronous sessions:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyCursorBackend


def list_events(session: Session):
    query = select(Event).order_by(Event.id)
    backend = SyncSQLAlchemyCursorBackend(session)

    # Note: sync cursor uses .fetch_page() directly (no paginate() dispatch)
    items, next_cursor, prev_cursor = backend.fetch_page(
        query,
        limit=20,
        after=None,
    )
    print(f"Items: {len(items)}, next: {next_cursor}")
```

## FastAPI with CursorDep

```python
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import CursorPage, paginate
from pypaginate.adapters.fastapi import CursorDep
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend

app = FastAPI()


@app.get("/events")
async def list_events(
    params: CursorDep,
    session: AsyncSession = Depends(get_session),
) -> CursorPage[dict]:
    query = select(Event).order_by(Event.id)
    backend = SQLAlchemyCursorBackend(session)
    return await paginate(query, params, backend=backend)
```

Request: `GET /events?limit=20&after=eyJpZCI6IDEwMH0=`

`CursorDep` parses `limit`, `after`, and `before` from query parameters automatically.

## When to Use Keyset vs Offset

| Scenario | Recommendation |
|----------|----------------|
| Small dataset (<10k rows) | Offset -- simpler, supports random page access |
| Large dataset (>10k rows) | Keyset -- consistent performance |
| Random page access needed | Offset -- keyset only supports next/previous |
| Sequential navigation | Keyset -- ideal for this |
| Real-time data (insertions) | Keyset -- no skipped/duplicate rows |
| Analytics/reporting | Offset -- page numbers useful for UIs |

## Best Practices

1. **Always include ORDER BY** -- sqlakeyset requires it
2. **Use indexed columns** for the sort key
3. **End with a unique column** (e.g., `id`) as the final sort key for deterministic ordering
4. **Cursors are opaque** -- clients should not parse or construct them
5. **Set reasonable limits** -- max 100-500 per page

## Next Steps

- [Basic Pagination](basic-pagination.md) -- Offset pagination
- [FastAPI Example](fastapi.md) -- Full app with all features
