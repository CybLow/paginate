# First Steps

This tutorial walks you through building a complete paginated API with filtering and search using pypaginate and FastAPI.

## What You'll Build

A user management API with:

- Paginated user listing
- Filtering by status and age
- Full-text search
- Sorting by multiple fields

## Prerequisites

```bash
pip install pypaginate[all] fastapi uvicorn aiosqlite
```

## Step 1: Project Setup

Create a new directory and file structure:

```
my_api/
├── main.py
├── models.py
├── database.py
└── schemas.py
```

## Step 2: Database Setup

Create `database.py`:

```python
"""Database configuration with async SQLAlchemy."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Using SQLite for simplicity (use PostgreSQL in production)
DATABASE_URL = "sqlite+aiosqlite:///./users.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


async def get_session() -> AsyncSession:
    """Dependency for getting database sessions."""
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

## Step 3: Define Models

Create `models.py`:

```python
"""SQLAlchemy models."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    age: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
```

## Step 4: Create Schemas

Create `schemas.py`:

```python
"""Pydantic schemas for API responses."""

from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """User response schema."""
    
    id: int
    name: str
    email: EmailStr
    age: int
    status: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PagedUserResponse(BaseModel):
    """Paginated user response."""
    
    items: list[UserResponse]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_previous: bool
```

## Step 5: Build the API

Create `main.py`:

```python
"""FastAPI application with pypaginate."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import PageParams, paginate_entities
from pypaginate.integrations.fastapi import get_pagination_params

from database import get_session, init_db
from models import User
from schemas import PagedUserResponse, UserResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    await seed_data()
    yield


app = FastAPI(
    title="User API",
    description="Paginated user management API",
    lifespan=lifespan,
)


async def seed_data():
    """Seed database with sample data."""
    from database import async_session
    
    async with async_session() as session:
        # Check if data exists
        result = await session.execute(select(User).limit(1))
        if result.scalar():
            return
        
        # Create sample users
        users = [
            User(name="Alice Smith", email="alice@example.com", age=30, status="active", is_verified=True),
            User(name="Bob Johnson", email="bob@example.com", age=25, status="active", is_verified=False),
            User(name="Charlie Brown", email="charlie@example.com", age=35, status="inactive", is_verified=True),
            User(name="Diana Ross", email="diana@example.com", age=28, status="active", is_verified=True),
            User(name="Eve Wilson", email="eve@example.com", age=32, status="pending", is_verified=False),
            User(name="Frank Miller", email="frank@example.com", age=40, status="active", is_verified=True),
            User(name="Grace Lee", email="grace@example.com", age=22, status="active", is_verified=False),
            User(name="Henry Davis", email="henry@example.com", age=45, status="inactive", is_verified=True),
        ]
        
        session.add_all(users)
        await session.commit()


@app.get("/users", response_model=PagedUserResponse)
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    # Filters
    status: str | None = Query(None, description="Filter by status"),
    min_age: int | None = Query(None, description="Minimum age"),
    max_age: int | None = Query(None, description="Maximum age"),
    verified: bool | None = Query(None, description="Filter by verification status"),
    # Sorting
    sort_by: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
):
    """
    List users with pagination, filtering, and sorting.
    
    **Query Parameters:**
    
    - `page`: Page number (default: 1)
    - `limit`: Items per page (default: 20)
    - `status`: Filter by status (active, inactive, pending)
    - `min_age`: Minimum age filter
    - `max_age`: Maximum age filter
    - `verified`: Filter by verification status
    - `sort_by`: Field to sort by (name, email, age, created_at)
    - `order`: Sort order (asc, desc)
    """
    # Build base query
    stmt = select(User)
    
    # Apply filters
    if status:
        stmt = stmt.where(User.status == status)
    if min_age is not None:
        stmt = stmt.where(User.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(User.age <= max_age)
    if verified is not None:
        stmt = stmt.where(User.is_verified == verified)
    
    # Apply sorting
    sort_column = getattr(User, sort_by, User.created_at)
    if order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())
    
    # Paginate
    page = await paginate_entities(session, stmt, params)
    
    return PagedUserResponse(
        items=[UserResponse.model_validate(user) for user in page.items],
        total=page.total,
        page=page.page,
        limit=page.limit,
        pages=page.pages,
        has_next=page.has_next,
        has_previous=page.has_previous,
    )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single user by ID."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.model_validate(user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 6: Run and Test

### Start the Server

```bash
python main.py
# or
uvicorn main:app --reload
```

### Test the API

Open http://localhost:8000/docs for interactive Swagger UI.

**Example requests:**

```bash
# Basic pagination
curl "http://localhost:8000/users?page=1&limit=5"

# Filter by status
curl "http://localhost:8000/users?status=active"

# Filter by age range
curl "http://localhost:8000/users?min_age=25&max_age=35"

# Combined filters with sorting
curl "http://localhost:8000/users?status=active&min_age=25&sort_by=age&order=asc"
```

### Example Response

```json
{
  "items": [
    {
      "id": 7,
      "name": "Grace Lee",
      "email": "grace@example.com",
      "age": 22,
      "status": "active",
      "is_verified": false,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20,
  "pages": 1,
  "has_next": false,
  "has_previous": false
}
```

## Adding Search

Enhance the API with full-text search:

```python
from pypaginate.filters.search import MemorySearchService
from pypaginate.filters.search.options import SearchOptions

# Create search service
search_service = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email"],
        fuzzy_threshold=0.7,
    )
)

@app.get("/users/search")
async def search_users(
    q: str = Query(..., description="Search query"),
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
):
    """Search users by name or email."""
    # Get all users (in production, use SQL-based search)
    result = await session.execute(select(User))
    users = result.scalars().all()
    
    # Convert to dicts for search
    user_dicts = [
        {"id": u.id, "name": u.name, "email": u.email, "age": u.age}
        for u in users
    ]
    
    # Search
    matched = search_service.search(user_dicts, q)
    
    # Paginate results
    from pypaginate.engines import MemoryPaginator
    paginator = MemoryPaginator()
    page = paginator.paginate(matched, params).to_page()
    
    return {
        "items": page.items,
        "total": page.total,
        "page": page.page,
        "pages": page.pages,
    }
```

## What's Next?

You now have a fully functional paginated API! Here's what to explore next:

- [Pagination Guide](../user-guide/pagination/index.md) - Learn cursor-based pagination for large datasets
- [Filtering Guide](../user-guide/filtering/index.md) - Use JSON Logic for complex filters
- [SQLAlchemy Integration](../user-guide/integrations/sqlalchemy.md) - Advanced database patterns
- [FastAPI Integration](../user-guide/integrations/fastapi.md) - Custom dependencies and response models

## Complete Source Code

Find the complete example in the [examples directory](https://github.com/CybLow/pypaginate/tree/main/examples/fastapi_integration.py).
