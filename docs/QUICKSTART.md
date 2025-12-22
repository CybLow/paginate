# PyPaginator Quick Start Guide

This guide will get you up and running with PyPaginator in 5 minutes.

## Installation

### Basic Installation (In-Memory Only)

```bash
pip install pypaginator
```

### With SQLAlchemy Support

```bash
pip install pypaginator[sqlalchemy]
```

### With All Features

```bash
pip install pypaginator[all]
```

## Basic Usage

### 1. In-Memory Pagination

The simplest way to use PyPaginator is with in-memory data:

```python
from pypaginator import PageParams
from pypaginator.engines import MemoryPaginator

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
params = PageParams(page=1, limit=2)

# Paginate
page = paginator.paginate(users, params).to_page()

print(f"Page {page.page} of {(page.total + page.limit - 1) // page.limit}")
print(f"Total items: {page.total}")
for user in page.items:
    print(f"  - {user['name']}, age {user['age']}")
```

**Output:**
```
Page 1 of 3
Total items: 5
  - Alice, age 30
  - Bob, age 25
```

### 2. Filtering

Filter your data before pagination:

```python
from pypaginator.filters.predicates import FilterEngine

engine = FilterEngine()

# Filter for users aged 30 or more
filtered = engine.filter(users, {"age": {"gte": 30}})

# Paginate filtered results
page = paginator.paginate(filtered, params).to_page()
```

**Available Operators:**
- `eq`, `ne` - Equality/inequality
- `lt`, `le`, `gt`, `ge` - Comparisons
- `in`, `contains` - Membership
- `like`, `regex` - Pattern matching
- `between` - Range
- `null`, `empty` - Nullity/emptiness

### 3. Complex Filters

Combine filters with AND/OR logic:

```python
# Active users aged 30+
filter_spec = {
    "and": [
        {"status": {"eq": "active"}},
        {"age": {"gte": 30}}
    ]
}

filtered = engine.filter(users, filter_spec)
```

### 4. SQLAlchemy Integration

For database pagination with SQLAlchemy:

```python
from sqlalchemy import select
from pypaginator import PageParams, paginate_entities

async def list_users(session):
    stmt = select(User).order_by(User.name)
    params = PageParams(page=1, limit=20)
    
    page = await paginate_entities(session, stmt, params)
    return page
```

### 5. FastAPI Integration

Use with FastAPI for automatic pagination:

```python
from fastapi import Depends, FastAPI
from pypaginator import PageParams
from pypaginator.integrations.fastapi import get_pagination_params

app = FastAPI()

@app.get("/users")
async def list_users(
    params: PageParams = Depends(get_pagination_params)
):
    # params.page and params.limit are automatically extracted
    # from query parameters
    ...
```

## Common Patterns

### Pattern 1: Paginate + Filter

```python
# 1. Filter data
filtered = engine.filter(users, {"status": {"eq": "active"}})

# 2. Paginate results
page = paginator.paginate(filtered, params).to_page()
```

### Pattern 2: Nested Field Access

```python
data = [
    {"user": {"profile": {"name": "Alice"}}},
    {"user": {"profile": {"name": "Bob"}}},
]

# Filter by nested field using JMESPath
filtered = engine.filter(data, {
    "user.profile.name": {"eq": "Alice"}
})
```

### Pattern 3: Multiple Conditions

```python
# Users aged 25-35 with specific names
filter_spec = {
    "and": [
        {"age": {"between": [25, 35]}},
        {"name": {"in": ["Alice", "Charlie", "Eve"]}}
    ]
}
```

### Pattern 4: Text Search

```python
from pypaginator.filters.search import MemorySearchService
from pypaginator.filters.search.options import SearchOptions

service = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email"],
        fuzzy_threshold=0.8
    )
)

# Search for "alice" in name or email
results = service.search(users, "alice")
```

## Configuration

### PageParams Options

```python
params = PageParams(
    page=1,      # Page number (1-indexed)
    limit=20,    # Items per page
)

# Calculate offset for SQL OFFSET
offset = params.offset  # (page - 1) * limit
```

### Search Options

```python
from pypaginator.filters.search.options import SearchOptions

options = SearchOptions(
    fields=["name", "description"],    # Fields to search
    fuzzy_threshold=0.8,                # Fuzzy matching threshold (0-1)
    case_sensitive=False,               # Case-sensitive search
    accent_sensitive=False,             # Accent-sensitive search
)
```

## Error Handling

```python
from pypaginator import PaginationConfigurationError

try:
    params = PageParams(page=0, limit=20)  # Invalid: page < 1
except PaginationConfigurationError as e:
    print(f"Invalid configuration: {e}")
```

## Next Steps

- **Examples**: Check the `examples/` directory for complete examples
- **Documentation**: Read `docs/ARCHITECTURE.md` for in-depth architecture
- **Contributing**: See `CONTRIBUTING.md` to contribute
- **API Reference**: Browse the source code with full type hints

## Tips

1. **Performance**: For large datasets, use SQLAlchemy pagination instead of in-memory
2. **Filtering**: Apply filters before pagination to reduce data size
3. **Type Safety**: All code is fully typed with mypy --strict
4. **Immutability**: PageParams and Page are immutable (frozen dataclasses)
5. **Optional Dependencies**: Install only what you need (`[sqlalchemy]`, `[search]`, etc.)

## Troubleshooting

### ImportError: No module named 'sqlalchemy'

Install SQLAlchemy support:
```bash
pip install pypaginator[sqlalchemy]
```

### ImportError: No module named 'rapidfuzz'

Install search support:
```bash
pip install pypaginator[search]
```

### All features not working

Install all optional dependencies:
```bash
pip install pypaginator[all]
```

## Resources

- **GitHub**: https://github.com/yourusername/pypaginator
- **PyPI**: https://pypi.org/project/pypaginator/
- **Documentation**: https://pypaginator.readthedocs.io
- **Issues**: https://github.com/yourusername/pypaginator/issues

---

Happy paginating! 🚀

