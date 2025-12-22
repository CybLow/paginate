# PyPaginator Architecture

## Overview

PyPaginator is organized into distinct layers with clear responsibilities and minimal coupling.

```
pypaginator/
├── core/              # Core data types and protocols
├── engines/           # Pagination strategy implementations
├── query/             # Query construction and execution
├── filters/           # Filtering and search
│   ├── predicates/    # JSON Logic filtering
│   └── search/        # Text search engines
├── sorting/           # Sorting utilities
├── text/              # Text processing
├── database/          # Database utilities
├── integrations/      # Framework integrations
│   └── fastapi.py     # FastAPI integration
└── exceptions.py      # Custom exceptions
```

## Core Principles

### 1. **Framework Agnostic Core**

The core pagination logic has zero dependencies on web frameworks or ORMs. This makes pypaginator:
- Lightweight for simple use cases
- Easy to integrate with any framework
- Testable without external dependencies

### 2. **Optional Dependencies**

Features are organized with optional dependencies:

```python
# Core (no dependencies)
from pypaginator import PageParams, Page
from pypaginator.engines import MemoryPaginator

# SQLAlchemy support (optional)
pip install pypaginator[sqlalchemy]
from pypaginator import paginate_entities

# Search features (optional)
pip install pypaginator[search]
from pypaginator.filters.search import MemorySearchService

# All features
pip install pypaginator[all]
```

### 3. **Immutable Data Types**

All core types are immutable frozen dataclasses:

```python
@dataclass(frozen=True, slots=True)
class PageParams:
    page: int = 1
    limit: int = 20
```

Benefits:
- Thread-safe
- Hashable
- Predictable behavior
- Easy to reason about

### 4. **Protocol-Based Design**

Core interfaces use Protocols for duck typing:

```python
class PageParamsProtocol(Protocol):
    page: int
    limit: int
    @property
    def offset(self) -> int: ...
```

This allows users to provide their own implementations without inheritance.

### 5. **Layered Architecture**

```
┌─────────────────────────────────────┐
│  Public API (pypaginator.__init__) │
│  - Page, PageParams, paginate_*     │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│  Query Layer (query/)               │
│  - Orchestrates pagination          │
└────────┬───────────────┬────────────┘
         │               │
┌────────▼────────┐  ┌──▼─────────────┐
│  Engines        │  │  Execution     │
│  - SQL          │  │  - Async exec  │
│  - Memory       │  │  - Builders    │
│  - Keyset       │  │                │
└────────┬────────┘  └────────────────┘
         │
┌────────▼─────────────────────────────┐
│  Utilities                           │
│  - filters/ (JSON Logic, search)     │
│  - sorting/ (Multi-column sort)      │
│  - text/ (Normalization)             │
│  - database/ (Type aliases)          │
└──────────────────────────────────────┘
         │
┌────────▼────────────────────────────┐
│  Core Types (core/)                 │
│  - Page, PageParams                 │
│  - Protocols                        │
│  - Context, Snapshots               │
└─────────────────────────────────────┘
```

## Key Components

### Core Types (`core/`)

**pages.py**: Main data structures
- `PageParams`: Pagination parameters (page, limit)
- `Page[T]`: Generic paginated result container
- `KeysetPageParams`: Cursor-based pagination params

**protocols** (`types.py`): Interface definitions
- `PageParamsProtocol`: Duck-typed pagination params
- `PageProtocol`: Duck-typed page results
- `SupportsTotalOrdering`: Comparison protocol

### Engines (`engines/`)

**SqlPaginator**: Database pagination
- Offset-based pagination for SQL databases
- Works with SQLAlchemy Select statements
- Automatic COUNT query generation

**MemoryPaginator**: In-memory pagination
- Fast pagination for Python collections
- No database required
- Useful for API responses, file processing

**KeysetPaginator**: Cursor-based pagination
- Better performance for large datasets
- Stable pagination (no page drift)
- Uses sqlakeyset library

### Filtering (`filters/`)

**Predicates** (`filters/predicates/`):
- JSON Logic-based filtering
- 20+ operators (eq, ne, gt, in, like, regex, etc.)
- JMESPath for nested field access
- Type-safe operator validation

**Search** (`filters/search/`):
- Full-text search with fuzzy matching
- SQL and in-memory implementations
- Configurable search options
- RapidFuzz for similarity matching

### Query Layer (`query/`)

**async_api.py**: High-level async functions
- `paginate_entities()`: Paginate ORM entities
- `paginate_rows()`: Paginate raw SQL rows
- Automatic count query optimization
- Deduplication support for joins

## Design Patterns

### 1. **Strategy Pattern**

Different pagination strategies (SQL, memory, keyset) implement the same interface:

```python
class SqlPaginator:
    async def paginate(self, session, stmt, params): ...

class MemoryPaginator:
    def paginate(self, items, params): ...
```

### 2. **Factory Pattern**

Search services use factories for creation:

```python
service = create_memory_search_service(options)
service = create_sql_search_service(options)
```

### 3. **Builder Pattern**

Complex queries use builders:

```python
builder = CountBuilder()
count_stmt = builder.build(original_stmt)
```

### 4. **Adapter Pattern**

Framework integrations adapt pypaginator to specific APIs:

```python
# FastAPI adapter
from pypaginator.integrations.fastapi import (
    PagedResponse,
    get_pagination_params
)
```

## Quality Standards

All code must maintain:

- ✅ **100% type coverage** (`mypy --strict`)
- ✅ **Zero linting issues** (`ruff check`)
- ✅ **Consistent formatting** (`black`)
- ✅ **Low complexity** (CC ≤ 8, grade A/B)
- ✅ **High test coverage** (≥ 90%)

## Extension Points

### Adding a New Operator

1. Create operator function in `filters/predicates/operators/`
2. Register in `operators/__init__.py`
3. Add tests
4. Update documentation

### Adding a New Pagination Engine

1. Create class in `engines/`
2. Implement `paginate()` method
3. Return `PaginationSnapshot`
4. Add to `engines/__init__.py`
5. Add tests and examples

### Adding a Framework Integration

1. Create module in `integrations/`
2. Add optional dependency to `pyproject.toml`
3. Provide helpful ImportError if missing
4. Add examples
5. Update README

## Performance Considerations

### SQL Pagination

- **Offset pagination**: Good for small-medium datasets
  - Simple implementation
  - Stable page numbers
  - Slower for deep pagination

- **Keyset pagination**: Best for large datasets
  - Constant-time pagination
  - No page drift
  - Requires indexed sort column

### Memory Pagination

- Fast for collections < 10k items
- No database roundtrips
- Entire dataset must fit in memory

### Filtering

- In-memory filtering: O(n) per filter
- SQL filtering: Pushed to database (indexed)
- Combine filters before pagination when possible

## Thread Safety

- All core types are immutable (thread-safe)
- Engine instances are stateless (thread-safe)
- Session/connection handling is caller's responsibility

## Future Architecture Goals

1. **Async/Sync unification**: Single codebase for both
2. **Streaming pagination**: Generator-based iteration
3. **Caching layer**: Optional result caching
4. **Django ORM support**: Native Django integration
5. **GraphQL integration**: Relay-style pagination

