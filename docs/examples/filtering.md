# Filtering

This example demonstrates declarative filtering with `FilterSpec`, `And`/`Or` groups, and the `FilterDep` FastAPI dependency.

## FilterSpec Basics

Each `FilterSpec` declares a single condition:

```python
from pypaginate import FilterSpec

# field = value (default operator is "eq")
FilterSpec(field="status", value="active")

# field >= value
FilterSpec(field="age", operator="gte", value=18)

# field contains substring
FilterSpec(field="name", operator="contains", value="alice")
```

## In-Memory Filtering

Apply filter specs to a Python list via the pipeline:

```python
from pypaginate import FilterSpec, OffsetParams
from pypaginate.adapters.memory import MemoryBackend, MemoryFilterBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline

products = [
    {"name": "iPhone 15", "category": "Electronics", "price": 999.99, "stock": 50},
    {"name": "MacBook Pro", "category": "Electronics", "price": 2499.99, "stock": 25},
    {"name": "AirPods Pro", "category": "Electronics", "price": 249.99, "stock": 100},
    {"name": "Python Book", "category": "Books", "price": 49.99, "stock": 200},
    {"name": "Standing Desk", "category": "Furniture", "price": 599.99, "stock": 15},
    {"name": "Headphones", "category": "Electronics", "price": 199.99, "stock": 0},
]

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
)

# Filter: Electronics only
page = pipeline.execute(
    products,
    OffsetParams(page=1, limit=10),
    filters=[FilterSpec(field="category", value="Electronics")],
)
print(f"Electronics: {len(page)} items")  # 4

# Filter: price between 50 and 300
page = pipeline.execute(
    products,
    OffsetParams(page=1, limit=10),
    filters=[
        FilterSpec(field="price", operator="gte", value=50),
        FilterSpec(field="price", operator="lte", value=300),
    ],
)
print(f"$50-$300: {len(page)} items")  # 2

# Filter: in stock (stock > 0)
page = pipeline.execute(
    products,
    OffsetParams(page=1, limit=10),
    filters=[FilterSpec(field="stock", operator="gt", value=0)],
)
print(f"In stock: {len(page)} items")  # 5
```

## Nested Groups with And / Or

Use `And()` and `Or()` for complex boolean logic:

```python
from pypaginate import And, Or, FilterSpec

# (category = "Electronics" OR category = "Books") AND price < 500
group = And(
    Or(
        FilterSpec(field="category", value="Electronics"),
        FilterSpec(field="category", value="Books"),
    ),
    FilterSpec(field="price", operator="lt", value=500),
)
```

Groups nest up to 5 levels deep for safety against runaway recursion.

### Nested group example

```python
from pypaginate import And, Or, FilterSpec

# Complex: (Electronics AND price < 300) OR (Books AND stock > 100)
group = Or(
    And(
        FilterSpec(field="category", value="Electronics"),
        FilterSpec(field="price", operator="lt", value=300),
    ),
    And(
        FilterSpec(field="category", value="Books"),
        FilterSpec(field="stock", operator="gt", value=100),
    ),
)
```

## Available Operators

| Operator | Description | Example Value |
|----------|-------------|---------------|
| `eq` | Equals | `"active"` |
| `ne` | Not equals | `"deleted"` |
| `gt` | Greater than | `100` |
| `gte` | Greater or equal | `18` |
| `lt` | Less than | `1000` |
| `lte` | Less or equal | `999.99` |
| `in` | Value in list | `["a", "b"]` |
| `not_in` | Value not in list | `["x", "y"]` |
| `contains` | Substring match | `"pro"` |
| `starts_with` | Starts with prefix | `"Air"` |
| `ends_with` | Ends with suffix | `".com"` |
| `like` | SQL LIKE pattern | `"A%"` |
| `ilike` | Case-insensitive LIKE | `"%pro%"` |
| `between` | Between two values | `[10, 100]` |
| `is_null` | Is None | (no value needed) |
| `is_not_null` | Is not None | (no value needed) |
| `regex` | Regex match | `"^[A-Z]"` |
| `empty` | Is None, `""`, or `[]` | (no value needed) |
| `not_empty` | Is not empty | (no value needed) |
| `exists` | Field exists | (no value needed) |

## SQLAlchemy Filtering

Use `SQLAlchemyFilterBackend` for database queries:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate import FilterSpec, OffsetParams
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend,
    SQLAlchemyFilterBackend,
)
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline


async def list_products(session: AsyncSession, category: str | None = None):
    query = select(Product).order_by(Product.id)

    filters = []
    if category:
        filters.append(FilterSpec(field="category", value=category))

    pipeline = AsyncPipeline(
        AsyncPaginator(SQLAlchemyBackend(session)),
        filter_backend=SQLAlchemyFilterBackend(),
    )

    return await pipeline.execute(
        query,
        OffsetParams(page=1, limit=20),
        filters=filters,
    )
```

## FastAPI FilterDep

`FilterDep` lets you declare filters as FastAPI query parameters. Subclass it, define fields with `FilterField`, and non-None values are automatically converted to `FilterSpec` objects via `.to_specs()`.

For a complete runnable example with `FilterDep`, `SortDep`, and `SearchDep`, see [FastAPI Integration](fastapi.md).

## Next Steps

- [Keyset Pagination](keyset.md) -- Cursor-based pagination
- [FastAPI Example](fastapi.md) -- Full app with filtering, sorting, and search
