# PyPaginator

Welcome to **PyPaginator** - the advanced pagination, filtering, and search toolkit for Python.

## Features

- 🔢 **Multiple Pagination Strategies**: Offset-based, cursor-based (keyset), and in-memory
- 🔍 **Advanced Filtering**: JSON Logic with 20+ operators
- 🔎 **Powerful Text Search**: Full-text search with fuzzy matching
- 📊 **Flexible Sorting**: Multi-column with custom sort keys
- 🎯 **Framework Integration**: FastAPI, SQLAlchemy 2.0+
- 🛡️ **Production Ready**: 100% type coverage, 80%+ test coverage

## Quick Start

```bash
pip install pypaginator[all]
```

```python
from pypaginator import PageParams, paginate_entities

async def list_users(session, page=1, limit=20):
    params = PageParams(page=page, limit=limit)
    stmt = select(User).order_by(User.created_at.desc())
    return await paginate_entities(session, stmt, params)
```

## Documentation

- [Getting Started](QUICKSTART.md) - Installation and basic usage
- [Architecture](ARCHITECTURE.md) - System design overview
- [Testing Guide](TESTING_GUIDE.md) - How to run and write tests
- [Comparison](COMPARISON.md) - Comparison with other libraries
- [Roadmap](ROADMAP.md) - Future development plans
