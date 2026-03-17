# Offset Pagination

Offset pagination uses page numbers and items-per-page to slice results. It maps to SQL `OFFSET`/`LIMIT`.

:::{tip} When to Use
Offset pagination is best for **small to medium datasets** (<100k rows) where users need page numbers in the UI and rarely go beyond page 10.
:::

## Basic Usage

### In-Memory (Auto-Detected)

Pass a list and `OffsetParams` to `paginate()`:

```python
from pypaginate import paginate, OffsetParams

users = [{"id": i, "name": f"User {i}"} for i in range(100)]

page = paginate(users, OffsetParams(page=1, limit=20))

page.items         # first 20 users
page.total         # 100
page.page          # 1
page.pages         # 5
page.has_next      # True
page.has_previous  # False
```

No backend needed -- `paginate()` auto-detects Python sequences.

### SQLAlchemy (Async)

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

async def list_users(session: AsyncSession, page: int = 1, limit: int = 20):
    backend = SQLAlchemyBackend(session)
    stmt = select(User).order_by(User.id)
    params = OffsetParams(page=page, limit=limit)

    result = await paginate(stmt, params, backend=backend)
    return result
```

### SQLAlchemy (Sync)

```python
from sqlalchemy.orm import Session
from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyBackend

def list_users(session: Session, page: int = 1, limit: int = 20):
    backend = SyncSQLAlchemyBackend(session)
    stmt = select(User).order_by(User.id)

    return paginate(stmt, OffsetParams(page=page, limit=limit), backend=backend)
```

## OffsetParams

### Creating Parameters

```python
from pypaginate import OffsetParams

# Defaults: page=1, limit=20
params = OffsetParams()

# Specific page and limit
params = OffsetParams(page=3, limit=50)

# Validation is automatic
from pypaginate import ValidationError

try:
    params = OffsetParams(page=0)  # page must be >= 1
except ValidationError as e:
    print(e)

try:
    params = OffsetParams(limit=0)  # limit must be >= 1
except ValidationError as e:
    print(e)

try:
    params = OffsetParams(limit=5000)  # limit must not exceed 1000
except ValidationError as e:
    print(e)
```

### Computed Offset

```python
params = OffsetParams(page=3, limit=20)

params.page    # 3
params.limit   # 20
params.offset  # 40 = (3 - 1) * 20
```

### Immutability

`OffsetParams` is frozen (immutable Pydantic model):

```python
params = OffsetParams(page=1, limit=20)
# params.page = 2  # raises ValidationError

# Create a new instance instead:
new_params = params.model_copy(update={"page": 2})
```

### Clamping

Clamp page to valid bounds:

```python
params = OffsetParams(page=999, limit=20)
clamped = params.clamp(total=100)
# clamped.page == 5 (max page for 100 items with limit=20)
```

## OffsetPage

### Result Fields

```python
page = paginate(items, OffsetParams(page=2, limit=20))

page.items         # list[T] -- items for this page
page.total         # int -- total count across all pages
page.page          # int -- current page number (2)
page.pages         # int -- total number of pages
page.limit         # int -- items per page (20)
page.has_next      # bool -- True if page < pages
page.has_previous  # bool -- True if page > 1
```

### Iteration and Indexing

```python
# Iterate
for user in page:
    print(user)

# Index
first = page[0]

# Length
count = len(page)  # items on this page
```

## Custom Count Queries

For complex queries with joins, provide a custom count query for better performance:

```python
from sqlalchemy import func, select
from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

# Complex query
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

backend = SQLAlchemyBackend(session, count_query=count_stmt)
page = await paginate(stmt, OffsetParams(page=1, limit=20), backend=backend)
```

## Deduplication

For queries with joins that may produce duplicates, enable deduplication:

```python
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend

backend = SQLAlchemyBackend(session, unique=True)
page = await paginate(stmt, params, backend=backend)
```

## Overflow Strategies

```python
from pypaginate import paginate, OffsetParams, OverflowStrategy

items = list(range(50))  # 50 items

# EMPTY (default): return empty page for out-of-range requests
page = paginate(items, OffsetParams(page=999, limit=20), overflow=OverflowStrategy.EMPTY)
page.items  # []
page.total  # 50
page.page   # 999

# CLAMP: clamp to the last valid page
page = paginate(items, OffsetParams(page=999, limit=20), overflow=OverflowStrategy.CLAMP)
page.items  # last 10 items
page.total  # 50
page.page   # 3
```

## Ordering Requirements

:::{warning} Always include ORDER BY
Pagination without ordering produces inconsistent results across pages.
:::

```python
# Bad: no ordering
stmt = select(User)

# Good: consistent ordering
stmt = select(User).order_by(User.id)

# Better: unique ordering for deterministic pages
stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
```

## Handling Edge Cases

### Empty Results

```python
page = paginate([], OffsetParams(page=1, limit=20))

page.items  # []
page.total  # 0
page.pages  # 0
page.has_next  # False
```

### Single Page

```python
items = [1, 2, 3]
page = paginate(items, OffsetParams(page=1, limit=20))

page.total  # 3
page.pages  # 1
page.has_next  # False
```

## Performance

### Deep Pagination Problem

Offset pagination becomes slower on deep pages because the database must skip rows:

```sql
-- Page 1: fast
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 0;

-- Page 1000: slow (must skip 19,980 rows)
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 19980;
```

### Mitigations

1. **Limit maximum page** -- reject requests beyond a reasonable page number
2. **Switch to cursor pagination** -- for infinite scroll or deep browsing
3. **Use CLAMP overflow** -- prevent empty deep-page responses
4. **Index ORDER BY columns** -- covering indexes speed up skip operations

## Next Steps

- [Cursor/Keyset Pagination](keyset.md) -- For large datasets and infinite scroll
- [In-Memory Pagination](memory.md) -- For Python collections
