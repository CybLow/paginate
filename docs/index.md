# pypaginate

<div class="hero" markdown>

**Advanced pagination, filtering, and search toolkit for Python**

[![PyPI version](https://img.shields.io/pypi/v/pypaginate.svg)](https://pypi.org/project/pypaginate/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypaginate.svg)](https://pypi.org/project/pypaginate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/CybLow/pypaginate/actions/workflows/ci.yml/badge.svg)](https://github.com/CybLow/pypaginate/actions/workflows/ci.yml)

</div>

---

## What is pypaginate?

**pypaginate** is a modern, framework-agnostic pagination library that provides powerful features for paginating, filtering, and searching data. It works seamlessly with SQLAlchemy (async/sync), in-memory collections, and can be extended to support other ORMs.

```python
from pypaginate import PageParams, paginate_entities
from sqlalchemy import select

async def list_users(session, page: int = 1, limit: int = 20):
    params = PageParams(page=page, limit=limit)
    stmt = select(User).order_by(User.created_at.desc())
    
    result = await paginate_entities(session, stmt, params)
    
    return {
        "items": result.items,
        "total": result.total,
        "page": result.page,
        "pages": result.pages,
    }
```

---

## Key Features

<div class="feature-grid" markdown>

<div class="feature-card" markdown>

### Multiple Pagination Strategies

- **Offset-based** pagination (page/limit)
- **Cursor-based** (keyset) pagination for large datasets
- **In-memory** pagination for collections

</div>

<div class="feature-card" markdown>

### Advanced Filtering

- JSON Logic filtering with 20+ operators
- JMESPath for nested field access
- Type-safe filtering with mypy strict mode

</div>

<div class="feature-card" markdown>

### Powerful Text Search

- Full-text search with fuzzy matching (RapidFuzz)
- Accent-insensitive search
- SQL and in-memory search engines

</div>

<div class="feature-card" markdown>

### Flexible Sorting

- Multi-column sorting
- Custom sort key functions
- SQL and in-memory sorting

</div>

<div class="feature-card" markdown>

### Framework Integration

- Native FastAPI support with dependency injection
- SQLAlchemy 2.0+ (async and sync)
- Framework-agnostic core

</div>

<div class="feature-card" markdown>

### Production Ready

- 100% type coverage (mypy --strict)
- Comprehensive test suite (90%+ coverage)
- Zero cyclomatic complexity issues

</div>

</div>

---

## Quick Installation

=== "Basic (in-memory only)"

    ```bash
    pip install pypaginate
    ```

=== "With SQLAlchemy"

    ```bash
    pip install pypaginate[sqlalchemy]
    ```

=== "With all features"

    ```bash
    pip install pypaginate[all]
    ```

---

## Quick Example

### In-Memory Pagination

```python
from pypaginate import PageParams
from pypaginate.engines import MemoryPaginator

users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]

paginator = MemoryPaginator()
params = PageParams(page=1, limit=2)

page = paginator.paginate(users, params).to_page()
print(page.items)  # [{"name": "Alice", ...}, {"name": "Bob", ...}]
print(page.total)  # 3
```

### Filtering with JSON Logic

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# Filter for active users aged 30+
filtered = engine.filter(users, {
    "and": [
        {"age": {"gte": 30}},
        {"status": {"eq": "active"}}
    ]
})
# Result: [Alice, Charlie]
```

---

## Documentation Sections

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/index.md) | Installation and first steps |
| [Pagination](user-guide/pagination/index.md) | Pagination strategies and usage |
| [API Reference](api/index.md) | Complete API documentation |
| [Examples](examples/index.md) | Practical code examples |
| [Contributing](contributing/index.md) | How to contribute |

---

## Why pypaginate?

| Feature | pypaginate | fastapi-pagination | Comparison |
|---------|------------|-------------------|------------|
| Type Safety | mypy --strict | Basic types | Better |
| Fuzzy Search | RapidFuzz | None | Unique |
| JSON Logic | Full support | None | Better |
| Architecture | Clean layers | Monolithic | Better |
| Framework | Agnostic | FastAPI only | More flexible |

---

## License

pypaginate is released under the [MIT License](https://opensource.org/licenses/MIT).

---

<div style="text-align: center; margin-top: 2rem;" markdown>

[Get Started](getting-started/index.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/CybLow/pypaginate){ .md-button }

</div>
