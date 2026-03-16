# Getting Started

Welcome to pypaginate! This section will help you get up and running quickly.

## What is pypaginate?

pypaginate is a modern, framework-agnostic pagination toolkit for Python 3.11+ that provides:

- **Universal `paginate()` function** -- one call for lists, SQLAlchemy queries, and custom backends
- **Type-safe inference** -- `OffsetParams` produces `OffsetPage`, `CursorParams` produces `CursorPage`
- **Declarative filtering** -- `FilterSpec`, composable `And`/`Or` groups, 20+ operators
- **Sorting and search** -- `SortSpec` and `SearchSpec` with fuzzy matching
- **FastAPI dependencies** -- `OffsetDep`, `CursorDep`, `FilterDep`, `SortDep`, `SearchDep`
- **Pipeline composition** -- filter, sort, search, then paginate in one call

## Quick Navigation

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Installation
:link: installation
:link-type: doc

Install pypaginate and optional dependencies
:::

:::{grid-item-card} Quick Start
:link: quickstart
:link-type: doc

Get paginating in 5 minutes
:::

:::{grid-item-card} First Steps
:link: first-steps
:link-type: doc

Filtering, sorting, and search examples
:::

::::


## Minimum Requirements

- **Python 3.11+**
- **pydantic** (core dependency)

## Optional Dependencies

| Feature | Installation | Provides |
|---------|-------------|----------|
| SQLAlchemy | `pypaginate[sqlalchemy]` | Database pagination + cursor/keyset |
| Search | `pypaginate[search]` | Fuzzy text search (rapidfuzz) |
| FastAPI | `pypaginate[fastapi]` | FastAPI dependency injection |
| Fast | `pypaginate[fast]` | msgspec-backed pages (near-zero overhead) |
| All | `pypaginate[all]` | Everything above |

## Next Steps

1. **[Install pypaginate](installation.md)** with your preferred extras
2. **[Follow the Quick Start](quickstart.md)** for basic usage
3. **[Explore First Steps](first-steps.md)** with filtering, sorting, and search
