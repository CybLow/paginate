# Basic Pagination

This example demonstrates offset pagination with in-memory data and SQLAlchemy.

## In-Memory Pagination

The simplest case -- paginate a Python list:

```python
from pypaginate import paginate, OffsetParams

data = list(range(1, 101))  # [1, 2, ..., 100]

# Page 1
page = paginate(data, OffsetParams(page=1, limit=10))
print(page.items)        # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(page.total)        # 100
print(page.page)         # 1
print(page.pages)        # 10
print(page.has_next)     # True
print(page.has_previous) # False

# Page 2
page = paginate(data, OffsetParams(page=2, limit=10))
print(page.items)        # [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
print(page.has_previous) # True

# Last page
page = paginate(data, OffsetParams(page=10, limit=10))
print(page.items)        # [91, 92, ..., 100]
print(page.has_next)     # False
```

### Iterating and indexing

`OffsetPage` supports iteration and indexing:

```python
from pypaginate import paginate, OffsetParams

page = paginate(["a", "b", "c"], OffsetParams(page=1, limit=10))

for item in page:
    print(item)  # a, b, c

print(page[0])   # "a"
print(len(page))  # 3
```

### Overflow handling

```python
from pypaginate import paginate, OffsetParams, OverflowStrategy

data = [1, 2, 3, 4, 5]

# Default: out-of-range page returns empty
page = paginate(data, OffsetParams(page=100, limit=2))
print(page.items)  # []

# Clamp: snap to last valid page
page = paginate(
    data,
    OffsetParams(page=100, limit=2),
    overflow=OverflowStrategy.CLAMP,
)
print(page.page)   # 3
print(page.items)  # [5]
```

## SQLAlchemy Async Pagination

Paginate a SQLAlchemy query with the async backend:

```python
import asyncio

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from pypaginate import OffsetParams, paginate
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend


# -- Models ---------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"


# -- Database setup -------------------------------------------------------

DATABASE_URL = "sqlite+aiosqlite:///./example.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        result = await session.execute(select(User).limit(1))
        if not result.scalar():
            session.add_all([User(name=f"User {i}") for i in range(1, 101)])
            await session.commit()


# -- Pagination -----------------------------------------------------------

async def list_users(page: int = 1, limit: int = 10):
    async with async_session() as session:
        query = select(User).order_by(User.id)
        backend = SQLAlchemyBackend(session)

        result = await paginate(query, OffsetParams(page=page, limit=limit), backend=backend)

        print(f"Page {result.page} of {result.pages} (total: {result.total})")
        for user in result:
            print(f"  {user}")
        print(f"Has next: {result.has_next}")


async def main():
    await setup()
    await list_users(page=1)
    await list_users(page=5)


if __name__ == "__main__":
    asyncio.run(main())
```

## SQLAlchemy Sync Pagination

For synchronous sessions, use `SyncSQLAlchemyBackend`:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyBackend


def list_users(session: Session, page: int = 1, limit: int = 10):
    query = select(User).order_by(User.id)
    backend = SyncSQLAlchemyBackend(session)

    result = paginate(query, OffsetParams(page=page, limit=limit), backend=backend)

    print(f"Page {result.page}: {result.items}")
```

## Custom Count Query

For complex joins where automatic `COUNT(*)` is expensive, provide a custom count query:

```python
from sqlalchemy import func, select
from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

# Main query with a costly join
query = select(User).join(Profile).where(Profile.verified == True)

# Fast custom count
count_query = select(func.count(User.id)).join(Profile).where(Profile.verified == True)

backend = SQLAlchemyBackend(session, count_query=count_query)
page = await paginate(query, OffsetParams(page=1, limit=20), backend=backend)
```

## Deduplication

When using `joinedload` or other join strategies that produce duplicate rows:

```python
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

backend = SQLAlchemyBackend(session, unique=True)
page = await paginate(query, OffsetParams(page=1, limit=20), backend=backend)
```

## Key Concepts

### OffsetParams

```python
from pypaginate import OffsetParams

params = OffsetParams(page=3, limit=20)
params.page    # 3
params.limit   # 20
params.offset  # 40  (computed: (page - 1) * limit)
```

- `page` must be >= 1
- `limit` must be between 1 and 1000

### OffsetPage

```python
# OffsetPage fields:
page.items         # list[T]   -- items for this page
page.total         # int       -- total count across all pages
page.page          # int       -- current page number
page.pages         # int       -- total number of pages
page.limit         # int       -- items per page
page.has_next      # bool
page.has_previous  # bool
```

## Next Steps

- [Filtering Example](filtering.md) -- Add filters to queries
- [Keyset Pagination](keyset.md) -- Cursor-based pagination for large datasets
- [FastAPI Example](fastapi.md) -- Build a REST API
