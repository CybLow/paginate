"""Cursor/keyset pagination backends (async and sync).

Implements the ``CursorBackend[T]`` protocol using built-in cursor encoding and
keyset WHERE-clause construction; the query must carry an ORDER BY. The keyset
page-assembly mechanics live in :mod:`pypaginate.adapters.sqlalchemy.cursor_page`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pypaginate.adapters.sqlalchemy.cursor_page import finalize_page, prepare_query


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from sqlalchemy.sql import Select


class SQLAlchemyCursorBackend(Generic[ItemT]):
    """Async cursor/keyset pagination backend (satisfies ``CursorBackend[ItemT]``).

    Args:
        session: An async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_page(
        self,
        query: Select[Any],
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[ItemT], str | None, str | None]:
        """Fetch a keyset-paginated page as ``(items, next_cursor, prev_cursor)``.

        Args:
            query: A SQLAlchemy Select with ORDER BY.
            limit: Maximum items per page.
            after: Cursor for the next page.
            before: Cursor for the previous page.
        """
        stmt, order_cols, backwards = prepare_query(query, limit=limit, after=after, before=before)
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        return finalize_page(
            rows,
            order_cols,
            limit=limit,
            backwards=backwards,
            has_cursor=bool(after or before),
        )


class SyncSQLAlchemyCursorBackend(Generic[ItemT]):
    """Sync cursor/keyset pagination backend (synchronous-session variant).

    Args:
        session: A synchronous SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_page(
        self,
        query: Select[Any],
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[ItemT], str | None, str | None]:
        """Fetch a keyset-paginated page as ``(items, next_cursor, prev_cursor)``.

        Args:
            query: A SQLAlchemy Select with ORDER BY.
            limit: Maximum items per page.
            after: Cursor for the next page.
            before: Cursor for the previous page.
        """
        stmt, order_cols, backwards = prepare_query(query, limit=limit, after=after, before=before)
        result = self._session.execute(stmt)
        rows = list(result.scalars().all())
        return finalize_page(
            rows,
            order_cols,
            limit=limit,
            backwards=backwards,
            has_cursor=bool(after or before),
        )


__all__ = ["SQLAlchemyCursorBackend", "SyncSQLAlchemyCursorBackend"]
