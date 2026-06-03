# pypaginate

```{image} _static/logo.svg
:alt: pypaginate
:width: 300px
:align: center
```

**Advanced pagination, filtering, and search toolkit for Python**

```{raw} html
<p align="center">
    <a href="https://pypi.org/project/pypaginate/"><img src="https://img.shields.io/pypi/v/pypaginate.svg" alt="PyPI version"></a>
    <a href="https://pypi.org/project/pypaginate/"><img src="https://img.shields.io/pypi/pyversions/pypaginate.svg" alt="Python Versions"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://github.com/CybLow/paginate/actions/workflows/ci.yml"><img src="https://github.com/CybLow/paginate/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>
```

---

## Get Started in 5 Minutes

::::{grid} 1 2 3 3
:gutter: 3

:::{grid-item-card} Installation
:link: getting-started/installation
:link-type: doc
:class-card: sd-border-primary

Install pypaginate and optional dependencies for your use case.

```bash
uv add pypaginate[all]
```
:::

:::{grid-item-card} Quick Start
:link: getting-started/quickstart
:link-type: doc
:class-card: sd-border-primary

Learn the basics with our step-by-step quickstart guide.
:::

:::{grid-item-card} First Steps
:link: getting-started/first-steps
:link-type: doc
:class-card: sd-border-primary

Build your first paginated API with FastAPI and SQLAlchemy.
:::

::::

---

## Why pypaginate?

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} Multiple Pagination Strategies
:class-card: sd-rounded-3

- **Offset-based** pagination (page/limit)
- **Cursor-based** (keyset) for large datasets
- **In-memory** for Python collections
:::

:::{grid-item-card} Advanced Filtering
:class-card: sd-rounded-3

- 20 operators (eq, gte, contains, between, regex, etc.)
- Dot notation for nested fields
- Type-safe with mypy strict
:::

:::{grid-item-card} Powerful Text Search
:class-card: sd-rounded-3

- Full-text with fuzzy matching
- Accent-insensitive search
- SQL and in-memory engines
:::

:::{grid-item-card} Flexible Sorting
:class-card: sd-rounded-3

- Multi-column sorting
- Custom sort key functions
- Bidirectional support
:::

:::{grid-item-card} Framework Integration
:class-card: sd-rounded-3

- Native FastAPI support
- SQLAlchemy 2.0+ (async/sync)
- Framework-agnostic core
:::

:::{grid-item-card} Production Ready
:class-card: sd-rounded-3

- 100% type coverage
- 90%+ test coverage
- Clean architecture
:::

::::

---

## Quick Example

::::{tab-set}

:::{tab-item} SQLAlchemy
```python
from pypaginate import paginate, OffsetParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend
from sqlalchemy import select

async def list_users(session, page: int = 1, limit: int = 20):
    params = OffsetParams(page=page, limit=limit)
    stmt = select(User).order_by(User.created_at.desc())
    backend = SQLAlchemyBackend(session)

    page = await paginate(stmt, params, backend=backend)

    return {
        "items": page.items,
        "total": page.total,
        "page": page.page,
        "pages": page.pages,
    }
```
:::

:::{tab-item} In-Memory
```python
from pypaginate import paginate, OffsetParams

users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]

page = paginate(users, OffsetParams(page=1, limit=2))
print(page.items)  # [Alice, Bob]
print(page.total)  # 3
```
:::

:::{tab-item} Filtering
```python
from pypaginate import FilterSpec, And
from pypaginate.filtering import FilterEngine

engine = FilterEngine()

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# Filter for active users aged 30+
filtered = engine.apply(users, And(
    FilterSpec(field="age", operator="gte", value=30),
    FilterSpec(field="status", value="active"),
))
# Result: [Alice, Charlie]
```
:::

::::

---

## Learn More

::::{grid} 1 2 2 4
:gutter: 3

:::{grid-item-card} Pagination
:link: pagination/index
:link-type: doc

Learn offset, cursor, and in-memory pagination strategies.
:::

:::{grid-item-card} Filtering
:link: filtering/index
:link-type: doc

Filter data with 20 typed operators and nested And/Or groups.
:::

:::{grid-item-card} Search
:link: search/index
:link-type: doc

Add full-text and fuzzy search capabilities.
:::

:::{grid-item-card} API Reference
:link: api/overview
:link-type: doc

Complete API documentation.
:::

::::

```{toctree}
:maxdepth: 2
:hidden:
:caption: Getting Started

getting-started/index
getting-started/installation
getting-started/quickstart
getting-started/first-steps
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: User Guide

pagination/index
pagination/offset
pagination/keyset
pagination/memory
filtering/index
filtering/basic
filtering/json-logic
filtering/operators
search/index
search/text-search
search/fuzzy
sorting/index
sorting/basic
sorting/multi-column
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Integrations

integrations/index
integrations/fastapi
integrations/sqlalchemy
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: API Reference

api/overview
api/pypaginate/index
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Examples

examples/index
examples/basic-pagination
examples/filtering
examples/fastapi
examples/keyset
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Concepts

concepts/index
concepts/architecture
concepts/pagination-strategies
concepts/cursor-encoding
concepts/filter-expressions
concepts/search-relevance
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Contributing

contributing/index
contributing/development
contributing/code-style
contributing/testing
contributing/architecture
contributing/roadmap
CODE_OF_CONDUCT
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Project

comparison
benchmarks
```
