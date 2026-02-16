# In-Memory Pagination

Paginate Python collections without database queries.

## Overview

The `MemoryPaginator` efficiently paginates any sequence type:

- Lists
- Tuples
- Dictionaries (values)
- Generator results
- Any iterable

## Basic Usage

```python
from pypaginate import PageParams
from pypaginate.engines import MemoryPaginator

# Your data
users = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25},
    {"id": 3, "name": "Charlie", "age": 35},
    {"id": 4, "name": "Diana", "age": 28},
    {"id": 5, "name": "Eve", "age": 32},
]

# Create paginator
paginator = MemoryPaginator()

# Paginate
params = PageParams(page=1, limit=2)
result = paginator.paginate(users, params)

# Convert to Page object
page = result.to_page()

print(page.items)  # First 2 users
print(page.total)  # 5
print(page.pages)  # 3
```

## The Paginator

### Creating a MemoryPaginator

```python
from pypaginate.engines import MemoryPaginator

# Default paginator
paginator = MemoryPaginator()

# Paginate any sequence
result = paginator.paginate(data, params)
```

### Result Object

The `paginate()` method returns a `PaginationSnapshot`:

```python
result = paginator.paginate(users, params)

# Access as snapshot
result.items      # Items for this page
result.total      # Total count
result.params     # Original params

# Convert to Page
page = result.to_page()
```

## Working with Different Data Types

### Lists

```python
users = [user1, user2, user3, ...]
page = paginator.paginate(users, params).to_page()
```

### Dictionaries

Paginate dictionary values:

```python
users_dict = {
    "alice": {"name": "Alice", "age": 30},
    "bob": {"name": "Bob", "age": 25},
}

# Convert to list first
users_list = list(users_dict.values())
page = paginator.paginate(users_list, params).to_page()
```

### Dataclasses / Pydantic Models

```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    age: int

users = [
    User(1, "Alice", 30),
    User(2, "Bob", 25),
    User(3, "Charlie", 35),
]

page = paginator.paginate(users, params).to_page()
# page.items contains User objects
```

### Generator Results

For generators, convert to list first:

```python
def generate_users():
    for i in range(100):
        yield {"id": i, "name": f"User {i}"}

# Materialize generator
users = list(generate_users())
page = paginator.paginate(users, params).to_page()
```

## Combining with Filtering

Filter before paginating:

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()
paginator = MemoryPaginator()

# All users
users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# 1. Filter
active_users = engine.filter(users, {"status": {"eq": "active"}})

# 2. Paginate filtered results
params = PageParams(page=1, limit=10)
page = paginator.paginate(active_users, params).to_page()

print(page.items)  # [Alice, Charlie]
print(page.total)  # 2
```

## Combining with Sorting

Sort before paginating:

```python
from pypaginate.sorting import SortEngine

sort_engine = SortEngine()
paginator = MemoryPaginator()

# Sort by age descending
sorted_users = sort_engine.sort(
    users,
    sort_fields=["age"],
    sort_orders=["desc"]
)

# Then paginate
page = paginator.paginate(sorted_users, params).to_page()
```

## Combining with Search

Search before paginating:

```python
from pypaginate.filters.search import MemorySearchService
from pypaginate.filters.search.options import SearchOptions

search = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email"],
        fuzzy_threshold=0.8
    )
)
paginator = MemoryPaginator()

# 1. Search
matches = search.search(users, "alice")

# 2. Paginate
page = paginator.paginate(matches, params).to_page()
```

## Complete Pipeline

A typical in-memory data pipeline:

```python
from pypaginate import PageParams
from pypaginate.engines import MemoryPaginator
from pypaginate.filters.predicates import FilterEngine
from pypaginate.sorting import SortEngine

def paginate_users(
    users: list[dict],
    filters: dict | None = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Complete pagination pipeline."""
    
    filter_engine = FilterEngine()
    sort_engine = SortEngine()
    paginator = MemoryPaginator()
    
    # 1. Filter (if provided)
    if filters:
        users = filter_engine.filter(users, filters)
    
    # 2. Sort
    users = sort_engine.sort(
        users,
        sort_fields=[sort_by],
        sort_orders=[sort_order]
    )
    
    # 3. Paginate
    params = PageParams(page=page, limit=limit)
    page_result = paginator.paginate(users, params).to_page()
    
    return {
        "items": page_result.items,
        "total": page_result.total,
        "page": page_result.page,
        "pages": page_result.pages,
        "has_next": page_result.has_next,
        "has_previous": page_result.has_previous,
    }
```

## Performance Considerations

### Memory Usage

In-memory pagination requires all data to be loaded:

```python
# Good: Small to medium datasets
users = load_users()  # 1,000 items = OK
page = paginator.paginate(users, params).to_page()

# Careful: Large datasets
users = load_all_users()  # 1,000,000 items = High memory
```

### For Large Datasets

Consider:

1. **Database pagination**: Use SQLAlchemy with offset/keyset
2. **Chunked processing**: Process in batches
3. **Streaming**: Use generators with itertools.islice

```python
import itertools

def paginate_generator(items, page: int, limit: int):
    """Paginate a generator without loading all into memory."""
    start = (page - 1) * limit
    
    # Skip items before start
    iterator = iter(items)
    for _ in range(start):
        next(iterator, None)
    
    # Take limit items
    page_items = list(itertools.islice(iterator, limit))
    
    return page_items
```

## API Integration

Using with FastAPI:

```python
from fastapi import FastAPI, Query
from pypaginate import PageParams
from pypaginate.engines import MemoryPaginator

app = FastAPI()

# In-memory data store
USERS = [
    {"id": i, "name": f"User {i}"}
    for i in range(100)
]

@app.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    paginator = MemoryPaginator()
    params = PageParams(page=page, limit=limit)
    result = paginator.paginate(USERS, params).to_page()
    
    return {
        "items": result.items,
        "total": result.total,
        "page": result.page,
        "pages": result.pages,
    }
```

## Next Steps

- [Offset Pagination](offset.md) - Database pagination
- [Keyset Pagination](keyset.md) - Large datasets
- [Filtering Guide](../filtering/index.md) - Filter before paginating
- [Sorting Guide](../sorting/index.md) - Sort before paginating
