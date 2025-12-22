"""Helpers for building and executing COUNT queries."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from sqlalchemy import func, select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql import Select

    from ...database.types import CountStatement, SelectStatement

RowT = TypeVar("RowT", bound=tuple[object, ...])


def strip_ordering(query: Select[RowT]) -> Select[RowT]:
    """Return a statement without ORDER BY clauses.

    Removing ordering ensures the COUNT aggregate is not affected by
    user-provided sorting and can be delegated efficiently by the database.

    Args:
        query: Input SQLAlchemy Select statement.

    Returns:
        A new Select with ORDER BY removed.
    """
    return query.order_by(None)


def build_count_statement(
    query: SelectStatement,
    explicit: CountStatement | None,
    *,
    unique: bool
) -> CountStatement:
    """Build the statement used to compute the total number of rows.

    Args:
        query: Base Select statement to count from.
        explicit: Optional explicit count statement (takes precedence).
        unique: When True, count distinct rows to remove duplicates.

    Returns:
        A Select statement yielding a single int value.
    """
    if explicit is not None:
        return explicit
    base = strip_ordering(query).subquery()
    if unique:
        distinct_subq = select(*base.c.values()).distinct().subquery()
        return select(func.count()).select_from(distinct_subq)
    return select(func.count()).select_from(base)


async def fetch_count(session: AsyncSession, stmt: CountStatement) -> int:
    """Execute the count statement and return an integer.

    Args:
        session: Async SQLAlchemy session used to execute the statement.
        stmt: Statement returning a single integer value.

    Returns:
        The count coerced to int; returns 0 when no value is produced.
    """
    result = await session.execute(stmt)
    value = result.scalar_one_or_none()
    return int(value or 0)


__all__ = ["build_count_statement", "fetch_count", "strip_ordering"]
