"""Tests for the paginate() dispatch function."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any, Generic, TypeVar

import pytest

from pypaginate import paginate
from pypaginate.domain.pages import OffsetPage
from pypaginate.domain.params import CursorParams, OffsetParams


PAGE_SIZE = 10

T = TypeVar("T")


class _AsyncOffsetBackend(Generic[T]):
    """Typed async backend satisfying PaginationBackend[T] protocol."""

    def __init__(
        self,
        count_result: int = 0,
        fetch_result: list[T] | None = None,
    ) -> None:
        self._count_result = count_result
        self._fetch_result: list[T] = fetch_result or []

    async def count(self, query: object) -> int:
        return self._count_result

    async def fetch(
        self,
        query: object,
        offset: int,
        limit: int,
    ) -> list[T]:
        return self._fetch_result


class _AsyncCursorBackend(Generic[T]):
    """Typed async backend satisfying CursorBackend[T] protocol."""

    def __init__(
        self,
        items: list[T] | None = None,
        next_cursor: str | None = None,
        prev_cursor: str | None = None,
    ) -> None:
        self._items: list[T] = items or []
        self._next_cursor = next_cursor
        self._prev_cursor = prev_cursor

    async def fetch_page(
        self,
        query: object,
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[T], str | None, str | None]:
        return self._items, self._next_cursor, self._prev_cursor


class TestPaginateAutoDetect:
    def test_list_auto_detects_memory_backend(self) -> None:
        data = list(range(50))

        page = paginate(data, OffsetParams(page=1, limit=PAGE_SIZE))

        assert len(page.items) == PAGE_SIZE
        assert page.total == 50

    def test_tuple_auto_detects_memory_backend(self) -> None:
        data = tuple(range(20))

        page = paginate(data, OffsetParams(page=1, limit=5))

        assert len(page.items) == 5
        assert page.total == 20


class TestPaginateSyncReturn:
    def test_returns_offset_page_type(self) -> None:
        result = paginate([1, 2, 3], OffsetParams())

        assert hasattr(result, "total") and hasattr(result, "page")


class TestPaginateErrors:
    def test_cursor_params_with_sync_backend_raises(self) -> None:
        class _SyncBackend:
            @staticmethod
            def count(_query: object) -> int:
                return 0

            @staticmethod
            def fetch(
                _query: object,
                _offset: int,
                _limit: int,
            ) -> list[object]:
                return []

        with pytest.raises(TypeError, match="async CursorBackend"):
            paginate(object(), CursorParams(), backend=_SyncBackend())

    def test_non_sequence_without_backend_raises(self) -> None:
        with pytest.raises(TypeError, match="Cannot auto-detect"):
            paginate(42, OffsetParams())

    def test_string_source_without_backend_raises(self) -> None:
        with pytest.raises(TypeError, match="Cannot auto-detect"):
            paginate("hello", OffsetParams())

    def test_backend_with_no_methods_raises(self) -> None:
        """Backend with no count/fetch/fetch_page hits _has_async_methods return False."""

        class _EmptyBackend:
            pass

        with pytest.raises(AttributeError):
            paginate(object(), OffsetParams(), backend=_EmptyBackend())


class TestPaginateEdgeCases:
    def test_empty_list_returns_empty_page(self) -> None:
        page = paginate([], OffsetParams())

        assert page.items == []
        assert page.total == 0

    def test_single_item_list(self) -> None:
        page = paginate([42], OffsetParams(page=1, limit=PAGE_SIZE))

        assert page.items == [42]
        assert page.total == 1
        assert page.has_next is False


class TestPaginateAsync:
    def test_paginate_returns_awaitable_for_async_backend(self) -> None:
        backend: _AsyncOffsetBackend[Any] = _AsyncOffsetBackend()

        result = paginate(object(), OffsetParams(), backend=backend)

        assert isinstance(result, Awaitable)

    def test_cursor_params_with_async_backend_returns_awaitable(
        self,
    ) -> None:
        backend: _AsyncCursorBackend[Any] = _AsyncCursorBackend()

        result = paginate(object(), CursorParams(), backend=backend)

        assert isinstance(result, Awaitable)

    def test_cursor_params_with_sync_list_raises(self) -> None:
        with pytest.raises(TypeError, match="Cannot auto-detect"):
            paginate(42, CursorParams())


class TestAsyncDetection:
    def test_detects_async_backend_via_paginate(self) -> None:
        backend: _AsyncOffsetBackend[Any] = _AsyncOffsetBackend()

        result = paginate(object(), OffsetParams(), backend=backend)

        assert isinstance(result, Awaitable)

    def test_sync_methods_produce_sync_result(self) -> None:
        result = paginate([1, 2, 3], OffsetParams())

        assert hasattr(result, "total") and hasattr(result, "page")

    def test_no_backend_with_non_sequence_raises(self) -> None:
        with pytest.raises(TypeError, match="Cannot auto-detect"):
            paginate(object(), OffsetParams())


class TestPaginateAsyncAwaited:
    @pytest.mark.asyncio()
    async def test_async_offset_returns_page(self) -> None:
        backend: _AsyncOffsetBackend[int] = _AsyncOffsetBackend(
            count_result=3,
            fetch_result=[1, 2, 3],
        )

        result = await paginate(
            object(),
            OffsetParams(page=1, limit=10),
            backend=backend,
        )

        assert hasattr(result, "total") and hasattr(result, "page")
        assert result.items == [1, 2, 3]

    @pytest.mark.asyncio()
    async def test_cursor_paginate_returns_cursor_page(self) -> None:
        from pypaginate.domain.pages import CursorPage

        backend: _AsyncCursorBackend[int] = _AsyncCursorBackend(
            items=[1, 2],
            next_cursor="nxt",
        )

        result = await paginate(
            object(),
            CursorParams(limit=2),
            backend=backend,
        )

        assert hasattr(result, "next_cursor")
        assert result.items == [1, 2]
