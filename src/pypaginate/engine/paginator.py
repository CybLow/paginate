"""Sync and async paginators for offset-based pagination.

Each paginator owns the pipeline: count -> clamp -> fetch -> OffsetPage.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pypaginate.domain.enums import OverflowStrategy
from pypaginate.domain.models import OffsetPage, OffsetParams
from pypaginate.domain.protocols import PaginationBackend, SyncPaginationBackend


ItemT = TypeVar("ItemT")


class Paginator(Generic[ItemT]):
    """Sync orchestrator: count -> clamp -> fetch -> OffsetPage."""

    __slots__ = ("_backend", "_overflow")

    def __init__(
        self,
        backend: SyncPaginationBackend[ItemT],
        *,
        overflow: OverflowStrategy = OverflowStrategy.EMPTY,
    ) -> None:
        self._backend = backend
        self._overflow = overflow

    def paginate(
        self,
        query: object,
        params: OffsetParams,
    ) -> Any:
        """Execute the sync pagination pipeline.

        Args:
            query: Backend-specific query or data source.
            params: Offset pagination parameters.

        Returns:
            OffsetPage (or FastOffsetPage if msgspec installed).
        """
        total = self._backend.count(query)
        effective = self._apply_overflow(params, total)
        if total <= 0 or effective.offset >= total:
            return OffsetPage.create([], total, effective)
        items = self._backend.fetch(query, effective.offset, effective.limit)
        return OffsetPage.create(items, total, effective)

    def _apply_overflow(
        self,
        params: OffsetParams,
        total: int,
    ) -> OffsetParams:
        if self._overflow is OverflowStrategy.CLAMP:
            return params.clamp(total)
        return params


class AsyncPaginator(Generic[ItemT]):
    """Async orchestrator: count -> clamp -> fetch -> OffsetPage."""

    __slots__ = ("_backend", "_overflow")

    def __init__(
        self,
        backend: PaginationBackend[ItemT],
        *,
        overflow: OverflowStrategy = OverflowStrategy.EMPTY,
    ) -> None:
        self._backend = backend
        self._overflow = overflow

    async def paginate(
        self,
        query: object,
        params: OffsetParams,
    ) -> Any:
        """Execute the async pagination pipeline.

        Args:
            query: Backend-specific query object.
            params: Offset pagination parameters.

        Returns:
            OffsetPage (or FastOffsetPage if msgspec installed).
        """
        total = await self._backend.count(query)
        effective = self._apply_overflow(params, total)
        if total <= 0 or effective.offset >= total:
            return OffsetPage.create([], total, effective)
        items = await self._backend.fetch(query, effective.offset, effective.limit)
        return OffsetPage.create(items, total, effective)

    def _apply_overflow(
        self,
        params: OffsetParams,
        total: int,
    ) -> OffsetParams:
        if self._overflow is OverflowStrategy.CLAMP:
            return params.clamp(total)
        return params


__all__ = ["AsyncPaginator", "Paginator"]
