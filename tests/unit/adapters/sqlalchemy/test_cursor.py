"""Tests for SQLAlchemyCursorBackend.

Uses mocks only. sqlakeyset requires specific ORDER BY handling
and bookmark serialization that does not work reliably with
async SQLite (no native cursor/keyset support in SQLite).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pypaginate.adapters.sqlalchemy.cursor import SQLAlchemyCursorBackend


@pytest.fixture()
def cursor_backend() -> SQLAlchemyCursorBackend:
    """Backend with a mocked async session."""
    return SQLAlchemyCursorBackend(session=AsyncMock())


# -- Mock tests: fetch_page -------------------------------------------------


class TestFetchPage:
    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.cursor._select_keyset_page")
    async def test_returns_items_and_cursors(
        self,
        mock_select: AsyncMock,
        cursor_backend: SQLAlchemyCursorBackend,
    ) -> None:
        page = _make_page(["a", "b"], has_next=True, has_prev=False)
        mock_select.return_value = page
        query = MagicMock()

        items, nxt, prev = await cursor_backend.fetch_page(query, limit=2)

        assert items == ["a", "b"]
        assert nxt == "next_cursor"
        assert prev is None

    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.cursor._select_keyset_page")
    async def test_no_next_returns_none_cursor(
        self,
        mock_select: AsyncMock,
        cursor_backend: SQLAlchemyCursorBackend,
    ) -> None:
        page = _make_page(["x"], has_next=False, has_prev=False)
        mock_select.return_value = page

        _, nxt, prev = await cursor_backend.fetch_page(MagicMock(), limit=10)

        assert nxt is None
        assert prev is None

    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.cursor._select_keyset_page")
    async def test_passes_after_and_before(
        self,
        mock_select: AsyncMock,
        cursor_backend: SQLAlchemyCursorBackend,
    ) -> None:
        mock_select.return_value = _make_page([], has_next=False, has_prev=True)

        await cursor_backend.fetch_page(
            MagicMock(),
            limit=5,
            after="abc",
            before="xyz",
        )

        call_kwargs = mock_select.call_args
        assert call_kwargs[0][2] == 5
        assert call_kwargs[0][3] == "abc"
        assert call_kwargs[0][4] == "xyz"


# -- Tests: extract_results via fetch_page -----------------------------------


class TestExtractResults:
    @pytest.mark.asyncio()
    @patch("pypaginate.adapters.sqlalchemy.cursor._select_keyset_page")
    async def test_extracts_plain_rows(
        self,
        mock_select: AsyncMock,
        cursor_backend: SQLAlchemyCursorBackend,
    ) -> None:
        page = _make_page(["a", "b"], has_next=True, has_prev=True)
        mock_select.return_value = page

        items, nxt, prev = await cursor_backend.fetch_page(MagicMock(), limit=2)

        assert items == ["a", "b"]
        assert nxt == "next_cursor"
        assert prev == "prev_cursor"


# -- Helpers -----------------------------------------------------------------


def _make_page(
    rows: list[object],
    *,
    has_next: bool,
    has_prev: bool,
) -> MagicMock:
    """Build a mock sqlakeyset Page."""
    page = MagicMock()
    page.__iter__ = MagicMock(return_value=iter(rows))
    page.paging.has_next = has_next
    page.paging.has_previous = has_prev
    page.paging.bookmark_next = "next_cursor" if has_next else None
    page.paging.bookmark_previous = "prev_cursor" if has_prev else None
    return page
