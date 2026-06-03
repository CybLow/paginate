"""Tests for SyncPipeline and AsyncPipeline."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

import pytest

from pypaginate.domain.pages import OffsetPage
from pypaginate.domain.params import OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec
from pypaginate.engine.pipeline import AsyncPipeline, SyncPipeline


_FILTERS = [FilterSpec(field="x")]
_SORTING = [SortSpec(field="y")]
_SEARCH = SearchSpec(query="z", fields=("a",))

T = TypeVar("T")


def _make_offset_page() -> OffsetPage[Any]:
    return OffsetPage.create(["a"], total=1, params=OffsetParams())


class _FakeFilterBackend:
    """Typed fake satisfying FilterBackend protocol."""

    def __init__(self, result: object = None) -> None:
        self._result = result
        self.called = False
        self.last_query: object = None
        self.last_filters: Sequence[FilterSpec] = ()

    def apply_filters(
        self,
        query: object,
        filters: Sequence[FilterSpec],
    ) -> object:
        self.called = True
        self.last_query = query
        self.last_filters = filters
        return self._result if self._result is not None else query


class _FakeSortBackend:
    """Typed fake satisfying SortBackend protocol."""

    def __init__(self, result: object = None) -> None:
        self._result = result
        self.called = False
        self.last_query: object = None
        self.last_sorting: Sequence[SortSpec] = ()

    def apply_sorting(
        self,
        query: object,
        sorting: Sequence[SortSpec],
    ) -> object:
        self.called = True
        self.last_query = query
        self.last_sorting = sorting
        return self._result if self._result is not None else query


class _FakeSearchBackend:
    """Typed fake satisfying SearchBackend protocol."""

    def __init__(self, result: object = None) -> None:
        self._result = result
        self.called = False
        self.last_query: object = None
        self.last_spec: SearchSpec | None = None

    def apply_search(self, query: object, spec: SearchSpec) -> object:
        self.called = True
        self.last_query = query
        self.last_spec = spec
        return self._result if self._result is not None else query


class _FakeSyncPaginator(Generic[T]):
    """Typed fake satisfying Paginator[T] interface for sync tests."""

    def __init__(self, page: OffsetPage[T]) -> None:
        self._page = page
        self.last_query: object = None
        self.last_params: OffsetParams | None = None

    def paginate(
        self,
        query: object,
        params: OffsetParams,
    ) -> OffsetPage[T]:
        self.last_query = query
        self.last_params = params
        return self._page


class _FakeAsyncPaginator(Generic[T]):
    """Typed fake satisfying AsyncPaginator[T] interface for async tests."""

    def __init__(self, page: OffsetPage[T]) -> None:
        self._page = page
        self.last_query: object = None
        self.last_params: OffsetParams | None = None

    async def paginate(
        self,
        query: object,
        params: OffsetParams,
    ) -> OffsetPage[T]:
        self.last_query = query
        self.last_params = params
        return self._page


class TestSyncPipelineNoSpecs:
    def test_paginates_without_backends(self) -> None:
        pag: _FakeSyncPaginator[Any] = _FakeSyncPaginator(_make_offset_page())

        result = SyncPipeline(pag).execute("query", OffsetParams())

        assert hasattr(result, "total") and hasattr(result, "page")
        assert pag.last_query == "query"


class TestSyncPipelineWithFilter:
    def test_applies_filters_before_paginate(self) -> None:
        pag: _FakeSyncPaginator[Any] = _FakeSyncPaginator(_make_offset_page())
        filter_be = _FakeFilterBackend(result="filtered_query")
        filters = [FilterSpec(field="age", operator="gte", value=18)]

        pipeline = SyncPipeline(
            pag,
            filter_backend=filter_be,
        )
        pipeline.execute("query", OffsetParams(), filters=filters)

        assert filter_be.called
        assert filter_be.last_query == "query"
        assert list(filter_be.last_filters) == filters


class TestSyncPipelineWithSort:
    def test_applies_sorting_before_paginate(self) -> None:
        pag: _FakeSyncPaginator[Any] = _FakeSyncPaginator(_make_offset_page())
        sort_be = _FakeSortBackend(result="sorted_query")
        sorting = [SortSpec(field="name")]

        pipeline = SyncPipeline(
            pag,
            sort_backend=sort_be,
        )
        pipeline.execute("query", OffsetParams(), sorting=sorting)

        assert sort_be.called
        assert sort_be.last_query == "query"
        assert list(sort_be.last_sorting) == sorting


class TestSyncPipelineWithSearch:
    def test_applies_search_before_paginate(self) -> None:
        pag: _FakeSyncPaginator[Any] = _FakeSyncPaginator(_make_offset_page())
        search_be = _FakeSearchBackend(result="searched_query")
        search = SearchSpec(query="hello", fields=("name",))

        pipeline = SyncPipeline(
            pag,
            search_backend=search_be,
        )
        pipeline.execute("query", OffsetParams(), search=search)

        assert search_be.called
        assert search_be.last_query == "query"
        assert search_be.last_spec == search


class TestSyncPipelineAllBackends:
    def test_applies_filter_sort_search_order(self) -> None:
        pag: _FakeSyncPaginator[Any] = _FakeSyncPaginator(_make_offset_page())
        f = _FakeFilterBackend(result="filtered")
        s = _FakeSortBackend(result="sorted")
        se = _FakeSearchBackend(result="searched")

        pipeline = SyncPipeline(
            pag,
            filter_backend=f,
            sort_backend=s,
            search_backend=se,
        )
        pipeline.execute(
            "query",
            OffsetParams(),
            filters=_FILTERS,
            sorting=_SORTING,
            search=_SEARCH,
        )

        assert f.last_query == "query"
        assert list(f.last_filters) == _FILTERS
        assert s.last_query == "filtered"
        assert list(s.last_sorting) == _SORTING
        assert se.last_query == "sorted"
        assert se.last_spec == _SEARCH


class TestSyncPipelineSkipsNone:
    def test_no_filter_when_backend_is_none(self) -> None:
        pag: _FakeSyncPaginator[Any] = _FakeSyncPaginator(_make_offset_page())
        filters = [FilterSpec(field="x")]

        SyncPipeline(pag).execute(
            "query",
            OffsetParams(),
            filters=filters,
        )

        assert pag.last_query == "query"


class TestAsyncPipelineNoSpecs:
    @pytest.mark.asyncio
    async def test_paginates_without_backends(self) -> None:
        pag: _FakeAsyncPaginator[Any] = _FakeAsyncPaginator(
            _make_offset_page(),
        )

        result = await AsyncPipeline(pag).execute("query", OffsetParams())

        assert hasattr(result, "total") and hasattr(result, "page")
        assert pag.last_query == "query"


class TestAsyncPipelineWithFilter:
    @pytest.mark.asyncio
    async def test_applies_filters_before_paginate(self) -> None:
        pag: _FakeAsyncPaginator[Any] = _FakeAsyncPaginator(
            _make_offset_page(),
        )
        filter_be = _FakeFilterBackend(result="filtered_query")
        filters = [FilterSpec(field="age", operator="gte", value=18)]

        pipeline = AsyncPipeline(
            pag,
            filter_backend=filter_be,
        )
        await pipeline.execute("query", OffsetParams(), filters=filters)

        assert filter_be.called
        assert filter_be.last_query == "query"
        assert list(filter_be.last_filters) == filters


class TestAsyncPipelineAllBackends:
    @pytest.mark.asyncio
    async def test_applies_filter_sort_search_order(self) -> None:
        pag: _FakeAsyncPaginator[Any] = _FakeAsyncPaginator(
            _make_offset_page(),
        )
        f = _FakeFilterBackend(result="filtered")
        s = _FakeSortBackend(result="sorted")
        se = _FakeSearchBackend(result="searched")

        pipeline = AsyncPipeline(
            pag,
            filter_backend=f,
            sort_backend=s,
            search_backend=se,
        )
        await pipeline.execute(
            "query",
            OffsetParams(),
            filters=_FILTERS,
            sorting=_SORTING,
            search=_SEARCH,
        )

        assert f.last_query == "query"
        assert list(f.last_filters) == _FILTERS
        assert s.last_query == "filtered"
        assert list(s.last_sorting) == _SORTING
        assert se.last_query == "sorted"
        assert se.last_spec == _SEARCH
