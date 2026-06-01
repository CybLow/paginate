"""Tests for the resident :class:`pypaginate.Dataset`.

The central contract is that the native one-call pipeline and the pure-Python
fallback produce an **identical** page. Each test runs the query both ways (the
pure path is forced by clearing ``_native``) and asserts they match, plus checks
concrete expected values so the two paths can't be wrong in the same way.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from pypaginate import Dataset, FilterSpec, OffsetParams, SearchSpec, SortSpec
from pypaginate.dataset import _HAS_NATIVE
from pypaginate.domain.enums import SortDirection


PEOPLE = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 17},
    {"id": 3, "name": "Cara", "age": 45},
    {"id": 4, "name": "Dan", "age": 30},
    {"id": 5, "name": "Eve", "age": 22},
]


def _fields(page: Any) -> tuple[Any, ...]:
    """A comparable tuple of a page's items + metadata."""
    return (
        list(page.items),
        page.total,
        page.page,
        page.pages,
        page.has_next,
        page.has_previous,
    )


def _both(items: list[Any], params: OffsetParams, **kw: Any) -> tuple[Any, Any]:
    """Run the same query via the (maybe-native) path and the forced-pure path."""
    native = Dataset(items).paginate(params, **kw)
    pure_ds: Dataset[Any] = Dataset(items)
    pure_ds._native = None
    pure = pure_ds.paginate(params, **kw)
    return native, pure


class TestNativePureParity:
    def test_no_query_is_plain_pagination(self) -> None:
        native, pure = _both(PEOPLE, OffsetParams(page=1, limit=2))
        assert _fields(native) == _fields(pure)
        assert _fields(native) == ([PEOPLE[0], PEOPLE[1]], 5, 1, 3, True, False)

    def test_filter_then_sort(self) -> None:
        native, pure = _both(
            PEOPLE,
            OffsetParams(page=1, limit=10),
            filters=[FilterSpec(field="age", operator="gte", value=30)],
            sorting=[SortSpec(field="age", direction=SortDirection.DESC)],
        )
        assert _fields(native) == _fields(pure)
        # ages >= 30: Cara(45), Alice(30), Dan(30); desc + stable keeps Alice<Dan.
        assert [p["name"] for p in native.items] == ["Cara", "Alice", "Dan"]
        assert native.total == 3

    def test_multiple_filters_are_anded(self) -> None:
        native, pure = _both(
            PEOPLE,
            OffsetParams(page=1, limit=10),
            filters=[
                FilterSpec(field="age", operator="gte", value=20),
                FilterSpec(field="age", operator="lt", value=45),
            ],
        )
        assert _fields(native) == _fields(pure)
        assert sorted(p["name"] for p in native.items) == ["Alice", "Dan", "Eve"]

    def test_second_page_metadata(self) -> None:
        native, pure = _both(
            PEOPLE,
            OffsetParams(page=2, limit=2),
            sorting=[SortSpec(field="id")],
        )
        assert _fields(native) == _fields(pure)
        assert [p["id"] for p in native.items] == [3, 4]
        assert (native.page, native.pages, native.has_next, native.has_previous) == (
            2,
            3,
            True,
            True,
        )

    def test_past_the_end_page_is_empty(self) -> None:
        native, pure = _both(PEOPLE, OffsetParams(page=99, limit=2))
        assert _fields(native) == _fields(pure)
        assert native.items == []
        assert native.total == 5
        assert native.has_next is False

    def test_string_sort_descending(self) -> None:
        native, pure = _both(
            PEOPLE,
            OffsetParams(page=1, limit=3),
            sorting=[SortSpec(field="name", direction=SortDirection.DESC)],
        )
        assert _fields(native) == _fields(pure)
        assert [p["name"] for p in native.items] == ["Eve", "Dan", "Cara"]

    def test_decimal_and_none_fields(self) -> None:
        items = [
            {"name": "a", "price": Decimal("9.99"), "tag": None},
            {"name": "b", "price": Decimal("19.99"), "tag": "x"},
            {"name": "c", "price": Decimal("4.99"), "tag": None},
        ]
        native, pure = _both(
            items,
            OffsetParams(page=1, limit=10),
            filters=[FilterSpec(field="price", operator="gt", value=Decimal("5.00"))],
            sorting=[SortSpec(field="price", direction=SortDirection.ASC)],
        )
        assert _fields(native) == _fields(pure)
        assert [i["name"] for i in native.items] == ["a", "b"]


class TestSearchFallback:
    def test_search_then_paginate(self) -> None:
        # Search has no native one-call path -> pure-Python; still returns a page.
        page = Dataset(PEOPLE).paginate(
            OffsetParams(page=1, limit=10),
            search=SearchSpec(query="a", fields=("name",)),
        )
        # contains "a" (normalized): Alice, Cara, Dan — order preserved.
        assert [p["name"] for p in page.items] == ["Alice", "Cara", "Dan"]
        assert page.total == 3


class TestMatchesBackendPipeline:
    def test_equals_manual_sort_then_paginate(self) -> None:
        from pypaginate import paginate
        from pypaginate.adapters.memory.sorting import MemorySortBackend

        params = OffsetParams(page=1, limit=2)
        sorting = [SortSpec(field="age")]
        expected = paginate(MemorySortBackend.apply_sorting(PEOPLE, sorting), params)
        got = Dataset(PEOPLE).paginate(params, sorting=sorting)
        assert _fields(got) == _fields(expected)


class TestLen:
    def test_len_reports_row_count(self) -> None:
        assert len(Dataset(PEOPLE)) == 5
        assert len(Dataset([])) == 0


@pytest.mark.skipif(not _HAS_NATIVE, reason="native paginate_core not installed")
class TestNativeActuallyUsed:
    def test_native_dataset_is_built(self) -> None:
        assert Dataset(PEOPLE)._native is not None
