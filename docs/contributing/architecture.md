# Architecture

pypaginate is organized into distinct layers with clear responsibilities and minimal coupling.

## Directory Structure

```
pypaginate/
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

### 1. Framework Agnostic Core

The core pagination logic has zero dependencies on web frameworks or ORMs:

- Lightweight for simple use cases
- Easy to integrate with any framework
- Testable without external dependencies

### 2. Optional Dependencies

Features are organized with optional dependencies:

```python
# Core (no dependencies)
from pypaginate.core import PageParams, Page
from pypaginate.engines import MemoryPaginator

# SQLAlchemy support (optional)
pip install pypaginate[sqlalchemy]
from pypaginate.query import paginate_entities

# All features
pip install pypaginate[all]
```

### 3. Immutable Data Types

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

### 4. Protocol-Based Design

Core interfaces use Protocols for duck typing:

```python
class PageParamsProtocol(Protocol):
    page: int
    limit: int
    
    @property
    def offset(self) -> int: ...
```

This allows custom implementations without inheritance.

## Layered Architecture

```
┌────────────────────────────────────────┐
│  Public API (pypaginate.__init__)     │
│  - Page, PageParams, paginate_*        │
└─────────────────┬──────────────────────┘
                  │
┌─────────────────▼──────────────────────┐
│  Query Layer (query/)                  │
│  - Orchestrates pagination             │
│  - High-level async API                │
└────────┬──────────────────┬────────────┘
         │                  │
┌────────▼────────┐   ┌────▼────────────┐
│  Engines        │   │  Execution      │
│  - SQL          │   │  - Async exec   │
│  - Memory       │   │  - Builders     │
│  - Keyset       │   │                 │
└────────┬────────┘   └─────────────────┘
         │
┌────────▼───────────────────────────────┐
│  Utilities                             │
│  - filters/ (JSON Logic, search)       │
│  - sorting/ (Multi-column sort)        │
│  - text/ (Normalization)               │
│  - database/ (Type aliases)            │
└────────────────────────────────────────┘
         │
┌────────▼───────────────────────────────┐
│  Core Types (core/)                    │
│  - Page, PageParams                    │
│  - Protocols                           │
│  - Context, Snapshots                  │
└────────────────────────────────────────┘
```

## Key Components

### Core Types (`core/`)

**pages.py**: Main data structures
- `PageParams`: Pagination parameters (page, limit)
- `Page[T]`: Generic paginated result container
- `KeysetPageParams`: Cursor-based pagination params

**context.py**: Execution context
- `PaginationContext`: Carries parameters and options
- `clamp_page_params`: Clamp to valid range

**snapshots.py**: Internal result containers
- `PaginationSnapshot`: Results with metadata

### Engines (`engines/`)

**SqlPaginator**: Database pagination
- Offset-based pagination for SQL databases
- Works with SQLAlchemy Select statements
- Automatic COUNT query generation

**MemoryPaginator**: In-memory pagination
- Fast pagination for Python collections
- No database required

**KeysetPaginator**: Cursor-based pagination
- Better performance for large datasets
- Stable pagination (no page drift)

### Filtering (`filters/`)

**Predicates** (`filters/predicates/`):
- JSON Logic-based filtering
- 20+ operators (eq, ne, gt, in, like, etc.)
- Type-safe operator validation

**Search** (`filters/search/`):
- Full-text search with fuzzy matching
- SQL and in-memory implementations
- RapidFuzz for similarity matching

### Query Layer (`query/`)

**async_api.py**: High-level async functions
- `paginate_entities()`: Paginate ORM entities
- `paginate_rows()`: Paginate raw SQL rows
- Automatic count query optimization

## Design Patterns

### Strategy Pattern

Different pagination strategies implement the same interface:

```python
class SqlPaginator:
    async def paginate(self, session, stmt, params): ...

class MemoryPaginator:
    def paginate(self, items, params): ...
```

### Factory Pattern

Search services use factories for creation:

```python
service = create_memory_search_service(options)
service = create_sql_search_service(options)
```

### Builder Pattern

Complex queries use builders:

```python
builder = CountBuilder()
count_stmt = builder.build(original_stmt)
```

### Adapter Pattern

Framework integrations adapt pypaginate to specific APIs:

```python
from pypaginate.integrations.fastapi import (
    PagedResponse,
    get_pagination_params
)
```

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
4. Add examples and documentation

## Performance Considerations

### SQL Pagination

- **Offset pagination**: Good for small-medium datasets
  - Simple implementation
  - Stable page numbers
  - Slower for deep pagination (page 1000+)

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

## Quality Standards

All code must maintain:

- 100% type coverage (`mypy --strict`)
- Zero linting issues (`ruff check`)
- Consistent formatting (`ruff format`)
- High test coverage (>= 80%)

## See Also

- [Code Style](code-style.md) - Coding standards
- [Testing Guide](testing.md) - Testing practices
- [Roadmap](roadmap.md) - Future plans
