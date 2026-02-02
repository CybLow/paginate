# SQLAlchemy Integration

pypaginate provides deep integration with SQLAlchemy 2.0+, offering async pagination, multiple strategies, and query optimization.

## Overview

The SQLAlchemy integration includes:

- **Async pagination** with `AsyncSession`
- **Offset-based pagination** for standard use cases
- **Keyset pagination** for large datasets
- **Automatic count queries** with optimization
- **Deduplication support** for joined queries

## Basic Usage

### Paginate Entities

The most common pattern is paginating ORM entities:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.query import paginate_entities, paginate_entities_to_page
from pypaginate.core import PageParams

async def list_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc())
    params = PageParams(page=1, limit=20)
    
    # Returns (items, total) tuple
    items, total = await paginate_entities(session, stmt, params)
    return items

async def list_users_page(session: AsyncSession) -> Page[User]:
    stmt = select(User).order_by(User.created_at.desc())
    params = PageParams(page=1, limit=20)
    
    # Returns a Page object
    page = await paginate_entities_to_page(session, stmt, params)
    return page
```

### Paginate Rows

For raw column selections:

```python
from pypaginate.query import paginate_rows, paginate_rows_to_page

async def list_user_summaries(session: AsyncSession):
    stmt = select(User.id, User.name, User.email).order_by(User.id)
    params = PageParams(page=1, limit=20)
    
    # Returns raw row tuples
    rows, total = await paginate_rows(session, stmt, params)
    
    # Or as a Page
    page = await paginate_rows_to_page(session, stmt, params)
```

## Pagination Functions

### `paginate_entities`

Returns ORM entities with total count:

```python
async def paginate_entities(
    session: AsyncSession,
    query: Select,
    params: PageParams,
    *,
    count_query: Select | None = None,
    unique: bool = False,
    clamp: bool = False,
) -> tuple[list[T], int]:
    ...
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session` | AsyncSession | SQLAlchemy async session |
| `query` | Select | SQLAlchemy select statement |
| `params` | PageParams | Pagination parameters |
| `count_query` | Select | Optional optimized count query |
| `unique` | bool | Deduplicate results (for joins) |
| `clamp` | bool | Clamp page to valid range |

### `paginate_entities_to_page`

Returns a `Page` object with metadata:

```python
page = await paginate_entities_to_page(session, stmt, params)

print(page.items)       # List of entities
print(page.total)       # Total count
print(page.page)        # Current page number
print(page.limit)       # Items per page
print(page.total_pages) # Computed total pages
print(page.has_next)    # Whether next page exists
print(page.has_previous)# Whether previous page exists
```

### `paginate_rows` / `paginate_rows_to_page`

Same as entity functions but for raw row tuples.

## Advanced Usage

### Custom Count Query

For complex queries, provide an optimized count query:

```python
from sqlalchemy import func, select

# Main query with joins and filters
stmt = (
    select(Order)
    .join(Order.customer)
    .join(Order.items)
    .where(Order.status == "completed")
    .options(selectinload(Order.items))
)

# Optimized count (no joins needed for count)
count_stmt = (
    select(func.count(Order.id))
    .where(Order.status == "completed")
)

items, total = await paginate_entities(
    session, 
    stmt, 
    params,
    count_query=count_stmt,
)
```

### Deduplication with `unique`

When using joins that may produce duplicate rows:

```python
# Query with one-to-many join
stmt = (
    select(Author)
    .join(Author.books)
    .where(Book.genre == "fiction")
)

# Deduplicate authors
items, total = await paginate_entities(
    session,
    stmt,
    params,
    unique=True,  # Remove duplicate authors
)
```

### Page Clamping with `clamp`

Automatically adjust out-of-range page requests:

```python
# If total is 100 and limit is 20, max page is 5
# Requesting page 10 will be clamped to page 5

page = await paginate_entities_to_page(
    session,
    stmt,
    PageParams(page=10, limit=20),
    clamp=True,  # Clamp to valid range
)
# page.page will be 5, not 10
```

## Using SqlPaginator Directly

For more control, use `SqlPaginator` directly:

```python
from pypaginate.engines.sql import SqlPaginator
from pypaginate.core.context import PaginationContext

async def advanced_pagination(session: AsyncSession):
    # Create paginator
    paginator = SqlPaginator(session, clamp=True)
    
    # Build context
    context = PaginationContext(
        params=PageParams(page=1, limit=20),
        count_query=None,
        unique=False,
    )
    
    # Execute pagination
    stmt = select(User).order_by(User.id)
    snapshot = await paginator.paginate(stmt, context, scalars=True)
    
    return snapshot.items, snapshot.total
```

## Keyset Pagination

For large datasets, use keyset (cursor) pagination:

```python
from pypaginate.core import KeysetPageParams
from pypaginate.engines.sql import SqlPaginator

async def keyset_pagination(session: AsyncSession):
    paginator = SqlPaginator(session, clamp=False)
    
    # First page
    params = KeysetPageParams(limit=20)
    stmt = select(User).order_by(User.id)
    
    snapshot = await paginator.paginate_keyset(
        stmt, 
        params, 
        unique=False,
        scalars=True,
    )
    
    # Get cursor for next page
    next_cursor = snapshot.next_marker
    
    # Subsequent pages use cursor
    if next_cursor:
        params = KeysetPageParams(limit=20, after=next_cursor)
        next_snapshot = await paginator.paginate_keyset(
            stmt, params, unique=False, scalars=True
        )
```

## Query Building Patterns {#filtering}

### With Filtering

```python
from pypaginate.filters.predicates import FilterEngine

async def filtered_pagination(
    session: AsyncSession,
    filters: dict,
):
    stmt = select(Product)
    
    # Apply filters
    engine = FilterEngine()
    if filters:
        conditions = engine.build_conditions(Product, filters)
        stmt = stmt.where(*conditions)
    
    # Always add ordering for consistent pagination
    stmt = stmt.order_by(Product.id)
    
    return await paginate_entities_to_page(
        session, stmt, PageParams(page=1, limit=20)
    )
```

### With Sorting

```python
from pypaginate.sorting import SqlSortAdapter

async def sorted_pagination(
    session: AsyncSession,
    sort_field: str = "created_at",
    descending: bool = True,
):
    stmt = select(Product)
    
    # Apply sorting
    column = getattr(Product, sort_field)
    order_expr = SqlSortAdapter.build_order_expression(
        column=column,
        descending=descending,
        nulls_position="last",
    )
    stmt = stmt.order_by(order_expr)
    
    return await paginate_entities_to_page(
        session, stmt, PageParams(page=1, limit=20)
    )
```

### With Search

```python
from pypaginate.filters.search import SqlSearchService, SearchOptions

async def search_pagination(
    session: AsyncSession,
    query: str | None = None,
):
    stmt = select(Product).order_by(Product.id)
    
    if query:
        search_service = SqlSearchService(
            model=Product,
            search_fields=["name", "description"],
            options=SearchOptions(fuzzy=True),
        )
        stmt = search_service.apply_search(stmt, query)
    
    return await paginate_entities_to_page(
        session, stmt, PageParams(page=1, limit=20)
    )
```

## Relationships and Eager Loading

### Avoiding N+1 Queries

Use SQLAlchemy's loading strategies:

```python
from sqlalchemy.orm import selectinload, joinedload

stmt = (
    select(Order)
    .options(
        selectinload(Order.items),      # Load items in separate query
        joinedload(Order.customer),     # Load customer in same query
    )
    .order_by(Order.created_at.desc())
)

page = await paginate_entities_to_page(session, stmt, params)
# page.items[0].items and page.items[0].customer are loaded
```

### With Joined Filters

```python
# Filter by related entity, but only return parent
stmt = (
    select(Author)
    .join(Author.books)
    .where(Book.published_year >= 2020)
    .options(selectinload(Author.books))
)

# Use unique to deduplicate authors with multiple matching books
page = await paginate_entities_to_page(
    session, stmt, params, unique=True
)
```

## Performance Tips

### 1. Index Your Sort Columns

```python
from sqlalchemy import Index

# Create index for common sort patterns
Index("idx_user_created_at", User.created_at.desc())
```

### 2. Use Keyset for Large Offsets

```python
# Offset pagination degrades for large page numbers
# Page 1000 with limit 20 = OFFSET 19980

# Use keyset pagination instead
page = await paginator.paginate_keyset(stmt, keyset_params, ...)
```

### 3. Optimize Count Queries

```python
# Provide simple count query for complex main queries
count_stmt = select(func.count()).select_from(User)
page = await paginate_entities_to_page(
    session, stmt, params, count_query=count_stmt
)
```

### 4. Limit Eager Loading

```python
# Only load what you need
stmt = select(User).options(
    load_only(User.id, User.name, User.email),  # Limit columns
    selectinload(User.profile),                   # Load specific relations
)
```

## Error Handling

```python
from pypaginate.exceptions import (
    PaginationConfigurationError,
    InvalidPageError,
)

try:
    page = await paginate_entities_to_page(session, stmt, params)
except PaginationConfigurationError as e:
    # Handle configuration errors
    logger.error(f"Pagination config error: {e}")
except InvalidPageError as e:
    # Handle invalid page requests
    logger.warning(f"Invalid page: {e}")
```

## Best Practices

1. **Always include ORDER BY** for consistent pagination
2. **Use `unique=True`** when joining one-to-many relationships
3. **Consider keyset pagination** for large datasets (>10k rows)
4. **Provide count queries** for complex queries with joins
5. **Use `clamp=True`** to gracefully handle out-of-range pages
6. **Index sort columns** for better performance
7. **Limit page size** to prevent excessive memory usage

## See Also

- [FastAPI Integration](fastapi.md) - Web framework integration
- [Offset Pagination](../pagination/offset.md) - Standard pagination
- [Keyset Pagination](../pagination/keyset.md) - Cursor-based pagination
- [Filtering](../filtering/index.md) - Query filtering
