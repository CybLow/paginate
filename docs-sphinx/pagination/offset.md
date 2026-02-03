# Offset Pagination

Offset pagination is the traditional approach where you specify a page number and items per page.

:::{tip} When to Use
Offset pagination is best for **small to medium datasets** (<100k rows) where users need page numbers in the UI and rarely go beyond page 10.
:::

## Overview

Offset pagination uses `LIMIT` and `OFFSET` SQL clauses:

```sql
-- Page 1
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 0;

-- Page 2
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 20;

-- Page 5
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 80;
```

## Basic Usage

### With SQLAlchemy

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import PageParams, paginate_entities

async def list_users(session: AsyncSession, page: int = 1, limit: int = 20):
    # Create pagination parameters
    params = PageParams(page=page, limit=limit)
    
    # Build query with ordering (required for consistent pagination)
    stmt = select(User).order_by(User.id)
    
    # Paginate
    result = await paginate_entities(session, stmt, params)
    
    return result
```

### Understanding the Result

```python
result = await paginate_entities(session, stmt, params)

# Access data
result.items       # List[User] - items for this page
result.total       # int - total count of all matching rows
result.page        # int - current page number
result.limit       # int - items per page
result.pages       # int - total number of pages
result.has_next    # bool - True if more pages exist
result.has_previous # bool - True if not on first page
```

## PageParams

### Creating Parameters

```python
from pypaginate import PageParams

# Default: page 1, 20 items
params = PageParams()

# Specific page and limit
params = PageParams(page=3, limit=50)

# Validation happens automatically
try:
    params = PageParams(page=0, limit=20)  # Raises error
except PaginationConfigurationError as e:
    print(e)  # "page must be greater than or equal to 1"
```

### Properties

```python
params = PageParams(page=3, limit=20)

params.page    # 3
params.limit   # 20
params.offset  # 40 (calculated as (page - 1) * limit)
```

### Immutability

`PageParams` is immutable (frozen dataclass):

```python
params = PageParams(page=1, limit=20)

# This raises an error:
# params.page = 2  # FrozenInstanceError

# Create a new instance instead:
new_params = params.model_copy(update={"page": 2})
```

## Pagination Functions

### paginate_entities

For ORM entities (full model objects):

```python
from pypaginate import paginate_entities

stmt = select(User).order_by(User.created_at.desc())
result = await paginate_entities(session, stmt, params)

# result.items contains User objects
for user in result.items:
    print(user.name)  # Access as ORM object
```

### paginate_rows

For raw rows (tuples or specific columns):

```python
from pypaginate import paginate_rows

stmt = select(User.id, User.name).order_by(User.id)
result = await paginate_rows(session, stmt, params)

# result.items contains Row objects
for row in result.items:
    print(row.id, row.name)
```

## Custom Count Queries

For complex queries with joins, automatic count may be slow. Provide a custom count:

:::{dropdown} Custom Count Query Example
:animate: fade-in

```python
from sqlalchemy import func, select

# Complex query with joins
stmt = (
    select(User)
    .join(Profile)
    .where(Profile.is_public == True)
    .order_by(User.name)
)

# Optimized count query
count_stmt = (
    select(func.count(User.id))
    .join(Profile)
    .where(Profile.is_public == True)
)

# Use custom count
result = await paginate_entities(
    session, 
    stmt, 
    params,
    count_statement=count_stmt
)
```
:::

## Ordering Requirements

:::{warning} Always include ORDER BY
Pagination without ordering produces inconsistent results. Always order your queries.
:::

```python
# Bad: No ordering - results may vary between pages
stmt = select(User)  # Don't do this!

# Good: Consistent ordering
stmt = select(User).order_by(User.id)

# Better: Order by unique column(s)
stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
```

## Handling Edge Cases

### Empty Results

```python
result = await paginate_entities(session, stmt, params)

if not result.items:
    # Handle empty page
    print("No results found")

# Page will still have metadata
print(result.total)  # 0
print(result.pages)  # 0
```

### Beyond Last Page

```python
# If page > total_pages, you get an empty items list
params = PageParams(page=999, limit=20)
result = await paginate_entities(session, stmt, params)

result.items  # []
result.total  # Actual total count
result.page   # 999
result.pages  # Actual number of pages
```

### Limit Bounds

```python
# Validate limit in your API
MAX_LIMIT = 100

@app.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=MAX_LIMIT),
):
    params = PageParams(page=page, limit=limit)
    ...
```

## Performance Considerations

### Deep Pagination Problem

Offset pagination becomes slower on deep pages:

```sql
-- Page 1: Fast
OFFSET 0 LIMIT 20

-- Page 1000: Slow - database must skip 19,980 rows
OFFSET 19980 LIMIT 20
```

:::{dropdown} Mitigation Strategies
:animate: fade-in

1. **Limit maximum page**: Don't allow pages beyond a reasonable number
2. **Use keyset pagination**: For deep pagination needs
3. **Cache counts**: Expensive count queries can be cached
4. **Use covering indexes**: Ensure ORDER BY columns are indexed

```python
# Limit maximum accessible pages
MAX_PAGE = 100

@app.get("/users")
async def list_users(
    page: int = Query(1, ge=1, le=MAX_PAGE),
    limit: int = Query(20, ge=1, le=100),
):
    params = PageParams(page=page, limit=limit)
    ...
```
:::

## Sync Usage

For synchronous SQLAlchemy:

```python
from sqlalchemy.orm import Session
from pypaginate import PageParams
from pypaginate.engines import SqlPaginator

def list_users_sync(session: Session, page: int = 1, limit: int = 20):
    params = PageParams(page=page, limit=limit)
    stmt = select(User).order_by(User.id)
    
    paginator = SqlPaginator()
    result = paginator.paginate_sync(session, stmt, params)
    
    return result.to_page()
```

## Next Steps

- [Keyset Pagination](keyset.md) - For large datasets
- [In-Memory Pagination](memory.md) - For collections
- [SQLAlchemy Integration](../integrations/sqlalchemy.md) - Advanced patterns
