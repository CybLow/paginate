"""Cursor/keyset paginators for cursor-based pagination.

Delegates fetch_page to a CursorBackend and builds a CursorPage.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pypaginate.domain.models import CursorPage, CursorParams
from pypaginate.domain.protocols import CursorBackend


ItemT = TypeVar("ItemT")


class AsyncCursorPaginator(Generic[ItemT]):
    """Async orchestrator for cursor-based pagination."""

    __slots__ = ("_backend",)

    def __init__(self, backend: CursorBackend[ItemT]) -> None:
        self._backend = backend

    async def paginate(
        self,
        query: object,
        params: CursorParams,
    ) -> Any:
        """Execute cursor pagination.

        Args:
            query: Backend-specific query object.
            params: Cursor pagination parameters.

        Returns:
            CursorPage with navigation metadata.
        """
        items, next_cursor, prev_cursor = await self._backend.fetch_page(
            query,
            limit=params.limit,
            after=params.after,
            before=params.before,
        )
        return CursorPage.create(
            items,
            params,
            next_cursor=next_cursor,
            previous_cursor=prev_cursor,
        )


__all__ = ["AsyncCursorPaginator"]
