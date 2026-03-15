"""Cursor/keyset pagination backends using sqlakeyset (async and sync).

Implements ``CursorBackend[T]`` protocol. Requires the query
to have an ORDER BY clause (sqlakeyset requirement).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session


# -- Shared helpers ----------------------------------------------------------


def _deserialize_markers(
    after: str | None,
    before: str | None,
) -> tuple[Any, Any]:
    """Deserialize bookmark strings into sqlakeyset markers.

    Args:
        after: Forward bookmark string.
        before: Backward bookmark string.

    Returns:
        Tuple of (after_marker, before_marker).
    """
    from sqlakeyset import unserialize_bookmark  # pragma: no cover

    after_marker = unserialize_bookmark(after) if after else None  # pragma: no cover
    before_marker = unserialize_bookmark(before) if before else None  # pragma: no cover
    return after_marker, before_marker  # pragma: no cover


def _extract_results(page: Any) -> tuple[list[Any], str | None, str | None]:
    """Extract items and cursors from a sqlakeyset Page.

    Args:
        page: A sqlakeyset Page object with paging metadata.

    Returns:
        Tuple of (items, next_cursor, prev_cursor).
    """
    items = [row[0] if hasattr(row, "_mapping") else row for row in page]
    paging = page.paging
    next_cursor = paging.bookmark_next if paging.has_next else None
    prev_cursor = paging.bookmark_previous if paging.has_previous else None
    return items, next_cursor, prev_cursor


# -- Async backend -----------------------------------------------------------


class SQLAlchemyCursorBackend(Generic[ItemT]):
    """Async cursor/keyset pagination backend using sqlakeyset.

    Satisfies ``CursorBackend[ItemT]`` protocol.

    Args:
        session: An async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_page(
        self,
        query: object,
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[ItemT], str | None, str | None]:
        """Fetch a keyset-paginated page via sqlakeyset.

        Args:
            query: A SQLAlchemy Select with ORDER BY.
            limit: Maximum items per page.
            after: Bookmark cursor for the next page.
            before: Bookmark cursor for the previous page.

        Returns:
            Tuple of (items, next_cursor, prev_cursor).
        """
        page = await _async_select_page(
            self._session,
            query,
            limit,
            after,
            before,
        )
        return _extract_results(page)


# -- Sync backend ------------------------------------------------------------


class SyncSQLAlchemyCursorBackend(Generic[ItemT]):
    """Sync cursor/keyset pagination backend using sqlakeyset.

    Satisfies cursor backend contract for synchronous sessions.

    Args:
        session: A synchronous SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_page(
        self,
        query: object,
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[ItemT], str | None, str | None]:
        """Fetch a keyset-paginated page via sqlakeyset.

        Args:
            query: A SQLAlchemy Select with ORDER BY.
            limit: Maximum items per page.
            after: Bookmark cursor for the next page.
            before: Bookmark cursor for the previous page.

        Returns:
            Tuple of (items, next_cursor, prev_cursor).
        """
        page = _sync_select_page(
            self._session,
            query,
            limit,
            after,
            before,
        )
        return _extract_results(page)


# -- Private execution helpers -----------------------------------------------


async def _async_select_page(
    session: Any,
    query: object,
    limit: int,
    after: str | None,
    before: str | None,
) -> Any:
    """Execute sqlakeyset's async select_page.

    Args:
        session: The async session.
        query: A SQLAlchemy Select with ORDER BY.
        limit: Page size.
        after: Forward bookmark string.
        before: Backward bookmark string.

    Returns:
        A sqlakeyset Page object.
    """
    from sqlakeyset.asyncio import select_page  # pragma: no cover

    after_m, before_m = _deserialize_markers(after, before)  # pragma: no cover
    return await select_page(  # pragma: no cover
        session,
        query,  # type: ignore[arg-type]
        per_page=limit,
        after=after_m,
        before=before_m,
    )


def _sync_select_page(
    session: Any,
    query: object,
    limit: int,
    after: str | None,
    before: str | None,
) -> Any:
    """Execute sqlakeyset's sync select_page.

    Args:
        session: The sync session.
        query: A SQLAlchemy Select with ORDER BY.
        limit: Page size.
        after: Forward bookmark string.
        before: Backward bookmark string.

    Returns:
        A sqlakeyset Page object.
    """
    from sqlakeyset import select_page  # pragma: no cover

    after_m, before_m = _deserialize_markers(after, before)  # pragma: no cover
    return select_page(  # pragma: no cover
        session,
        query,  # type: ignore[arg-type]
        per_page=limit,
        after=after_m,
        before=before_m,
    )


__all__ = ["SQLAlchemyCursorBackend", "SyncSQLAlchemyCursorBackend"]
