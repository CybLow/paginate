"""Offset pagination backends for SQLAlchemy (async and sync).

Implements ``PaginationBackend[T]`` and ``SyncPaginationBackend[T]``
protocols using SELECT COUNT(*) for counting and OFFSET/LIMIT for fetching.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from sqlalchemy.sql import Select


# -- Shared query builders ---------------------------------------------------


def _build_count_query(query: object) -> Any:
    """Build ``SELECT COUNT(*) FROM (subquery)``.

    Args:
        query: A SQLAlchemy Select statement.

    Returns:
        A count select statement.
    """
    from sqlalchemy import func, select

    stmt: Select[Any] = query  # type: ignore[assignment]
    return select(func.count()).select_from(stmt.subquery())


def _build_fetch_query(query: object, offset: int, limit: int) -> Any:
    """Apply OFFSET/LIMIT to a query.

    Args:
        query: A SQLAlchemy Select statement.
        offset: Rows to skip.
        limit: Maximum rows.

    Returns:
        The query with offset and limit applied.
    """
    stmt: Select[Any] = query  # type: ignore[assignment]
    return stmt.offset(offset).limit(limit)


# -- Async backend -----------------------------------------------------------


class SQLAlchemyBackend(Generic[ItemT]):
    """Async offset pagination backend for SQLAlchemy.

    Satisfies ``PaginationBackend[ItemT]`` protocol.

    Args:
        session: An async SQLAlchemy session.
    """

    __slots__ = ("_session",)

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count(self, query: object) -> int:
        """Count rows using ``SELECT COUNT(*) FROM (subquery)``.

        Args:
            query: A SQLAlchemy Select statement.

        Returns:
            Total number of matching rows.
        """
        result = await self._session.execute(_build_count_query(query))
        return result.scalar_one()  # type: ignore[no-any-return]

    async def fetch(
        self,
        query: object,
        offset: int,
        limit: int,
    ) -> list[ItemT]:
        """Fetch rows with OFFSET/LIMIT.

        Args:
            query: A SQLAlchemy Select statement.
            offset: Number of rows to skip.
            limit: Maximum rows to return.

        Returns:
            List of ORM entities for the requested slice.
        """
        result = await self._session.execute(
            _build_fetch_query(query, offset, limit),
        )
        return list(result.scalars().all())


# -- Sync backend ------------------------------------------------------------


class SyncSQLAlchemyBackend(Generic[ItemT]):
    """Sync offset pagination backend for SQLAlchemy.

    Satisfies ``SyncPaginationBackend[ItemT]`` protocol.

    Args:
        session: A synchronous SQLAlchemy session.
    """

    __slots__ = ("_session",)

    def __init__(self, session: Session) -> None:
        self._session = session

    def count(self, query: object) -> int:
        """Count rows using ``SELECT COUNT(*) FROM (subquery)``.

        Args:
            query: A SQLAlchemy Select statement.

        Returns:
            Total number of matching rows.
        """
        result = self._session.execute(_build_count_query(query))
        return result.scalar_one()  # type: ignore[no-any-return]

    def fetch(
        self,
        query: object,
        offset: int,
        limit: int,
    ) -> list[ItemT]:
        """Fetch rows with OFFSET/LIMIT.

        Args:
            query: A SQLAlchemy Select statement.
            offset: Number of rows to skip.
            limit: Maximum rows to return.

        Returns:
            List of ORM entities for the requested slice.
        """
        result = self._session.execute(
            _build_fetch_query(query, offset, limit),
        )
        return list(result.scalars().all())


__all__ = ["SQLAlchemyBackend", "SyncSQLAlchemyBackend"]
