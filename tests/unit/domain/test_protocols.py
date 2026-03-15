"""Tests for runtime-checkable backend protocols."""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from pypaginate.domain.protocols import (
    CursorBackend,
    FilterBackend,
    PaginationBackend,
    SearchBackend,
    SortBackend,
    SyncPaginationBackend,
)
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec


_ALL_PROTOCOLS = [
    PaginationBackend,
    SyncPaginationBackend,
    CursorBackend,
    FilterBackend,
    SortBackend,
    SearchBackend,
]


class TestProtocolsAreRuntimeCheckable:
    @pytest.mark.parametrize("proto", _ALL_PROTOCOLS)
    def test_is_runtime_checkable(self, proto: type) -> None:
        assert hasattr(proto, "__protocol_attrs__") or hasattr(
            proto,
            "__abstractmethods__",
        )


class TestSyncPaginationBackendRecognized:
    def test_conforming_class_recognized(self) -> None:
        class _Good:
            @staticmethod
            def count(_query: object) -> int:
                return 0

            @staticmethod
            def fetch(_query: object, _offset: int, _limit: int) -> list[object]:
                return []

        assert isinstance(_Good(), SyncPaginationBackend)

    def test_missing_method_not_recognized(self) -> None:
        class _Bad:
            @staticmethod
            def count(_query: object) -> int:
                return 0

        assert not isinstance(_Bad(), SyncPaginationBackend)


class TestPaginationBackendRecognized:
    def test_conforming_async_class_recognized(self) -> None:
        class _Good:
            @staticmethod
            async def count(_query: object) -> int:
                return 0

            @staticmethod
            async def fetch(_query: object, _offset: int, _limit: int) -> list[object]:
                return []

        assert isinstance(_Good(), PaginationBackend)


class TestCursorBackendRecognized:
    def test_conforming_class_recognized(self) -> None:
        class _Good:
            @staticmethod
            async def fetch_page(
                _query: object,
                *,
                _limit: int,
                _after: str | None = None,
                _before: str | None = None,
            ) -> tuple[list[object], str | None, str | None]:
                return [], None, None

        assert isinstance(_Good(), CursorBackend)


class TestFilterBackendRecognized:
    def test_conforming_class_recognized(self) -> None:
        class _Good:
            @staticmethod
            def apply_filters(
                query: object,
                _filters: Sequence[FilterSpec],
            ) -> object:
                return query

        assert isinstance(_Good(), FilterBackend)


class TestSortBackendRecognized:
    def test_conforming_class_recognized(self) -> None:
        class _Good:
            @staticmethod
            def apply_sorting(
                query: object,
                _sorting: Sequence[SortSpec],
            ) -> object:
                return query

        assert isinstance(_Good(), SortBackend)


class TestSearchBackendRecognized:
    def test_conforming_class_recognized(self) -> None:
        class _Good:
            @staticmethod
            def apply_search(query: object, _spec: SearchSpec) -> object:
                return query

        assert isinstance(_Good(), SearchBackend)
