"""Core pagination types and utilities.

This module provides the fundamental types for pagination:
- PageParams, KeysetPageParams: Pagination parameters
- Page: Generic page result container
- PaginationContext: Execution context
- PaginationSnapshot, KeysetPaginationSnapshot: Result snapshots
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .context import PaginationContext, clamp_page_params
from .pages import KeysetPageParams, Page, PageParams


# Lazy import for sqlakeyset-dependent types
def __getattr__(name: str) -> object:
    """Lazy import for optional sqlakeyset-dependent types."""
    if name in ("KeysetPaginationSnapshot", "PaginationSnapshot"):
        from .snapshots import KeysetPaginationSnapshot, PaginationSnapshot

        if name == "KeysetPaginationSnapshot":
            return KeysetPaginationSnapshot
        return PaginationSnapshot
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if TYPE_CHECKING:
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
