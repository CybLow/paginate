# FastAPI Integration

pypaginate provides first-class FastAPI integration with dependency injection and Pydantic models for seamless API development.

## Installation

```bash
uv add pypaginate[fastapi]
```

This installs pypaginate along with FastAPI and Pydantic dependencies.

## Quick Start

```python
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from pypaginate.integrations.fastapi import get_pagination_params, PagedResponse
from pypaginate.core import PageParams
from pypaginate.query import paginate_entities_to_page

app = FastAPI()

@app.get("/users", response_model=PagedResponse[UserSchema])
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
):
    stmt = select(User).order_by(User.created_at.desc())
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)
```

## Pagination Parameters

### Using `get_pagination_params`

The `get_pagination_params` function is a FastAPI dependency that extracts pagination parameters from query strings:

```python
from pypaginate.integrations.fastapi import get_pagination_params
from pypaginate.core import PageParams

@app.get("/items")
async def list_items(
    params: PageParams = Depends(get_pagination_params),
):
    # Access pagination parameters
    print(f"Page: {params.page}")      # Default: 1
    print(f"Limit: {params.limit}")    # Default: 20
    print(f"Offset: {params.offset}")  # Computed: (page - 1) * limit
```

**Query parameters:**

| Parameter | Type | Default | Constraints |
|-----------|------|---------|-------------|
| `page` | int | 1 | >= 1 |
| `limit` | int | 20 | >= 1, <= 100 |

**Example requests:**

```
GET /items                    # page=1, limit=20
GET /items?page=2            # page=2, limit=20
GET /items?page=3&limit=50   # page=3, limit=50
```

### Custom Pagination Parameters

Create custom pagination dependencies with different defaults or constraints:

```python
from fastapi import Query
from pypaginate.core import PageParams

def get_custom_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
) -> PageParams:
    return PageParams(page=page, limit=limit)

@app.get("/products")
async def list_products(
    params: PageParams = Depends(get_custom_pagination),
):
    # Uses custom defaults: page=1, limit=50, max=200
    ...
```

### Aliased Parameter Names

Use different query parameter names:

```python
from fastapi import Query
from pypaginate.core import PageParams

def get_aliased_pagination(
    offset: int = Query(0, ge=0, alias="skip"),
    count: int = Query(20, ge=1, le=100, alias="take"),
) -> PageParams:
    # Convert offset/count to page/limit
    page = (offset // count) + 1
    return PageParams(page=page, limit=count)

@app.get("/data")
async def get_data(
    params: PageParams = Depends(get_aliased_pagination),
):
    # Query: /data?skip=40&take=20
    ...
```

## Response Models

### Using `PagedResponse`

`PagedResponse` is a Pydantic model that wraps pagination results for proper OpenAPI schema generation:

```python
from pypaginate.integrations.fastapi import PagedResponse
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users", response_model=PagedResponse[UserSchema])
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
):
    stmt = select(User).order_by(User.id)
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)
```

**Response structure:**

```json
{
    "items": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
    ],
    "total": 100,
    "page": 1,
    "limit": 20
}
```

### Custom Response Models

Create custom response models with additional fields:

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class CustomPagedResponse(BaseModel, Generic[T]):
    """Extended pagination response with navigation helpers."""
    
    items: list[T]
    total: int
    page: int
    limit: int
    has_next: bool = Field(description="Whether more pages exist")
    has_previous: bool = Field(description="Whether previous pages exist")
    total_pages: int = Field(description="Total number of pages")
    
    @classmethod
    def from_page(cls, page):
        total_pages = (page.total + page.limit - 1) // page.limit
        return cls(
            items=list(page.items),
            total=page.total,
            page=page.page,
            limit=page.limit,
            has_next=page.page < total_pages,
            has_previous=page.page > 1,
            total_pages=total_pages,
        )

@app.get("/users", response_model=CustomPagedResponse[UserSchema])
async def list_users(...):
    page = await paginate_entities_to_page(session, stmt, params)
    return CustomPagedResponse.from_page(page)
```

## Complete Example

Here's a complete FastAPI application with pagination:

```python
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from pypaginate.integrations.fastapi import get_pagination_params, PagedResponse
from pypaginate.core import PageParams
from pypaginate.query import paginate_entities_to_page

# Database setup
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session

# Pydantic schemas
class UserCreate(BaseModel):
    name: str
    email: str

class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="User API")

@app.get("/users", response_model=PagedResponse[UserSchema])
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    search: str | None = Query(None, description="Search by name"),
):
    """List users with pagination and optional search."""
    stmt = select(User).order_by(User.id)
    
    if search:
        stmt = stmt.where(User.name.ilike(f"%{search}%"))
    
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)

@app.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single user by ID."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

## Filtering and Sorting

Combine pagination with filtering and sorting:

```python
from pypaginate.sorting import SqlSortAdapter
from pypaginate.filters.predicates import FilterEngine

@app.get("/products", response_model=PagedResponse[ProductSchema])
async def list_products(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    # Filters
    category: str | None = Query(None),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    # Sorting
    sort_by: str = Query("created_at", regex="^(name|price|created_at)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
):
    """List products with filtering, sorting, and pagination."""
    stmt = select(Product)
    
    # Apply filters
    if category:
        stmt = stmt.where(Product.category == category)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)
    
    # Apply sorting
    column = getattr(Product, sort_by)
    order_expr = SqlSortAdapter.build_order_expression(
        column=column,
        descending=(order == "desc"),
    )
    stmt = stmt.order_by(order_expr)
    
    # Paginate
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)
```

## Error Handling

Handle pagination-related errors gracefully:

```python
from pypaginate.exceptions import PaginationConfigurationError

@app.exception_handler(PaginationConfigurationError)
async def pagination_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": "pagination_error"},
    )
```

## OpenAPI Documentation

The integration automatically generates proper OpenAPI documentation:

- Query parameters are documented with types and constraints
- Response schemas show the paginated structure
- Descriptions are included from docstrings

Access your API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Best Practices

1. **Always use response models** for proper OpenAPI generation
2. **Set reasonable limits** to prevent excessive data fetching
3. **Add caching headers** for paginated responses
4. **Include sorting** for consistent results across pages
5. **Validate sort fields** against an allowed list
6. **Use async sessions** for non-blocking database access

## See Also

- [SQLAlchemy Integration](sqlalchemy.md) - Database-level pagination
- [Basic Pagination](../pagination/offset.md) - Pagination fundamentals
- [Filtering](../filtering/index.md) - Add filters to your API
