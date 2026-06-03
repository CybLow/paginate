"""Backend contracts (ports) for the hexagonal architecture.

Each protocol defines the minimal interface a backend must implement.
Protocols are generic over query type ``Q`` and item type ``T``
for full type safety in backend implementations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec

Q = TypeVar("Q")
T = TypeVar("T")


@runtime_checkable
class PaginationBackend(Protocol[T]):
    """Async backend for offset-based pagination."""

    async def count(self, query: object) -> int:
        """Count total items matching the query."""
        ...

    async def fetch(
        self,
        query: object,
        offset: int,
        limit: int,
    ) -> list[T]:
        """Fetch a slice of items from the query."""
        ...


@runtime_checkable
class SyncPaginationBackend(Protocol[T]):
    """Sync backend for offset-based pagination."""

    def count(self, query: object) -> int:
        """Count total items matching the query."""
        ...

    def fetch(
        self,
        query: object,
        offset: int,
        limit: int,
    ) -> list[T]:
        """Fetch a slice of items from the query."""
        ...


@runtime_checkable
class CursorBackend(Protocol[T]):
    """Async backend for cursor/keyset-based pagination."""

    async def fetch_page(
        self,
        query: object,
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[T], str | None, str | None]:
        """Fetch a page: returns (items, next_cursor, prev_cursor)."""
        ...


@runtime_checkable
class FilterBackend(Protocol):
    """Translates filter specs to backend query conditions."""

    def apply_filters(
        self,
        query: object,
        filters: Sequence[FilterSpec],
    ) -> object:
        """Apply filter specifications to a query."""
        ...


@runtime_checkable
class SortBackend(Protocol):
    """Translates sort specs to backend query ordering."""

    @staticmethod
    def apply_sorting(
        query: object,
        sorting: Sequence[SortSpec],
    ) -> object:
        """Apply sort specifications to a query."""
        ...


@runtime_checkable
class SearchBackend(Protocol):
    """Translates search specs to backend query conditions."""

    @staticmethod
    def apply_search(
        query: object,
        spec: SearchSpec,
    ) -> object:
        """Apply search specification to a query."""
        ...


__all__ = [
    "CursorBackend",
    "FilterBackend",
    "PaginationBackend",
    "SearchBackend",
    "SortBackend",
    "SyncPaginationBackend",
]
