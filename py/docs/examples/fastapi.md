# FastAPI Integration

This example demonstrates a complete FastAPI REST API using pypaginate's declarative dependencies: `OffsetDep`, `FilterDep`, `SortDep`, and `SearchDep`.

## Installation

```bash
pip install pypaginate[fastapi,sqlalchemy] uvicorn aiosqlite
```

## Complete Example

```python
"""Full FastAPI app with pypaginate v0.2 — pagination, filtering, sorting, search."""
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Float, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from pypaginate import OffsetPage, OffsetParams, paginate
from pypaginate.adapters.fastapi import (
    FilterDep,
    FilterField,
    OffsetDep,
    SearchDep,
    SortDep,
)
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend,
    SQLAlchemyFilterBackend,
    SQLAlchemySearchBackend,
    SQLAlchemySortBackend,
)
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline


# ── Database setup ───────────────────────────────────────

DATABASE_URL = "sqlite+aiosqlite:///./products.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(1000), default=None)
    category: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)


async def get_session():
    async with async_session() as session:
        yield session


# ── Schemas ──────────────────────────────────────────────

class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    category: str
    price: float
    stock: int


# ── Filter dependency ────────────────────────────────────

class ProductFilters(FilterDep):
    """Declarative product filters — non-None fields become FilterSpecs."""

    category: str | None = FilterField(None, operator="eq")
    min_price: float | None = FilterField(None, field="price", operator="gte")
    max_price: float | None = FilterField(None, field="price", operator="lte")
    in_stock: int | None = FilterField(None, field="stock", operator="gt")


# ── Pipeline factory ─────────────────────────────────────

def create_pipeline(session: AsyncSession) -> AsyncPipeline:
    return AsyncPipeline(
        AsyncPaginator(SQLAlchemyBackend(session)),
        filter_backend=SQLAlchemyFilterBackend(),
        sort_backend=SQLAlchemySortBackend(),
        search_backend=SQLAlchemySearchBackend(),
    )


# ── App ──────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(select(Product).limit(1))
        if not result.scalar():
            session.add_all([
                Product(name="iPhone 15", description="Latest iPhone",
                        category="Electronics", price=999.99, stock=50),
                Product(name="MacBook Pro", description="Professional laptop",
                        category="Electronics", price=2499.99, stock=25),
                Product(name="AirPods Pro", description="Noise-cancelling earbuds",
                        category="Electronics", price=249.99, stock=100),
                Product(name="Python Cookbook", description="Python recipes",
                        category="Books", price=49.99, stock=200),
                Product(name="Standing Desk", description="Ergonomic desk",
                        category="Furniture", price=599.99, stock=20),
                Product(name="Headphones", description="Over-ear headphones",
                        category="Electronics", price=199.99, stock=0),
            ])
            await session.commit()
    yield


app = FastAPI(title="Product API", lifespan=lifespan)


# ── Endpoints ────────────────────────────────────────────

@app.get("/products")
async def list_products(
    params: OffsetDep,
    filters: Annotated[ProductFilters, Query()],
    sort: Annotated[SortDep, Query()],
    search: Annotated[SearchDep, Query()],
    session: AsyncSession = Depends(get_session),
) -> OffsetPage[ProductSchema]:
    """
    List products with pagination, filtering, sorting, and search.

    **Pagination:** `?page=1&limit=20`
    **Filters:** `?category=Electronics&min_price=100&max_price=500`
    **Sorting:** `?sort=price` or `?sort=-price` (desc) or `?sort=name,-price`
    **Search:** `?q=iphone&search_fields=name,description`
    """
    query = select(Product)
    pipeline = create_pipeline(session)

    return await pipeline.execute(
        query,
        params,
        filters=filters,
        sorting=sort,
        search=search,
    )


@app.get("/products/{product_id}")
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
) -> ProductSchema:
    """Get a single product by ID."""
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running It

```bash
python app.py
# or
uvicorn app:app --reload
```

Open http://localhost:8000/docs for the interactive Swagger UI.

## API Usage

### Basic pagination

```bash
curl "http://localhost:8000/products?page=1&limit=3"
```

### Filtering

```bash
# By category
curl "http://localhost:8000/products?category=Electronics"

# By price range
curl "http://localhost:8000/products?min_price=100&max_price=500"

# In stock only
curl "http://localhost:8000/products?in_stock=1"

# Combined
curl "http://localhost:8000/products?category=Electronics&max_price=300&in_stock=1"
```

### Sorting

```bash
# Sort by price ascending
curl "http://localhost:8000/products?sort=price"

# Sort by price descending
curl "http://localhost:8000/products?sort=-price"

# Multi-column: category ASC, then price DESC
curl "http://localhost:8000/products?sort=category,-price"
```

### Search

```bash
# Search name and description for "pro"
curl "http://localhost:8000/products?q=pro&search_fields=name,description"
```

### Everything combined

```bash
curl "http://localhost:8000/products?category=Electronics&sort=-price&q=pro&search_fields=name&page=1&limit=5"
```

### Response format

```json
{
    "items": [
        {
            "id": 3,
            "name": "AirPods Pro",
            "description": "Noise-cancelling earbuds",
            "category": "Electronics",
            "price": 249.99,
            "stock": 100
        }
    ],
    "total": 1,
    "page": 1,
    "pages": 1,
    "limit": 5,
    "has_next": false,
    "has_previous": false
}
```

## How It Works

### Dependency injection

| Dependency | Query Parameters | Produces |
|-----------|------------------|----------|
| `OffsetDep` | `?page=1&limit=20` | `OffsetParams` |
| `CursorDep` | `?limit=20&after=...&before=...` | `CursorParams` |
| `FilterDep` subclass | Custom per subclass | `list[FilterSpec]` via `.to_specs()` |
| `SortDep` | `?sort=name,-price` | `list[SortSpec]` via `.to_specs()` |
| `SearchDep` | `?q=text&search_fields=a,b` | `SearchSpec` via `.to_spec()` |

### Pipeline auto-detection

The `AsyncPipeline.execute()` method auto-detects `FilterDep`, `SortDep`, and `SearchDep` objects and calls their conversion methods. You can also pass raw spec lists directly:

```python
from pypaginate import FilterSpec, SortSpec, SearchSpec, SortDirection

page = await pipeline.execute(
    query,
    params,
    filters=[FilterSpec(field="category", value="Electronics")],
    sorting=[SortSpec(field="price", direction=SortDirection.DESC)],
    search=SearchSpec(query="pro", fields=("name", "description")),
)
```

### Simple endpoint (no pipeline)

For endpoints that only need pagination (no filtering/sorting/search):

```python
@app.get("/users")
async def list_users(
    params: OffsetDep,
    session: AsyncSession = Depends(get_session),
) -> OffsetPage[UserSchema]:
    query = select(User).order_by(User.id)
    backend = SQLAlchemyBackend(session)
    return await paginate(query, params, backend=backend)
```

## Next Steps

- [Basic Pagination](basic-pagination.md) -- In-memory and SQLAlchemy basics
- [Filtering](filtering.md) -- Deep dive into FilterSpec and And/Or groups
- [Keyset Pagination](keyset.md) -- CursorParams for large datasets
