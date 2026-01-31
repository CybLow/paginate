# User Guide

Welcome to the pypaginate User Guide. This section provides comprehensive documentation on all features.

## Sections

### Pagination

Learn about different pagination strategies:

- [**Offset Pagination**](pagination/offset.md) - Traditional page-based pagination
- [**Cursor/Keyset Pagination**](pagination/keyset.md) - Efficient pagination for large datasets
- [**In-Memory Pagination**](pagination/memory.md) - Paginate Python collections

### Filtering

Master data filtering with pypaginate:

- [**Basic Filtering**](filtering/basic.md) - Simple filter operations
- [**JSON Logic**](filtering/json-logic.md) - Complex filter expressions
- [**Operators Reference**](filtering/operators.md) - All available operators

### Search

Implement powerful search functionality:

- [**Text Search**](search/text-search.md) - Full-text search basics
- [**Fuzzy Matching**](search/fuzzy.md) - Approximate string matching

### Sorting

Sort your data effectively:

- [**Basic Sorting**](sorting/basic.md) - Single-column sorting
- [**Multi-Column Sorting**](sorting/multi-column.md) - Complex sort orders

### Integrations

Use pypaginate with your favorite frameworks:

- [**FastAPI**](integrations/fastapi.md) - Dependency injection and response models
- [**SQLAlchemy**](integrations/sqlalchemy.md) - Async and sync database pagination

## Quick Reference

### Core Classes

| Class | Description |
|-------|-------------|
| `PageParams` | Pagination parameters (page, limit) |
| `Page[T]` | Paginated result container |
| `KeysetPageParams` | Cursor-based pagination parameters |

### Engines

| Engine | Use Case |
|--------|----------|
| `MemoryPaginator` | In-memory collections |
| `SqlPaginator` | SQLAlchemy queries |
| `KeysetPaginator` | Large datasets with cursors |

### Common Imports

```python
# Core
from pypaginate import PageParams, Page, paginate_entities

# Engines
from pypaginate.engines import MemoryPaginator, KeysetPaginator

# Filtering
from pypaginate.filters.predicates import FilterEngine

# Search
from pypaginate.filters.search import MemorySearchService, SearchOptions

# Sorting
from pypaginate.sorting import SortEngine

# FastAPI
from pypaginate.integrations.fastapi import get_pagination_params
```
