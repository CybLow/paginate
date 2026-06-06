"""Offset pagination backends (async and sync).

Each backend counts matching rows with ``SELECT COUNT(*)`` and fetches the
requested window with OFFSET / LIMIT, returning an :class:`OffsetPage` whose
metadata is derived by the core. Filtering / sorting are applied by the caller
on the ``query`` before it is handed in.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from sqlalchemy import func, select

from pypaginate._native import build_offset_page
from pypaginate.pages import OffsetPage
from pypaginate.params import OffsetParams


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from sqlalchemy.sql import Select


def _count_stmt(query: object) -> Any:
    """Build ``SELECT COUNT(*) FROM (<query>)``."""
    return select(func.count()).select_from(cast("Select[Any]", query).subquery())


def _fetch_stmt(query: object, offset: int, limit: int) -> Any:
    """Apply OFFSET / LIMIT to ``query``."""
    return cast("Select[Any]", query).offset(offset).limit(limit)


class SQLAlchemyBackend(Generic[ItemT]):
    """Async offset pagination backend.

    Args:
        session: An async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count(self, query: object) -> int:
        """Count the rows matched by ``query``."""
        result = await self._session.execute(_count_stmt(query))
        return int(result.scalar_one())

    async def fetch(self, query: object, offset: int, limit: int) -> list[ItemT]:
        """Fetch the ``offset`` / ``limit`` window of ``query`` as scalars."""
        result = await self._session.execute(_fetch_stmt(query, offset, limit))
        return list(result.scalars().all())

    async def paginate(self, query: object, params: OffsetParams) -> OffsetPage[ItemT]:
        """Offset-paginate ``query`` into an :class:`OffsetPage`."""
        total = await self.count(query)
        items = await self.fetch(query, params.offset, params.limit)
        return build_offset_page(items, total, params)


class SyncSQLAlchemyBackend(Generic[ItemT]):
    """Sync offset pagination backend.

    Args:
        session: A synchronous SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def count(self, query: object) -> int:
        """Count the rows matched by ``query``."""
        result = self._session.execute(_count_stmt(query))
        return int(result.scalar_one())

    def fetch(self, query: object, offset: int, limit: int) -> list[ItemT]:
        """Fetch the ``offset`` / ``limit`` window of ``query`` as scalars."""
        result = self._session.execute(_fetch_stmt(query, offset, limit))
        return list(result.scalars().all())

    def paginate(self, query: object, params: OffsetParams) -> OffsetPage[ItemT]:
        """Offset-paginate ``query`` into an :class:`OffsetPage`."""
        total = self.count(query)
        items = self.fetch(query, params.offset, params.limit)
        return build_offset_page(items, total, params)


__all__ = ["SQLAlchemyBackend", "SyncSQLAlchemyBackend"]
