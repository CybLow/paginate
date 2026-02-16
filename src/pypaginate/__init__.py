"""Modern pagination toolkit for Python.

pypaginate is a framework-agnostic pagination library that provides powerful
features for paginating, filtering, and searching data. It works seamlessly with
SQLAlchemy (async/sync), in-memory collections, and can be extended to support
other ORMs.

Quick Start
-----------

.. code-block:: python

    from pypaginate import PageParams, paginate_entities

    params = PageParams(page=1, limit=20)
    page = await paginate_entities(session, select(User), params)

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

For advanced usage, import from submodules::

    from pypaginate.engines import MemoryPaginator
    from pypaginate.filters.predicates import FilterEngine
    from pypaginate.filters.search import SqlSearchService
    from pypaginate.sorting import SortEngine
"""

from __future__ import annotations

# Core types
from .core import KeysetPageParams, Page, PageParams

# Exceptions
from .exceptions import (
    FilterException,
    FilterValidationError,
    PaginationConfigurationError,
    PaginatorException,
    SearchException,
    SearchNormalizationError,
    SearchQueryError,
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
    def _sqlalchemy_required(*args: object, **kwargs: object) -> object:
        raise ImportError(
            "SQLAlchemy features require installation: pip install pypaginate[sqlalchemy]"
        )

    paginate_entities = _sqlalchemy_required  # type: ignore[assignment]
    paginate_entities_to_page = _sqlalchemy_required  # type: ignore[assignment]
    paginate_rows = _sqlalchemy_required  # type: ignore[assignment]
    paginate_rows_to_page = _sqlalchemy_required  # type: ignore[assignment]


__version__ = "0.1.0"

__all__ = [
    "FilterException",
    "KeysetPageParams",
    # Core types
    "Page",
    "PageParams",
    "PaginationConfigurationError",
    # Exceptions
    "PaginatorException",
    "SearchException",
    "SortException",
    "ValidationException",
    # Version
    "__version__",
    # Main functions (SQLAlchemy)
    "paginate_entities",
    "paginate_entities_to_page",
    "paginate_rows",
    "paginate_rows_to_page",
]
