# Basic Pagination Example

This example demonstrates basic offset pagination with SQLAlchemy.

## Complete Example

```python
"""Basic pagination example with SQLAlchemy."""
import asyncio
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from pypaginator.core import Page, PageParams
from pypaginator.query import paginate_entities_to_page


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./example.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"


async def create_tables():
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data():
    """Add sample data."""
    async with async_session() as session:
        # Check if data exists
        result = await session.execute(select(User).limit(1))
        if result.scalar():
            return
        
        # Create sample users
        users = [
            User(name=f"User {i}", email=f"user{i}@example.com")
            for i in range(1, 101)  # 100 users
        ]
        session.add_all(users)
        await session.commit()
        print(f"Created {len(users)} users")


async def paginate_users(page: int = 1, limit: int = 10) -> Page[User]:
    """Paginate users with offset pagination."""
    async with async_session() as session:
        # Build query with ordering
        stmt = select(User).order_by(User.id)
        
        # Create pagination parameters
        params = PageParams(page=page, limit=limit)
        
        # Execute pagination
        page_result = await paginate_entities_to_page(session, stmt, params)
        
        return page_result


async def main():
    """Run the example."""
    # Setup
    await create_tables()
    await seed_data()
    
    # Paginate first page
    print("\n=== Page 1 ===")
    page1 = await paginate_users(page=1, limit=10)
    print(f"Items: {page1.items}")
    print(f"Total: {page1.total}")
    print(f"Page: {page1.page} of {page1.total_pages}")
    print(f"Has next: {page1.has_next}")
    print(f"Has previous: {page1.has_previous}")
    
    # Paginate second page
    print("\n=== Page 2 ===")
    page2 = await paginate_users(page=2, limit=10)
    print(f"Items: {page2.items}")
    print(f"Page: {page2.page} of {page2.total_pages}")
    
    # Paginate last page
    print("\n=== Last Page ===")
    last_page = await paginate_users(page=10, limit=10)
    print(f"Items: {last_page.items}")
    print(f"Page: {last_page.page} of {last_page.total_pages}")
    print(f"Has next: {last_page.has_next}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Output

```
Created 100 users

=== Page 1 ===
Items: [User(id=1, name=User 1), User(id=2, name=User 2), ...]
Total: 100
Page: 1 of 10
Has next: True
Has previous: False

=== Page 2 ===
Items: [User(id=11, name=User 11), User(id=12, name=User 12), ...]
Page: 2 of 10

=== Last Page ===
Items: [User(id=91, name=User 91), User(id=92, name=User 92), ...]
Page: 10 of 10
Has next: False
```

## Key Concepts

### 1. Create Pagination Parameters

```python
params = PageParams(page=1, limit=10)
```

- `page`: 1-based page number
- `limit`: Items per page
- `offset`: Computed automatically as `(page - 1) * limit`

### 2. Build the Query

```python
stmt = select(User).order_by(User.id)
```

Always include `ORDER BY` for consistent pagination results.

### 3. Execute Pagination

```python
page = await paginate_entities_to_page(session, stmt, params)
```

Returns a `Page` object with:
- `items`: List of entities
- `total`: Total count
- `page`, `limit`: Current parameters
- `total_pages`, `has_next`, `has_previous`: Computed metadata

## Variations

### Return Tuple Instead of Page

```python
from pypaginator.query import paginate_entities

items, total = await paginate_entities(session, stmt, params)
```

### Paginate Raw Rows

```python
from pypaginator.query import paginate_rows_to_page

stmt = select(User.id, User.name)  # Select specific columns
page = await paginate_rows_to_page(session, stmt, params)
# page.items contains Row tuples, not User objects
```

### With Clamping

Automatically adjust out-of-range pages:

```python
page = await paginate_entities_to_page(
    session, stmt, params, clamp=True
)
# Requesting page 100 when max is 10 returns page 10
```

## Next Steps

- [Filtering Example](filtering.md) - Add filters to queries
- [FastAPI Example](fastapi.md) - Build a REST API
