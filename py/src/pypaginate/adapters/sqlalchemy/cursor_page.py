"""Keyset page assembly for the SQLAlchemy cursor backends.

The decode → keyset-filter → re-order → fetch-prep → trim → encode mechanics,
kept separate from the (async/sync) backend adapter classes in
``cursor.py`` so each has a single responsibility. ``prepare_query`` and
``finalize_page`` are the two entry points the backends call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.adapters.sqlalchemy.keyset import (
    OrderColumn,
    build_keyset_condition,
    extract_order_columns,
)
from pypaginate.engine.cursor_codec import decode_cursor, encode_cursor


if TYPE_CHECKING:
    from sqlalchemy.sql import Select


def prepare_query(
    query: Select[Any],
    *,
    limit: int,
    after: str | None,
    before: str | None,
) -> tuple[Select[Any], list[OrderColumn], bool]:
    """Build the final SELECT with keyset filter and ``limit + 1``.

    Returns the prepared statement, the original ORDER BY columns, and whether
    this is a backward navigation.
    """
    order_cols = extract_order_columns(query)
    backwards = before is not None
    cursor_str = before or after
    stmt = query

    if cursor_str:
        stmt, nav_cols = _apply_keyset_filter(stmt, order_cols, cursor_str, backwards=backwards)
        stmt = _apply_order_by(stmt, nav_cols)
    return stmt.limit(limit + 1), order_cols, backwards


def finalize_page(
    rows: list[Any],
    order_cols: list[OrderColumn],
    *,
    limit: int,
    backwards: bool,
    has_cursor: bool,
) -> tuple[list[Any], str | None, str | None]:
    """Trim the ``limit + 1`` rows, reverse if backward, and compute cursors.

    Returns ``(items, next_cursor, prev_cursor)``.
    """
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
    if backwards:
        rows.reverse()
    next_c, prev_c = _compute_cursors(
        rows,
        order_cols,
        has_more=has_more,
        backwards=backwards,
        has_cursor=has_cursor,
    )
    return rows, next_c, prev_c


def _apply_keyset_filter(
    stmt: Select[Any],
    order_cols: list[OrderColumn],
    cursor_str: str,
    *,
    backwards: bool,
) -> tuple[Select[Any], list[OrderColumn]]:
    """Decode the cursor, optionally flip direction, and apply the WHERE."""
    cursor_values = decode_cursor(cursor_str)
    nav_cols = [c.reversed for c in order_cols] if backwards else order_cols
    condition = build_keyset_condition(nav_cols, cursor_values)
    return stmt.where(condition), nav_cols


def _apply_order_by(stmt: Select[Any], nav_cols: list[OrderColumn]) -> Select[Any]:
    """Replace ORDER BY with the (possibly flipped) navigation columns."""
    stmt = stmt.order_by(None)
    for col in nav_cols:
        stmt = stmt.order_by(col.order_clause)
    return stmt


def _extract_cursor_values(row: Any, order_cols: list[OrderColumn]) -> tuple[Any, ...]:
    """Extract the ORDER BY column values from a result row."""
    return tuple(getattr(row, str(col.element.key)) for col in order_cols)


def _compute_cursors(
    rows: list[Any],
    order_cols: list[OrderColumn],
    *,
    has_more: bool,
    backwards: bool,
    has_cursor: bool,
) -> tuple[str | None, str | None]:
    """Compute the ``(next_cursor, prev_cursor)`` strings from the page rows."""
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


__all__ = ["finalize_page", "prepare_query"]
