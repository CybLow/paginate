"""Async offset pagination backend for SQLAlchemy.

Implements ``PaginationBackend[T]`` protocol using SELECT COUNT(*)
for counting and OFFSET/LIMIT for fetching.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql import Select


class SQLAlchemyBackend(Generic[ItemT]):
    """Async offset pagination backend for SQLAlchemy.

    Satisfies ``PaginationBackend[ItemT]`` protocol.

    Args:
        session: An async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count(self, query: object) -> int:
        """Count rows using ``SELECT COUNT(*) FROM (subquery)``.

        Args:
            query: A SQLAlchemy Select statement.

        Returns:
            Total number of matching rows.
        """
        return await _execute_count(self._session, query)

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
        return await _execute_fetch(self._session, query, offset, limit)


async def _execute_count(session: AsyncSession, query: object) -> int:
    """Build and execute a count subquery.

    Args:
        session: The async session.
        query: A SQLAlchemy Select statement.

    Returns:
        The scalar count result.
    """
    from sqlalchemy import func, select

    stmt: Select[Any] = query  # type: ignore[assignment]
    count_stmt = select(func.count()).select_from(stmt.subquery())
    result = await session.execute(count_stmt)
    return result.scalar_one()


async def _execute_fetch(
    session: AsyncSession,
    query: object,
    offset: int,
    limit: int,
) -> list[Any]:
    """Apply offset/limit and execute the query.

    Args:
        session: The async session.
        query: A SQLAlchemy Select statement.
        offset: Rows to skip.
        limit: Maximum rows.

    Returns:
        List of scalar results (ORM entities).
    """
    stmt: Select[Any] = query  # type: ignore[assignment]
    result = await session.execute(stmt.offset(offset).limit(limit))
    return list(result.scalars().all())


__all__ = ["SQLAlchemyBackend"]
