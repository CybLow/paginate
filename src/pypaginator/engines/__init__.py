"""Pagination engines for different strategies.

This module provides the core pagination engines:
- MemoryPaginator: In-memory pagination
- SqlPaginator: SQL-based pagination

Each engine implements a specific pagination strategy.
Note: Keyset pagination is handled directly by SqlPaginator.
"""

from __future__ import annotations

from .memory import MemoryPaginator, filter_iter
try:
    from .sql import SqlPaginator
    _HAS_SQL = True
except ImportError:
    _HAS_SQL = False
    SqlPaginator = None  # type: ignore, get_pagination_strategy

__all__ = [
    "MemoryPaginator",
    "SqlPaginator",
    "filter_iter",
    "get_pagination_strategy",
]

if _HAS_SQL:
    __all__ += ["SqlPaginator"]
