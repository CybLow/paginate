"""Keyset page assembly for the SQLAlchemy cursor backends.

Holds the decode -> keyset-filter -> re-order -> over-fetch -> trim -> encode
mechanics, kept separate from the (async / sync) backend classes in
:mod:`pypaginate.adapters.sqlalchemy.cursor`. ``prepare_query`` and
``finalize_page`` are the two entry points the backends call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate._core import decode_cursor, encode_cursor
from pypaginate.adapters.sqlalchemy.keyset import (
    OrderColumn,
    build_keyset_condition,
    extract_order_columns,
)
from pypaginate.pages import CursorPage
from pypaginate.params import CursorParams


if TYPE_CHECKING:
    from sqlalchemy.sql import Select


def _backwards(params: CursorParams) -> bool:
    """Whether this request pages backward (a ``before`` cursor was given)."""
    return params.before is not None


def _token(params: CursorParams) -> str | None:
    """The active cursor token (``before`` wins over ``after``)."""
    return params.before or params.after


def prepare_query(
    query: Select[Any], params: CursorParams
) -> tuple[Select[Any], list[OrderColumn]]:
    """Build the keyset-filtered SELECT over-fetching ``limit + 1`` rows.

    Args:
        query: A SQLAlchemy Select carrying an ORDER BY clause.
        params: The cursor request (limit + optional after / before).

    Returns:
        The prepared statement and the original ORDER BY columns.
    """
    order_cols = extract_order_columns(query)
    stmt = query
    token = _token(params)
    if token is not None:
        stmt, nav_cols = _apply_keyset(stmt, order_cols, token, backwards=_backwards(params))
        stmt = _apply_order_by(stmt, nav_cols)
    return stmt.limit(params.limit + 1), order_cols


def finalize_page(
    rows: list[Any], order_cols: list[OrderColumn], params: CursorParams
) -> CursorPage[Any]:
    """Trim the over-fetched rows, reverse if backward, and compute cursors.

    Args:
        rows: The (up to ``limit + 1``) fetched rows.
        order_cols: The original ORDER BY columns.
        params: The cursor request that produced ``rows``.

    Returns:
        A :class:`CursorPage` with next / previous cursors.
    """
    has_more = len(rows) > params.limit
    page_rows = rows[: params.limit] if has_more else rows
    if _backwards(params):
        page_rows = list(reversed(page_rows))
    next_c, prev_c = _cursors(page_rows, order_cols, params, has_more=has_more)
    return CursorPage(
        items=page_rows,
        limit=params.limit,
        has_next=next_c is not None,
        has_previous=prev_c is not None,
        next_cursor=next_c,
        previous_cursor=prev_c,
    )


def _apply_keyset(
    stmt: Select[Any], order_cols: list[OrderColumn], token: str, *, backwards: bool
) -> tuple[Select[Any], list[OrderColumn]]:
    """Decode the cursor, flip direction if backward, and apply the WHERE."""
    nav_cols = [c.reversed for c in order_cols] if backwards else order_cols
    condition = build_keyset_condition(nav_cols, decode_cursor(token))
    return stmt.where(condition), nav_cols


def _apply_order_by(stmt: Select[Any], nav_cols: list[OrderColumn]) -> Select[Any]:
    """Replace ORDER BY with the (possibly flipped) navigation columns."""
    stmt = stmt.order_by(None)
    for col in nav_cols:
        stmt = stmt.order_by(col.order_clause)
    return stmt


def _values(row: Any, order_cols: list[OrderColumn]) -> tuple[Any, ...]:
    """Extract the ORDER BY column values from one result row."""
    return tuple(getattr(row, str(col.element.key)) for col in order_cols)


def _cursors(
    rows: list[Any], order_cols: list[OrderColumn], params: CursorParams, *, has_more: bool
) -> tuple[str | None, str | None]:
    """Compute ``(next_cursor, previous_cursor)`` from the trimmed page rows."""
    if not rows:
        return None, None
    first = _values(rows[0], order_cols)
    last = _values(rows[-1], order_cols)
    if _backwards(params):
        return encode_cursor(last), (encode_cursor(first) if has_more else None)
    if _token(params) is not None:
        return (encode_cursor(last) if has_more else None), encode_cursor(first)
    return (encode_cursor(last) if has_more else None), None


__all__ = ["finalize_page", "prepare_query"]
