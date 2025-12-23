# PyPaginator 🚀

**Advanced pagination, filtering, and search toolkit for Python**

[![CI](https://github.com/CybLow/pypaginator/actions/workflows/ci.yml/badge.svg)](https://github.com/CybLow/pypaginator/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pypaginator.svg)](https://pypi.org/project/pypaginator/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypaginator.svg)](https://pypi.org/project/pypaginator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/CybLow/pypaginator/branch/main/graph/badge.svg)](https://codecov.io/gh/CybLow/pypaginator)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

PyPaginator is a modern, framework-agnostic pagination library that provides powerful features for paginating, filtering, and searching data. It works seamlessly with SQLAlchemy (async/sync), in-memory collections, and can be extended to support other ORMs.

## ✨ Features

- 🔢 **Multiple Pagination Strategies**
  - Offset-based pagination (page/limit)
  - Cursor-based (keyset) pagination for efficient large datasets
  - In-memory pagination for collections
  
- 🔍 **Advanced Filtering**
  - JSON Logic filtering with 20+ operators
  - JMESPath for nested field access
  - Type-safe filtering with mypy strict mode
  
- 🔎 **Powerful Text Search**
  - Full-text search with fuzzy matching (RapidFuzz)
  - Accent-insensitive search
  - SQL and in-memory search engines
  
- 📊 **Flexible Sorting**
  - Multi-column sorting
  - Custom sort key functions
  - SQL and in-memory sorting
  
- 🎯 **Framework Integration**
  - Native FastAPI support with dependency injection
  - SQLAlchemy 2.0+ (async and sync)
  - Django ORM support (coming soon)
  - Framework-agnostic core

- 🛡️ **Production Ready**
  - 100% type coverage (mypy --strict)
  - Comprehensive test suite (90%+ coverage)
  - Zero cyclomatic complexity issues
  - Fully documented API

## 📦 Installation

### Basic installation (in-memory pagination only)

```bash
pip install pypaginator
```

### With SQLAlchemy support

```bash
pip install pypaginator[sqlalchemy]
```

### With all features

```bash
pip install pypaginator[all]
```

### Optional dependencies

```bash
# Text search with fuzzy matching
pip install pypaginator[search]

# Advanced filtering
pip install pypaginator[filters]

# Text normalization
pip install pypaginator[text]

# FastAPI integration
pip install pypaginator[fastapi]
```

## 🚀 Quick Start

### Basic Pagination with SQLAlchemy

```python
from sqlalchemy import select
from pypaginator import PageParams, paginate_entities

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
from pypaginator import PageParams
from pypaginator.engines import MemoryPaginator

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
from pypaginator.filters.predicates import FilterEngine

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
from pypaginator.filters.search import MemorySearchService
from pypaginator.filters.search.options import SearchOptions

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
from pypaginator import PageParams, PagedResponse, get_pagination_params
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/users", response_model=PagedResponse)
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params)
):
    stmt = select(User).order_by(User.created_at.desc())
    return await paginate_entities(session, stmt, params)
```

## 📚 Documentation

- [Full Documentation](https://pypaginator.readthedocs.io)
- [API Reference](https://pypaginator.readthedocs.io/api/)
- [Integration Guide](https://pypaginator.readthedocs.io/integration/)
- [Architecture](https://pypaginator.readthedocs.io/architecture/)
- [Examples](./examples/)

## 🧪 Advanced Usage

### Cursor-Based Pagination (Keyset)

For better performance with large datasets:

```python
from pypaginator.core import KeysetPageParams
from pypaginator.engines import KeysetPaginator

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

## 🏗️ Architecture

PyPaginator follows a clean, layered architecture:

```
pypaginator/
├── core/          # Base types (Page, PageParams, protocols)
├── engines/       # Pagination strategies (SQL, memory, keyset)
├── query/         # Query construction and execution
├── filters/       # Filtering and search
│   ├── predicates/    # JSON Logic filtering
│   └── search/        # Text search engines
├── sorting/       # Sorting utilities
├── text/          # Text normalization
└── database/      # Database utilities
```

## 🧪 Development

### Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) - Fast Python package manager

### Setup

```bash
git clone https://github.com/CybLow/pypaginator.git
cd pypaginator
uv sync  # Installs all dependencies
```

### Running Tests

```bash
# Run all tests
uv run pypaginator test

# Run with coverage
uv run pypaginator test-cov

# Run specific test categories
uv run pytest -m unit
uv run pytest -m integration
```

### Code Quality

```bash
# Quick quality check (format, lint, test)
uv run pypaginator qa

# All checks including type checking
uv run pypaginator qas

# Individual checks
uv run pypaginator lint      # Linting
uv run pypaginator format    # Formatting
uv run pypaginator typecheck # Type checking
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by modern pagination patterns
- Built with SQLAlchemy, RapidFuzz, and other excellent libraries
- Thanks to all contributors

## 📞 Support

- [Documentation](https://pypaginator.readthedocs.io)
- [Issue Tracker](https://github.com/yourusername/pypaginator/issues)
- [Discussions](https://github.com/yourusername/pypaginator/discussions)

---

Made with ❤️ by the PyPaginator team

