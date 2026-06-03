"""Tests for Paginator and AsyncPaginator."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

import pytest

from pypaginate.domain.enums import OverflowStrategy
from pypaginate.domain.params import OffsetParams
from pypaginate.engine.paginator import AsyncPaginator, Paginator


TOTAL_ITEMS = 50
PAGE_SIZE = 10

T = TypeVar("T")


class _FakeSyncBackend(Generic[T]):
    """Minimal sync backend satisfying SyncPaginationBackend[T]."""

    def __init__(self, data: list[T]) -> None:
        self._data = data

    def count(self, query: object) -> int:
        return len(self._data)

    def fetch(self, query: object, offset: int, limit: int) -> list[T]:
        return self._data[offset : offset + limit]


class _FakeAsyncBackend(Generic[T]):
    """Minimal async backend satisfying PaginationBackend[T]."""

    def __init__(self, data: list[T]) -> None:
        self._data = data

    async def count(self, query: object) -> int:
        return len(self._data)

    async def fetch(
        self,
        query: object,
        offset: int,
        limit: int,
    ) -> list[T]:
        return self._data[offset : offset + limit]


class _MockSyncBackend(Generic[T]):
    """Configurable sync backend satisfying SyncPaginationBackend[T]."""

    def __init__(
        self,
        count_result: int = 0,
        fetch_result: list[T] | None = None,
    ) -> None:
        self.count_result = count_result
        self.fetch_result: list[T] = fetch_result or []
        self.count_calls: list[object] = []
        self.fetch_calls: list[tuple[object, int, int]] = []

    def count(self, query: object) -> int:
        self.count_calls.append(query)
        return self.count_result

    def fetch(self, query: object, offset: int, limit: int) -> list[T]:
        self.fetch_calls.append((query, offset, limit))
        return self.fetch_result


class _MockAsyncBackend(Generic[T]):
    """Configurable async backend satisfying PaginationBackend[T]."""

    def __init__(
        self,
        count_result: int = 0,
        fetch_result: list[T] | None = None,
    ) -> None:
        self.count_result = count_result
        self.fetch_result: list[T] = fetch_result or []
        self.count_calls: list[object] = []
        self.fetch_calls: list[tuple[object, int, int]] = []

    async def count(self, query: object) -> int:
        self.count_calls.append(query)
        return self.count_result

    async def fetch(self, query: object, offset: int, limit: int) -> list[T]:
        self.fetch_calls.append((query, offset, limit))
        return self.fetch_result


class TestPaginator:
    def test_basic_pagination_returns_correct_slice(self) -> None:
        backend: _FakeSyncBackend[int] = _FakeSyncBackend(list(range(TOTAL_ITEMS)))
        paginator = Paginator(backend)

        page = paginator.paginate(None, OffsetParams(page=1, limit=PAGE_SIZE))

        assert len(page.items) == PAGE_SIZE
        assert page.total == TOTAL_ITEMS
        assert page.page == 1

    def test_empty_data_returns_empty_page(self) -> None:
        backend: _FakeSyncBackend[Any] = _FakeSyncBackend([])
        paginator = Paginator(backend)

        page = paginator.paginate(None, OffsetParams())

        assert page.total == 0
        assert page.items == []

    def test_overflow_empty_returns_empty_items(self) -> None:
        backend: _FakeSyncBackend[int] = _FakeSyncBackend(list(range(PAGE_SIZE)))
        paginator = Paginator(backend, overflow=OverflowStrategy.EMPTY)

        page = paginator.paginate(None, OffsetParams(page=5, limit=PAGE_SIZE))

        assert page.items == []
        assert page.total == PAGE_SIZE

    def test_overflow_clamp_returns_last_page(self) -> None:
        backend: _FakeSyncBackend[int] = _FakeSyncBackend(list(range(PAGE_SIZE)))
        paginator = Paginator(backend, overflow=OverflowStrategy.CLAMP)

        page = paginator.paginate(None, OffsetParams(page=5, limit=PAGE_SIZE))

        assert page.page == 1
        assert len(page.items) == PAGE_SIZE

    def test_single_item_pagination(self) -> None:
        backend: _FakeSyncBackend[int] = _FakeSyncBackend([42])
        paginator = Paginator(backend)

        page = paginator.paginate(None, OffsetParams(page=1, limit=PAGE_SIZE))

        assert page.total == 1
        assert page.items == [42]
        assert page.has_next is False


class TestPaginatorMocks:
    def test_count_called_once(self) -> None:
        """Paginator calls backend.count exactly once."""
        backend: _MockSyncBackend[int] = _MockSyncBackend(
            count_result=100,
            fetch_result=list(range(20)),
        )

        Paginator(backend).paginate("q", OffsetParams(page=1, limit=20))

        assert len(backend.count_calls) == 1

    def test_skips_fetch_when_empty(self) -> None:
        """Paginator skips fetch when count is 0."""
        backend: _MockSyncBackend[Any] = _MockSyncBackend(count_result=0)

        result = Paginator(backend).paginate("q", OffsetParams())

        assert len(backend.fetch_calls) == 0
        assert result.items == []

    def test_passes_correct_offset(self) -> None:
        """Paginator passes correct offset to backend.fetch."""
        backend: _MockSyncBackend[Any] = _MockSyncBackend(
            count_result=100,
            fetch_result=[],
        )

        Paginator(backend).paginate("q", OffsetParams(page=3, limit=10))

        assert backend.fetch_calls == [("q", 20, 10)]

    def test_skips_fetch_when_offset_exceeds_total(self) -> None:
        """Paginator skips fetch when offset >= total."""
        backend: _MockSyncBackend[Any] = _MockSyncBackend(count_result=10)

        result = Paginator(backend).paginate("q", OffsetParams(page=5, limit=10))

        assert len(backend.fetch_calls) == 0
        assert result.items == []

    def test_clamp_adjusts_page_before_fetch(self) -> None:
        """Clamp strategy adjusts page before calling fetch."""
        backend: _MockSyncBackend[int] = _MockSyncBackend(
            count_result=30,
            fetch_result=list(range(10)),
        )

        paginator = Paginator(backend, overflow=OverflowStrategy.CLAMP)
        result = paginator.paginate("q", OffsetParams(page=99, limit=10))

        assert backend.fetch_calls == [("q", 20, 10)]
        assert result.page == 3

    def test_returns_correct_total(self) -> None:
        """Paginator passes backend count as total."""
        backend: _MockSyncBackend[int] = _MockSyncBackend(
            count_result=42,
            fetch_result=[1, 2, 3],
        )

        result = Paginator(backend).paginate("q", OffsetParams(page=1, limit=10))

        assert result.total == 42


class TestAsyncPaginator:
    @pytest.mark.asyncio
    async def test_basic_pagination_returns_correct_slice(self) -> None:
        backend: _FakeAsyncBackend[int] = _FakeAsyncBackend(list(range(30)))
        paginator = AsyncPaginator(backend)

        page = await paginator.paginate(
            None,
            OffsetParams(page=1, limit=PAGE_SIZE),
        )

        assert len(page.items) == PAGE_SIZE
        assert page.total == 30

    @pytest.mark.asyncio
    async def test_empty_data_returns_empty_page(self) -> None:
        backend: _FakeAsyncBackend[Any] = _FakeAsyncBackend([])
        paginator = AsyncPaginator(backend)

        page = await paginator.paginate(None, OffsetParams())

        assert page.total == 0
        assert page.items == []

    @pytest.mark.asyncio
    async def test_overflow_clamp_returns_correct_page(self) -> None:
        backend: _FakeAsyncBackend[int] = _FakeAsyncBackend(list(range(15)))
        paginator = AsyncPaginator(backend, overflow=OverflowStrategy.CLAMP)

        page = await paginator.paginate(
            None,
            OffsetParams(page=10, limit=5),
        )

        assert page.page == 3
        assert len(page.items) == 5


class TestAsyncPaginatorMocks:
    @pytest.mark.asyncio
    async def test_count_awaited_once(self) -> None:
        """AsyncPaginator awaits backend.count exactly once."""
        backend: _MockAsyncBackend[int] = _MockAsyncBackend(
            count_result=50,
            fetch_result=list(range(10)),
        )

        await AsyncPaginator(backend).paginate(
            "q",
            OffsetParams(page=1, limit=10),
        )

        assert len(backend.count_calls) == 1

    @pytest.mark.asyncio
    async def test_fetch_awaited_once(self) -> None:
        """AsyncPaginator awaits backend.fetch exactly once."""
        backend: _MockAsyncBackend[int] = _MockAsyncBackend(
            count_result=50,
            fetch_result=list(range(10)),
        )

        await AsyncPaginator(backend).paginate(
            "q",
            OffsetParams(page=1, limit=10),
        )

        assert len(backend.fetch_calls) == 1

    @pytest.mark.asyncio
    async def test_skips_fetch_when_empty(self) -> None:
        """AsyncPaginator skips fetch when count is 0."""
        backend: _MockAsyncBackend[Any] = _MockAsyncBackend(count_result=0)

        result = await AsyncPaginator(backend).paginate("q", OffsetParams())

        assert len(backend.fetch_calls) == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_passes_correct_offset(self) -> None:
        """AsyncPaginator passes correct offset to fetch."""
        backend: _MockAsyncBackend[Any] = _MockAsyncBackend(
            count_result=100,
            fetch_result=[],
        )

        await AsyncPaginator(backend).paginate(
            "q",
            OffsetParams(page=4, limit=5),
        )

        assert backend.fetch_calls == [("q", 15, 5)]
