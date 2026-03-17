"""Cursor/keyset pagination backends (async and sync).

Implements ``CursorBackend[T]`` protocol using built-in cursor
encoding and keyset WHERE clause construction. Requires the query
to have an ORDER BY clause.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pypaginate.adapters.sqlalchemy.cursor_codec import decode_cursor, encode_cursor
from pypaginate.adapters.sqlalchemy.keyset import (
    OrderColumn,
    build_keyset_condition,
    extract_order_columns,
)


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from sqlalchemy.sql import Select


# -- Shared helpers ----------------------------------------------------------


def _apply_keyset_filter(
    stmt: Select[Any],
    order_cols: list[OrderColumn],
    cursor_str: str,
    *,
    backwards: bool,
) -> tuple[Select[Any], list[OrderColumn]]:
    """Decode cursor, optionally flip direction, apply WHERE.

    Args:
        stmt: The current SELECT statement.
        order_cols: Original ORDER BY columns.
        cursor_str: Encoded cursor string.
        backwards: Whether navigating backward.

    Returns:
        Tuple of (modified statement, navigation columns).
    """
    cursor_values = decode_cursor(cursor_str)
    nav_cols = [c.reversed for c in order_cols] if backwards else order_cols
    condition = build_keyset_condition(nav_cols, cursor_values)
    return stmt.where(condition), nav_cols


def _apply_order_by(
    stmt: Select[Any],
    nav_cols: list[OrderColumn],
) -> Select[Any]:
    """Replace ORDER BY with navigation columns.

    Args:
        stmt: The current SELECT statement.
        nav_cols: Columns with (possibly flipped) directions.

    Returns:
        Statement with updated ORDER BY.
    """
    stmt = stmt.order_by(None)
    for col in nav_cols:
        stmt = stmt.order_by(col.order_clause)
    return stmt


def _extract_cursor_values(
    row: Any,
    order_cols: list[OrderColumn],
) -> tuple[Any, ...]:
    """Extract ORDER BY column values from a result row.

    Args:
        row: An ORM model instance or row object.
        order_cols: The original ORDER BY columns.

    Returns:
        Tuple of values matching each ORDER BY column.
    """
    return tuple(
        getattr(row, col.element.key)  # type: ignore[arg-type]
        for col in order_cols
    )


def _compute_cursors(
    rows: list[Any],
    order_cols: list[OrderColumn],
    *,
    has_more: bool,
    backwards: bool,
    has_cursor: bool,
) -> tuple[str | None, str | None]:
    """Compute next/prev cursor strings from result rows.

    Args:
        rows: The fetched result rows (already trimmed).
        order_cols: Original ORDER BY columns.
        has_more: Whether extra rows were returned beyond limit.
        backwards: Whether this was a backward navigation.
        has_cursor: Whether a cursor was provided in the request.

    Returns:
        Tuple of (next_cursor, prev_cursor).
    """
    if not rows:
        return None, None
    first_vals = _extract_cursor_values(rows[0], order_cols)
    last_vals = _extract_cursor_values(rows[-1], order_cols)
    if backwards:
        return (
            encode_cursor(last_vals) if rows else None,
            encode_cursor(first_vals) if has_more else None,
        )
    if has_cursor:
        return (
            encode_cursor(last_vals) if has_more else None,
            encode_cursor(first_vals),
        )
    return encode_cursor(last_vals) if has_more else None, None


# -- Async backend -----------------------------------------------------------


class SQLAlchemyCursorBackend(Generic[ItemT]):
    """Async cursor/keyset pagination backend.

    Satisfies ``CursorBackend[ItemT]`` protocol.

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
        """Fetch a keyset-paginated page.

        Args:
            query: A SQLAlchemy Select with ORDER BY.
            limit: Maximum items per page.
            after: Cursor for the next page.
            before: Cursor for the previous page.

        Returns:
            Tuple of (items, next_cursor, prev_cursor).
        """
        stmt, order_cols, backwards = _prepare_query(
            query, limit=limit, after=after, before=before,
        )
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        return _finalize_page(
            rows, order_cols, limit=limit, backwards=backwards,
            has_cursor=bool(after or before),
        )


# -- Sync backend ------------------------------------------------------------


class SyncSQLAlchemyCursorBackend(Generic[ItemT]):
    """Sync cursor/keyset pagination backend.

    Satisfies cursor backend contract for synchronous sessions.

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
        """Fetch a keyset-paginated page.

        Args:
            query: A SQLAlchemy Select with ORDER BY.
            limit: Maximum items per page.
            after: Cursor for the next page.
            before: Cursor for the previous page.

        Returns:
            Tuple of (items, next_cursor, prev_cursor).
        """
        stmt, order_cols, backwards = _prepare_query(
            query, limit=limit, after=after, before=before,
        )
        result = self._session.execute(stmt)
        rows = list(result.scalars().all())
        return _finalize_page(
            rows, order_cols, limit=limit, backwards=backwards,
            has_cursor=bool(after or before),
        )


# -- Private execution helpers -----------------------------------------------


def _prepare_query(
    query: Select[Any],
    *,
    limit: int,
    after: str | None,
    before: str | None,
) -> tuple[Select[Any], list[OrderColumn], bool]:
    """Build the final SELECT with keyset filter and limit+1.

    Args:
        query: Original SELECT with ORDER BY.
        limit: Page size.
        after: Forward cursor string.
        before: Backward cursor string.

    Returns:
        Tuple of (prepared statement, order columns, is_backwards).
    """
    order_cols = extract_order_columns(query)
    backwards = before is not None
    cursor_str = before or after
    stmt = query

    if cursor_str:
        stmt, nav_cols = _apply_keyset_filter(
            stmt, order_cols, cursor_str, backwards=backwards,
        )
        stmt = _apply_order_by(stmt, nav_cols)
    return stmt.limit(limit + 1), order_cols, backwards


def _finalize_page(
    rows: list[Any],
    order_cols: list[OrderColumn],
    *,
    limit: int,
    backwards: bool,
    has_cursor: bool,
) -> tuple[list[Any], str | None, str | None]:
    """Trim rows, reverse if needed, compute cursors.

    Args:
        rows: Raw result rows (may be limit+1).
        order_cols: Original ORDER BY columns.
        limit: Page size.
        backwards: Whether navigating backward.
        has_cursor: Whether a cursor was in the request.

    Returns:
        Tuple of (items, next_cursor, prev_cursor).
    """
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
    if backwards:
        rows.reverse()
    next_c, prev_c = _compute_cursors(
        rows, order_cols,
        has_more=has_more, backwards=backwards, has_cursor=has_cursor,
    )
    return rows, next_c, prev_c


__all__ = ["SQLAlchemyCursorBackend", "SyncSQLAlchemyCursorBackend"]
