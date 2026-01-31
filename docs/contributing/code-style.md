# Code Style

pypaginate follows strict coding standards to maintain quality and consistency.

## Tools

| Tool | Purpose |
|------|---------|
| [Ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [mypy](https://mypy.readthedocs.io/) | Type checking |
| [pytest](https://docs.pytest.org/) | Testing |

## Running Checks

```bash
# All checks
uv run pypaginate qa

# Individual checks
uv run pypaginate lint      # Ruff linting
uv run pypaginate format    # Ruff formatting
uv run pypaginate typecheck # mypy
```

## Type Hints

### Required for All Public APIs

```python
# GOOD
def paginate(
    items: list[T],
    page: int,
    limit: int,
) -> Page[T]:
    ...

# BAD
def paginate(items, page, limit):
    ...
```

### Use Future Annotations

```python
from __future__ import annotations

# Enables: list[T] instead of List[T]
# Enables: T | None instead of Optional[T]
```

### Prefer `collections.abc`

```python
# GOOD
from collections.abc import Sequence, Mapping

def process(items: Sequence[int]) -> list[int]:
    ...

# AVOID
from typing import List, Sequence

def process(items: Sequence[int]) -> List[int]:
    ...
```

## Docstrings

### Google Style

```python
def paginate_entities(
    session: AsyncSession,
    query: Select,
    params: PageParams,
) -> Page[T]:
    """Paginate a SQLAlchemy query.
    
    Executes the query with offset pagination and returns
    a Page object containing the results.
    
    Args:
        session: Async SQLAlchemy session.
        query: Select statement to paginate.
        params: Pagination parameters.
    
    Returns:
        A Page object with items and metadata.
    
    Raises:
        PaginationError: If pagination fails.
    
    Example:
        >>> page = await paginate_entities(
        ...     session, select(User), PageParams(page=1, limit=20)
        ... )
        >>> print(page.total)
        100
    """
```

### Class Docstrings

```python
class SqlPaginator(Generic[T]):
    """SQL pagination engine using SQLAlchemy.
    
    This class provides offset-based pagination for SQLAlchemy
    queries with automatic count query generation.
    
    Attributes:
        session: The async session used for queries.
        clamp: Whether to clamp out-of-range pages.
    
    Example:
        >>> paginator = SqlPaginator(session, clamp=True)
        >>> page = await paginator.paginate(stmt, params)
    """
```

## Code Organization

### Imports

```python
# Standard library
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

# Third-party
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from pypaginate.core import Page, PageParams
from pypaginate.exceptions import PaginationError


if TYPE_CHECKING:
    from collections.abc import Sequence
```

### Module Structure

```python
"""Module docstring explaining purpose.

This module provides X functionality for Y use case.
"""

from __future__ import annotations

# Imports...

# Constants
DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# Type variables
T = TypeVar("T")


# Public classes/functions
class PublicClass:
    """Public class docstring."""
    ...


def public_function() -> None:
    """Public function docstring."""
    ...


# Private helpers (underscore prefix)
def _private_helper() -> None:
    ...


# Module exports
__all__ = [
    "PublicClass",
    "public_function",
]
```

## Naming Conventions

### Variables and Functions

```python
# snake_case for variables and functions
page_params = PageParams(page=1, limit=20)
total_count = calculate_total(items)

def get_pagination_params() -> PageParams:
    ...
```

### Classes

```python
# PascalCase for classes
class SqlPaginator:
    ...

class PageParams:
    ...
```

### Constants

```python
# UPPER_SNAKE_CASE for constants
DEFAULT_PAGE_SIZE = 20
MAX_RESULTS = 1000
```

### Private Members

```python
class Example:
    def __init__(self):
        self._private_attr = "internal"
    
    def _private_method(self):
        """Internal use only."""
        ...
```

## Dataclasses

### Immutable by Default

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PageParams:
    """Pagination parameters."""
    
    page: int = 1
    limit: int = 20
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and limit."""
        return (self.page - 1) * self.limit
```

### Why Frozen?

- Thread-safe
- Hashable (can be dict keys)
- Prevents accidental mutation
- Clearer intent

## Error Handling

### Custom Exceptions

```python
class PaginationError(Exception):
    """Base exception for pagination errors."""
    pass


class InvalidPageError(PaginationError):
    """Raised when page number is invalid."""
    pass
```

### Raising Exceptions

```python
def validate_page(page: int) -> None:
    """Validate page number.
    
    Raises:
        InvalidPageError: If page is less than 1.
    """
    if page < 1:
        raise InvalidPageError(
            f"Page must be >= 1, got {page}"
        )
```

## Async Patterns

### Async Functions

```python
async def paginate_entities(
    session: AsyncSession,
    query: Select,
    params: PageParams,
) -> Page[T]:
    """Async pagination function."""
    result = await session.execute(query)
    ...
```

### Context Managers

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_session():
    """Provide database session."""
    async with async_session() as session:
        yield session
```

## Quality Requirements

All code must pass:

- **Zero linting errors** (`ruff check`)
- **Proper formatting** (`ruff format`)
- **Type checking** (`mypy --strict`)
- **All tests pass** (`pytest`)
- **Test coverage** (>= 80%)

## Pre-commit Hooks

Install pre-commit to run checks automatically:

```bash
uv run pre-commit install
```

This runs ruff and mypy before each commit.

## See Also

- [Development Setup](development.md)
- [Testing Guide](testing.md)
- [Architecture](architecture.md)
