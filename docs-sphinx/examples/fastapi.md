# FastAPI Integration Example

This example demonstrates a complete FastAPI REST API with pagination, filtering, sorting, and search.

## Complete Example

```python
"""FastAPI integration example with pypaginate."""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, DateTime, Float, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from pypaginate.core import PageParams
from pypaginate.query import paginate_entities_to_page
from pypaginate.integrations.fastapi import get_pagination_params, PagedResponse
from pypaginate.sorting import SqlSortAdapter


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./api.db"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic schemas
class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: str | None
    category: str
    price: float
    stock: int
    created_at: datetime


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category: str
    price: float
    stock: int = 0


# Dependencies
async def get_session():
    async with async_session() as session:
        yield session


# Lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        result = await session.execute(select(Product).limit(1))
        if not result.scalar():
            products = [
                Product(name="iPhone 15", description="Latest iPhone", 
                       category="Electronics", price=999.99, stock=50),
                Product(name="MacBook Pro", description="Professional laptop",
                       category="Electronics", price=2499.99, stock=25),
                Product(name="Python Cookbook", description="Python recipes",
                       category="Books", price=49.99, stock=100),
                Product(name="Standing Desk", description="Ergonomic desk",
                       category="Furniture", price=599.99, stock=20),
            ]
            session.add_all(products)
            await session.commit()
    
    yield
    # Shutdown: cleanup if needed


# FastAPI app
app = FastAPI(
    title="Product API",
    description="Example API with pypaginate",
    lifespan=lifespan,
)


@app.get("/products", response_model=PagedResponse[ProductSchema])
async def list_products(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    # Filters
    category: Annotated[str | None, Query(description="Filter by category")] = None,
    min_price: Annotated[float | None, Query(ge=0, description="Minimum price")] = None,
    max_price: Annotated[float | None, Query(ge=0, description="Maximum price")] = None,
    in_stock: Annotated[bool | None, Query(description="Only in-stock items")] = None,
    # Search
    search: Annotated[str | None, Query(description="Search in name/description")] = None,
    # Sorting
    sort_by: Annotated[str, Query(
        regex="^(name|price|created_at|stock)$",
        description="Field to sort by"
    )] = "created_at",
    order: Annotated[str, Query(
        regex="^(asc|desc)$",
        description="Sort order"
    )] = "desc",
):
    """
    List products with pagination, filtering, sorting, and search.
    
    **Pagination:**
    - `page`: Page number (default: 1)
    - `limit`: Items per page (default: 20, max: 100)
    
    **Filters:**
    - `category`: Exact category match
    - `min_price`, `max_price`: Price range
    - `in_stock`: Only products with stock > 0
    
    **Search:**
    - `search`: Search in name and description
    
    **Sorting:**
    - `sort_by`: name, price, created_at, stock
    - `order`: asc or desc
    """
    stmt = select(Product)
    
    # Apply filters
    if category:
        stmt = stmt.where(Product.category == category)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)
    if in_stock:
        stmt = stmt.where(Product.stock > 0)
    
    # Apply search
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            Product.name.ilike(search_term) | 
            Product.description.ilike(search_term)
        )
    
    # Apply sorting
    column = getattr(Product, sort_by)
    order_expr = SqlSortAdapter.build_order_expression(
        column=column,
        descending=(order == "desc"),
        nulls_position="last",
    )
    stmt = stmt.order_by(order_expr)
    
    # Paginate
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)


@app.get("/products/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single product by ID."""
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@app.post("/products", response_model=ProductSchema, status_code=201)
async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new product."""
    product = Product(**data.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running the Example

```bash
# Install dependencies
uv add pypaginate[fastapi] uvicorn aiosqlite

# Run the server
python examples/fastapi_example.py

# Or with uvicorn
uvicorn examples.fastapi_example:app --reload
```

## API Usage

### List Products

```bash
# Basic pagination
curl "http://localhost:8000/products?page=1&limit=10"

# With filters
curl "http://localhost:8000/products?category=Electronics&min_price=100"

# With search
curl "http://localhost:8000/products?search=iPhone"

# With sorting
curl "http://localhost:8000/products?sort_by=price&order=asc"

# Combined
curl "http://localhost:8000/products?category=Electronics&sort_by=price&order=desc&page=1&limit=5"
```

### Response Format

```json
{
    "items": [
        {
            "id": 1,
            "name": "iPhone 15",
            "description": "Latest iPhone",
            "category": "Electronics",
            "price": 999.99,
            "stock": 50,
            "created_at": "2024-01-15T10:30:00"
        }
    ],
    "total": 25,
    "page": 1,
    "limit": 10
}
```

### OpenAPI Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## Key Features Demonstrated

1. **Dependency Injection** - `get_pagination_params` for query params
2. **Response Models** - `PagedResponse[ProductSchema]` for OpenAPI
3. **Filtering** - Multiple filter parameters
4. **Search** - ILIKE search across fields
5. **Sorting** - Dynamic sort with validation
6. **Validation** - Query parameter constraints

## Next Steps

- [Keyset Pagination](keyset.md) - Handle large datasets
- [SQLAlchemy Integration](../integrations/sqlalchemy.md) - Advanced patterns
