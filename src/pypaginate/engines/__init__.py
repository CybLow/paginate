"""Pagination engines for different strategies.

This module provides the core pagination engines:
- MemoryPaginator: In-memory pagination
- SqlPaginator: SQL-based pagination

Each engine implements a specific pagination strategy.
Note: Keyset pagination is handled directly by SqlPaginator.
"""

from __future__ import annotations

from .memory import MemoryPaginator, filter_iter
from .sql import SqlPaginator


__all__ = [
    "MemoryPaginator",
    "SqlPaginator",
    "filter_iter",
    "get_pagination_strategy",
]
