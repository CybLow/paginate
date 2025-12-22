"""Keyset pagination runtime and execution.

This module provides keyset (cursor-based) pagination functionality.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING

from sqlakeyset import Page as KeysetPage
from sqlakeyset.asyncio import select_page as sqlakeyset_select_page

from ..core.snapshots import coerce_bookmark

if TYPE_CHECKING:  # pragma: no cover - typing only
    from sqlalchemy.ext.asyncio import AsyncSession

    from ..core.pages import KeysetPageParams
    from ..database.types import SelectStatement

RowSequence = Sequence[object]

SelectPageCallable = Callable[..., Awaitable[KeysetPage[RowSequence]]]


async def select_keyset_page(
    session: AsyncSession,
    query: SelectStatement,
    params: KeysetPageParams,
    *,
    unique: bool,
) -> KeysetPage[RowSequence]:
    """Execute a keyset pagination query using sqlakeyset.

    This helper delegates to sqlakeyset.asyncio.select_page with arguments
    derived from the strongly-typed pagination parameters.

    Args:
        session: Async SQLAlchemy session used to execute the query.
        query: Concrete Select statement to paginate.
        params: Keyset pagination parameters (limit and optional bookmarks).
        unique: Whether to enforce unique rows prior to pagination.

    Returns:
        A sqlakeyset.Page instance carrying the selected rows and runtime
        paging metadata.
    """
    kwargs = _keyset_kwargs(params, unique)
    select_page: SelectPageCallable = sqlakeyset_select_page
    page = await select_page(session, query, **kwargs)
    return page


def _keyset_kwargs(params: KeysetPageParams, unique: bool) -> dict[str, object]:
    """Build keyword arguments for sqlakeyset.select_page.

    Args:
        params: Typed keyset parameters (limit, after, before, page).
        unique: Whether to enforce uniqueness before computing the page.

    Returns:
        A dictionary of keyword arguments accepted by select_page.
    """
    return {
        "per_page": params.limit,
        "unique": unique,
        "after": coerce_bookmark(params.after),
        "before": coerce_bookmark(params.before),
        "page": params.page,
    }


__all__ = ["select_keyset_page"]
