# Examples

Complete, runnable examples demonstrating pypaginate v0.2 features.

## Quick Links

| Example | Description |
|---------|-------------|
| [Basic Pagination](basic-pagination.md) | In-memory and SQLAlchemy offset pagination |
| [Filtering](filtering.md) | FilterSpec, And/Or groups, FilterDep |
| [Keyset Pagination](keyset.md) | CursorParams, CursorPage, cursor backends |
| [FastAPI Integration](fastapi.md) | Full app with OffsetDep, filtering, sorting, search |

## Prerequisites

```bash
pip install pypaginate[all]
```

## The Core Pattern

Every example follows the same pattern -- the universal `paginate()` function:

```python
from pypaginate import paginate, OffsetParams

# In-memory: no backend needed
page = paginate([1, 2, 3, 4, 5], OffsetParams(page=1, limit=2))

# Database: pass a backend explicitly
page = await paginate(query, OffsetParams(page=1, limit=20), backend=backend)
```

Input type determines output type:

- `OffsetParams` produces `OffsetPage` (with `total`, `page`, `pages`)
- `CursorParams` produces `CursorPage` (with `next_cursor`, `previous_cursor`)

## Example Categories

### Getting Started

- **Basic Pagination** -- `paginate()` with lists and SQLAlchemy
- **Filtering** -- `FilterSpec` and `And`/`Or` groups

### Intermediate

- **Keyset Pagination** -- `CursorParams` for large datasets
- **FastAPI Integration** -- Declarative dependencies

### Advanced

- **Pipelines** -- `SyncPipeline` / `AsyncPipeline` for filter + sort + search + paginate
- **Custom backends** -- Implement the `PaginationBackend` protocol
