# pypaginate

**Advanced pagination, filtering, and search toolkit for Python**

[![CI](https://github.com/CybLow/pypaginate/actions/workflows/ci.yml/badge.svg)](https://github.com/CybLow/pypaginate/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pypaginate.svg)](https://pypi.org/project/pypaginate/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypaginate.svg)](https://pypi.org/project/pypaginate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/CybLow/pypaginate/branch/main/graph/badge.svg)](https://codecov.io/gh/CybLow/pypaginate)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

pypaginate is a modern, framework-agnostic pagination library that provides powerful features for paginating, filtering, and searching data. It works seamlessly with SQLAlchemy (async/sync), in-memory collections, and can be extended to support other ORMs.

## Features

- **Multiple Pagination Strategies**
  - Offset-based pagination (page/limit)
  - Cursor-based (keyset) pagination for efficient large datasets
  - In-memory pagination for collections
  
- **Advanced Filtering**
  - JSON Logic filtering with 20+ operators
  - JMESPath for nested field access
  - Type-safe filtering with mypy strict mode
  
- **Powerful Text Search**
  - Full-text search with fuzzy matching (RapidFuzz)
  - Accent-insensitive search
  - SQL and in-memory search engines
  
- **Flexible Sorting**
  - Multi-column sorting
  - Custom sort key functions
  - SQL and in-memory sorting
  
- **Framework Integration**
  - Native FastAPI support with dependency injection
  - SQLAlchemy 2.0+ (async and sync)
  - Framework-agnostic core

- **Production Ready**
  - 100% type coverage (mypy --strict)
  - Comprehensive test suite
  - Fully documented API

## Installation

### Using UV (Recommended)

```bash
# Basic installation
uv add pypaginate

# With SQLAlchemy support
uv add pypaginate[sqlalchemy]

# With all features
uv add pypaginate[all]
```

### Using pip

```bash
# Basic installation (in-memory pagination only)
pip install pypaginate

# With SQLAlchemy support
pip install pypaginate[sqlalchemy]

# With all features
pip install pypaginate[all]
```

### Optional Dependencies

```bash
# Text search with fuzzy matching
pip install pypaginate[search]

# Advanced filtering
pip install pypaginate[filters]

# Text normalization
pip install pypaginate[text]

# FastAPI integration
pip install pypaginate[fastapi]
```

## Quick Start

### Basic Pagination with SQLAlchemy

```python
from sqlalchemy import select
from pypaginate import PageParams, paginate_entities

async def list_users(session, page: int = 1, limit: int = 20):
    """Paginate User entities with automatic count."""
    params = PageParams(page=page, limit=limit)
    stmt = select(User).order_by(User.created_at.desc())
    
    result = await paginate_entities(
        session=session,
        query=stmt,
        params=params
    )
    
    return {
        "items": result.items,      # List of User objects
        "total": result.total,      # Total count
        "page": result.page,        # Current page
        "limit": result.limit,      # Items per page
    }
```

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

# Simple equality filter
filtered = engine.filter(users, {"status": {"eq": "active"}})
# Result: Alice and Charlie

# Complex filters with AND/OR
filtered = engine.filter(users, {
    "and": [
        {"age": {"gte": 30}},
        {"status": {"eq": "active"}}
    ]
})
# Result: Alice and Charlie (age >= 30 and active)
```

### Text Search

```python
from pypaginate.filters.search import MemorySearchService
from pypaginate.filters.search.options import SearchOptions

service = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email"],
        fuzzy_threshold=0.8
    )
)

users = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
]

results = service.search(users, "alice")
# Returns users matching "alice" in name or email
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pypaginate import PageParams, paginate_entities
from pypaginate.integrations.fastapi import get_pagination_params, PagedResponse

app = FastAPI()

@app.get("/users", response_model=PagedResponse)
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params)
):
    stmt = select(User).order_by(User.created_at.desc())
    return await paginate_entities(session, stmt, params)
```

## Documentation

Full documentation is available at [pypaginate.readthedocs.io](https://pypaginate.readthedocs.io):

- [Getting Started](https://pypaginate.readthedocs.io/getting-started/)
- [User Guide](https://pypaginate.readthedocs.io/user-guide/)
- [API Reference](https://pypaginate.readthedocs.io/api/)
- [Examples](https://pypaginate.readthedocs.io/examples/)
- [Contributing](https://pypaginate.readthedocs.io/contributing/)

## Advanced Usage

### Cursor-Based Pagination (Keyset)

For better performance with large datasets:

```python
from pypaginate.core import KeysetPageParams
from pypaginate.engines import KeysetPaginator

params = KeysetPageParams(
    limit=20,
    cursor=None  # or cursor from previous page
)

paginator = KeysetPaginator()
page = await paginator.paginate(session, stmt, params)
```

### Custom Count Queries

For complex joins:

```python
stmt = select(User).join(Profile).filter(Profile.verified == True)
count_stmt = select(func.count(User.id)).join(Profile).filter(Profile.verified == True)

page = await paginate_entities(
    session, 
    stmt, 
    params,
    count_statement=count_stmt
)
```

### Available Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq`, `ne` | Equality/inequality | `{"status": {"eq": "active"}}` |
| `lt`, `le`, `gt`, `ge` | Comparisons | `{"age": {"gte": 18}}` |
| `in`, `contains` | Membership | `{"role": {"in": ["admin", "user"]}}` |
| `like`, `regex` | Pattern matching | `{"email": {"like": "%@gmail.com"}}` |
| `between` | Range | `{"price": {"between": [10, 100]}}` |
| `null`, `empty` | Nullity/emptiness | `{"notes": {"null": true}}` |

### Nested Field Access with JMESPath

```python
items = [
    {"user": {"profile": {"name": "Alice"}}},
    {"user": {"profile": {"name": "Bob"}}},
]

filtered = engine.filter(items, {
    "user.profile.name": {"eq": "Alice"}
})
```

## Architecture

pypaginate follows a clean, layered architecture:

```
pypaginate/
├── core/          # Base types (Page, PageParams, protocols)
├── engines/       # Pagination strategies (SQL, memory, keyset)
├── query/         # Query construction and execution
├── filters/       # Filtering and search
│   ├── predicates/    # JSON Logic filtering
│   └── search/        # Text search engines
├── sorting/       # Sorting utilities
├── text/          # Text normalization
└── integrations/  # Framework integrations (FastAPI)
```

## Development

### Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) - Fast Python package manager

### Setup

```bash
git clone https://github.com/CybLow/pypaginate.git
cd pypaginate

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pypaginate --cov-report=term-missing

# Run specific test categories
uv run pytest -m unit
uv run pytest -m integration
```

### Code Quality

```bash
# Format code
uv run ruff format src tests

# Lint code
uv run ruff check src tests

# Type checking
uv run mypy src

# All quality checks via Makefile
make qa
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`uv run pytest && uv run ruff check src tests`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with SQLAlchemy, RapidFuzz, and other excellent libraries
- Inspired by modern pagination patterns from the Python ecosystem
- Thanks to all contributors

## Support

- [Documentation](https://pypaginate.readthedocs.io)
- [Issue Tracker](https://github.com/CybLow/pypaginate/issues)
- [Discussions](https://github.com/CybLow/pypaginate/discussions)

---

Made with care by the pypaginate team
