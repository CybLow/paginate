"""Modern pagination toolkit for Python.

PyPaginator is a framework-agnostic pagination library that provides powerful
features for paginating, filtering, and searching data. It works seamlessly with
SQLAlchemy (async/sync), in-memory collections, and can be extended to support
other ORMs.

Quick Start
-----------
>>> from pypaginator import PageParams, paginate_entities
>>> params = PageParams(page=1, limit=20)
>>> page = await paginate_entities(session, select(User), params)

Architecture
------------
The pagination module is organized by responsibility:

- core/: Base types (Page, PageParams, PaginationSnapshot)
- engines/: Pagination strategies (MemoryPaginator, SqlPaginator, KeysetPaginator)
- query/: Query construction and execution (paginate_* functions)
- filters/: Filtering and search (predicates and text search)
- sorting/: Sorting utilities
- text/: Text normalization
- database/: Database utilities

Public API
----------
From core:
    Page, PageParams, KeysetPageParams

From query:
    paginate_entities, paginate_entities_to_page
    paginate_rows, paginate_rows_to_page

From exceptions:
    PaginatorException, PaginationConfigurationError, FilterException,
    SearchException, SortException, ValidationException

For advanced usage, import from submodules:
    from pypaginator.engines import MemoryPaginator
    from pypaginator.filters.predicates import FilterEngine
    from pypaginator.filters.search import SqlSearchService
    from pypaginator.sorting import SortEngine
"""

from __future__ import annotations

# Core types
from .core import KeysetPageParams, Page, PageParams

# Exceptions
from .exceptions import (
    FilterException,
    PaginationConfigurationError,
    PaginatorException,
    SearchException,
    SortException,
    ValidationException,
)

# Main query functions (with optional SQLAlchemy support)
try:
    from .query import (
        paginate_entities,
        paginate_entities_to_page,
        paginate_rows,
        paginate_rows_to_page,
    )

    _HAS_SQLALCHEMY = True
except ImportError:
    _HAS_SQLALCHEMY = False

    # Provide stubs that raise helpful errors
    def _sqlalchemy_required(*args, **kwargs):  # type: ignore
        raise ImportError(
            "SQLAlchemy features require installation: pip install pypaginator[sqlalchemy]"
        )

    paginate_entities = _sqlalchemy_required  # type: ignore
    paginate_entities_to_page = _sqlalchemy_required  # type: ignore
    paginate_rows = _sqlalchemy_required  # type: ignore
    paginate_rows_to_page = _sqlalchemy_required  # type: ignore


__version__ = "0.1.0"

__all__ = [
    # Core types
    "Page",
    "PageParams",
    "KeysetPageParams",
    # Main functions (SQLAlchemy)
    "paginate_entities",
    "paginate_entities_to_page",
    "paginate_rows",
    "paginate_rows_to_page",
    # Exceptions
    "PaginatorException",
    "PaginationConfigurationError",
    "FilterException",
    "SearchException",
    "SortException",
    "ValidationException",
    # Version
    "__version__",
]

