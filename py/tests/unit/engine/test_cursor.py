"""Tests for AsyncCursorPaginator."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

import pytest

from pypaginate.domain.params import CursorParams
from pypaginate.engine.cursor import AsyncCursorPaginator


T = TypeVar("T")


class _FakeCursorBackend(Generic[T]):
    """Typed fake satisfying CursorBackend[T] protocol exactly."""

    def __init__(
        self,
        items: list[T],
        next_cursor: str | None = None,
        prev_cursor: str | None = None,
    ) -> None:
        self.items = items
        self.next_cursor = next_cursor
        self.prev_cursor = prev_cursor
        self.last_call: dict[str, Any] = {}

    async def fetch_page(
        self,
        _query: object,
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[T], str | None, str | None]:
        self.last_call = {"limit": limit, "after": after, "before": before}
        return self.items, self.next_cursor, self.prev_cursor


class TestCursorPaginatorReturnsPage:
    @pytest.mark.asyncio
    async def test_returns_cursor_page_with_items(self) -> None:
        backend: _FakeCursorBackend[int] = _FakeCursorBackend(
            [1, 2, 3],
            next_cursor="next_abc",
        )
        paginator = AsyncCursorPaginator(backend)

        page = await paginator.paginate(object(), CursorParams(limit=3))

        assert hasattr(page, "next_cursor")
        assert page.items == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_has_next_when_next_cursor_present(self) -> None:
        backend: _FakeCursorBackend[int] = _FakeCursorBackend(
            [1, 2],
            next_cursor="next_abc",
        )
        paginator = AsyncCursorPaginator(backend)

        page = await paginator.paginate(object(), CursorParams(limit=3))

        assert page.has_next is True
        assert page.next_cursor == "next_abc"

    @pytest.mark.asyncio
    async def test_has_previous_when_prev_cursor_present(self) -> None:
        backend: _FakeCursorBackend[int] = _FakeCursorBackend(
            [1, 2],
            prev_cursor="prev_xyz",
        )
        paginator = AsyncCursorPaginator(backend)

        page = await paginator.paginate(object(), CursorParams(limit=3))

        assert page.has_previous is True
        assert page.previous_cursor == "prev_xyz"


class TestCursorPaginatorNoNext:
    @pytest.mark.asyncio
    async def test_no_next_when_cursor_is_none(self) -> None:
        backend: _FakeCursorBackend[int] = _FakeCursorBackend([1])
        paginator = AsyncCursorPaginator(backend)

        page = await paginator.paginate(object(), CursorParams(limit=5))

        assert page.has_next is False
        assert page.next_cursor is None


class TestCursorPaginatorPassesParams:
    @pytest.mark.asyncio
    async def test_passes_after_to_backend(self) -> None:
        backend: _FakeCursorBackend[Any] = _FakeCursorBackend([])
        paginator = AsyncCursorPaginator(backend)

        await paginator.paginate(object(), CursorParams(limit=5, after="abc"))

        assert backend.last_call["limit"] == 5
        assert backend.last_call["after"] == "abc"
        assert backend.last_call["before"] is None

    @pytest.mark.asyncio
    async def test_passes_before_to_backend(self) -> None:
        backend: _FakeCursorBackend[Any] = _FakeCursorBackend([])
        paginator = AsyncCursorPaginator(backend)

        await paginator.paginate(object(), CursorParams(limit=10, before="xyz"))

        assert backend.last_call["limit"] == 10
        assert backend.last_call["after"] is None
        assert backend.last_call["before"] == "xyz"


class TestCursorPaginatorEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_result(self) -> None:
        backend: _FakeCursorBackend[Any] = _FakeCursorBackend([])
        paginator = AsyncCursorPaginator(backend)

        page = await paginator.paginate(object(), CursorParams(limit=10))

        assert page.items == []
        assert page.has_next is False
        assert page.has_previous is False

    @pytest.mark.asyncio
    async def test_first_page_no_cursors(self) -> None:
        backend: _FakeCursorBackend[int] = _FakeCursorBackend(
            [1, 2, 3],
            next_cursor="next_abc",
        )
        paginator = AsyncCursorPaginator(backend)

        page = await paginator.paginate(object(), CursorParams(limit=3))

        assert page.items == [1, 2, 3]
        assert page.has_next is True
        assert page.has_previous is False
        assert page.next_cursor == "next_abc"
