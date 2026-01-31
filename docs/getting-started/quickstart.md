# Quick Start

Get up and running with pypaginate in 5 minutes.

## Installation

```bash
pip install pypaginate[all]
```

## Basic Usage

### 1. In-Memory Pagination

The simplest way to paginate data in Python:

```python
from pypaginate import PageParams
from pypaginate.engines import MemoryPaginator

# Your data (list, tuple, or any sequence)
users = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25},
    {"id": 3, "name": "Charlie", "age": 35},
    {"id": 4, "name": "Diana", "age": 28},
    {"id": 5, "name": "Eve", "age": 32},
]

# Create paginator and parameters
paginator = MemoryPaginator()
params = PageParams(page=1, limit=2)

# Paginate!
page = paginator.paginate(users, params).to_page()

# Access results
print(f"Items: {page.items}")      # First 2 users
print(f"Total: {page.total}")       # 5
print(f"Page: {page.page}")         # 1
print(f"Pages: {page.pages}")       # 3
print(f"Has next: {page.has_next}") # True
```

**Output:**
```
Items: [{'id': 1, 'name': 'Alice', 'age': 30}, {'id': 2, 'name': 'Bob', 'age': 25}]
Total: 5
Page: 1
Pages: 3
Has next: True
```

### 2. Filtering Data

Filter your data before pagination using JSON Logic:

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# Simple filter: active users only
active_users = engine.filter(users, {"status": {"eq": "active"}})
# Result: [Alice, Charlie]

# Complex filter: active AND age >= 30
filtered = engine.filter(users, {
    "and": [
        {"age": {"gte": 30}},
        {"status": {"eq": "active"}}
    ]
})
# Result: [Alice, Charlie]
```

### 3. SQLAlchemy Pagination

Paginate database queries with SQLAlchemy:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import PageParams, paginate_entities

async def list_users(session: AsyncSession, page: int = 1, limit: int = 20):
    # Create pagination parameters
    params = PageParams(page=page, limit=limit)
    
    # Build your query
    stmt = select(User).order_by(User.created_at.desc())
    
    # Paginate
    result = await paginate_entities(session, stmt, params)
    
    return {
        "items": result.items,
        "total": result.total,
        "page": result.page,
        "pages": result.pages,
    }
```

### 4. FastAPI Integration

Use pypaginate with FastAPI's dependency injection:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import PageParams, paginate_entities
from pypaginate.integrations.fastapi import get_pagination_params

app = FastAPI()

@app.get("/users")
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
):
    stmt = select(User).order_by(User.created_at.desc())
    return await paginate_entities(session, stmt, params)
```

Now your API accepts query parameters:
```
GET /users?page=1&limit=20
```

### 5. Text Search

Search your data with fuzzy matching:

```python
from pypaginate.filters.search import MemorySearchService
from pypaginate.filters.search.options import SearchOptions

# Configure search
service = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email"],
        fuzzy_threshold=0.8,
    )
)

users = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Alicia Keys", "email": "alicia@example.com"},
]

# Search for "alice" - finds "Alice" and "Alicia" (fuzzy match)
results = service.search(users, "alice")
```

## Core Concepts

### PageParams

Immutable parameters for pagination:

```python
from pypaginate import PageParams

params = PageParams(page=1, limit=20)

print(params.page)    # 1
print(params.limit)   # 20
print(params.offset)  # 0 (calculated: (page - 1) * limit)
```

### Page

The result of pagination:

```python
from pypaginate import Page

# Page contains:
# - items: List of items for current page
# - total: Total count across all pages
# - page: Current page number
# - limit: Items per page
# - pages: Total number of pages (calculated)
# - has_next: True if there are more pages
# - has_previous: True if not on first page
```

## Common Patterns

### Pattern 1: Filter then Paginate

```python
# 1. Filter data
filtered = engine.filter(users, {"status": {"eq": "active"}})

# 2. Paginate results
page = paginator.paginate(filtered, params).to_page()
```

### Pattern 2: Search then Paginate

```python
# 1. Search
results = search_service.search(users, "query")

# 2. Paginate
page = paginator.paginate(results, params).to_page()
```

### Pattern 3: Custom Count Query

For complex joins where automatic count is expensive:

```python
from sqlalchemy import func, select

# Main query with join
stmt = select(User).join(Profile).filter(Profile.verified == True)

# Custom count query
count_stmt = select(func.count(User.id)).join(Profile).filter(Profile.verified == True)

# Use custom count
page = await paginate_entities(
    session, 
    stmt, 
    params,
    count_statement=count_stmt
)
```

## Error Handling

```python
from pypaginate import PaginationConfigurationError

try:
    # Invalid: page must be >= 1
    params = PageParams(page=0, limit=20)
except PaginationConfigurationError as e:
    print(f"Error: {e}")
```

## Next Steps

- [First Steps Tutorial](first-steps.md) - Build a complete paginated API
- [Pagination Guide](../user-guide/pagination/index.md) - Learn all pagination strategies
- [Filtering Guide](../user-guide/filtering/index.md) - Master filtering with JSON Logic
- [API Reference](../api/index.md) - Complete API documentation
