"""Cursor / keyset pagination backends (async and sync).

Each backend over-fetches ``limit + 1`` rows for a keyset-ordered query and
returns a :class:`CursorPage`; the page-assembly mechanics live in
:mod:`pypaginate.adapters.sqlalchemy.cursor_page`. The query must carry an
ORDER BY that uniquely orders rows (e.g. a trailing primary key).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pypaginate.adapters.sqlalchemy.cursor_page import finalize_page, prepare_query
from pypaginate.pages import CursorPage
from pypaginate.params import CursorParams


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from sqlalchemy.sql import Select


class SQLAlchemyCursorBackend(Generic[ItemT]):
    """Async cursor / keyset pagination backend.

    Args:
        session: An async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_page(self, query: Select[Any], params: CursorParams) -> CursorPage[ItemT]:
        """Fetch one keyset page for ``query`` as a :class:`CursorPage`.

        Args:
            query: A SQLAlchemy Select with an ORDER BY clause.
            params: The cursor request (limit + optional after / before).

        Returns:
            The matched page with next / previous cursors.
        """
        stmt, order_cols = prepare_query(query, params)
        result = await self._session.execute(stmt)
        rows: list[Any] = list(result.scalars().all())
        return finalize_page(rows, order_cols, params)


class SyncSQLAlchemyCursorBackend(Generic[ItemT]):
    """Sync cursor / keyset pagination backend.

    Args:
        session: A synchronous SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_page(self, query: Select[Any], params: CursorParams) -> CursorPage[ItemT]:
        """Fetch one keyset page for ``query`` as a :class:`CursorPage`.

        Args:
            query: A SQLAlchemy Select with an ORDER BY clause.
            params: The cursor request (limit + optional after / before).

        Returns:
            The matched page with next / previous cursors.
        """
        stmt, order_cols = prepare_query(query, params)
        result = self._session.execute(stmt)
        rows: list[Any] = list(result.scalars().all())
        return finalize_page(rows, order_cols, params)


__all__ = ["SQLAlchemyCursorBackend", "SyncSQLAlchemyCursorBackend"]
