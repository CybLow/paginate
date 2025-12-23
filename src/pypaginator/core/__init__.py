"""Core pagination types and utilities.

This module provides the fundamental types for pagination:
- PageParams, KeysetPageParams: Pagination parameters
- Page: Generic page result container
- PaginationContext: Execution context
- PaginationSnapshot, KeysetPaginationSnapshot: Result snapshots
"""

from __future__ import annotations

from .context import PaginationContext, clamp_page_params
from .pages import KeysetPageParams, Page, PageParams
from .snapshots import KeysetPaginationSnapshot, PaginationSnapshot


__all__ = [
    "KeysetPageParams",
    "KeysetPaginationSnapshot",
    # Pages
    "Page",
    "PageParams",
    # Context
    "PaginationContext",
    # Snapshots
    "PaginationSnapshot",
    "clamp_page_params",
]
