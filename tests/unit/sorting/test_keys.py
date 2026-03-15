"""Tests for sort key building utilities."""

from __future__ import annotations

import pytest

from pypaginate.domain.enums import NullsPosition, SortDirection
from pypaginate.sorting.keys import build_sort_key


class TestAscKey:
    def test_asc_orders_numbers_correctly(self) -> None:
        items = [{"v": 3}, {"v": 1}, {"v": 2}]
        key = build_sort_key("v", SortDirection.ASC, NullsPosition.LAST)

        result = sorted(items, key=key)

        assert [r["v"] for r in result] == [1, 2, 3]

    def test_asc_orders_strings_correctly(self) -> None:
        items = [{"v": "c"}, {"v": "a"}, {"v": "b"}]
        key = build_sort_key("v", SortDirection.ASC, NullsPosition.LAST)

        result = sorted(items, key=key)

        assert [r["v"] for r in result] == ["a", "b", "c"]


class TestDescKey:
    def test_desc_orders_reversed(self) -> None:
        items = [{"v": 1}, {"v": 3}, {"v": 2}]
        key = build_sort_key("v", SortDirection.DESC, NullsPosition.LAST)

        result = sorted(items, key=key, reverse=True)

        assert [r["v"] for r in result] == [3, 2, 1]


class TestNullsFirst:
    def test_nulls_first_places_none_before_values(self) -> None:
        items: list[dict[str, object]] = [{"v": 2}, {"v": None}, {"v": 1}]
        key = build_sort_key("v", SortDirection.ASC, NullsPosition.FIRST)

        result = sorted(items, key=key)

        assert result[0]["v"] is None


class TestNullsLast:
    def test_nulls_last_places_none_after_values(self) -> None:
        items: list[dict[str, object]] = [{"v": None}, {"v": 1}, {"v": 2}]
        key = build_sort_key("v", SortDirection.ASC, NullsPosition.LAST)

        result = sorted(items, key=key)

        assert result[-1]["v"] is None


class TestSortKeyMixed:
    @pytest.mark.parametrize(
        ("direction", "nulls", "expected_first"),
        [
            (SortDirection.ASC, NullsPosition.FIRST, None),
            (SortDirection.ASC, NullsPosition.LAST, 1),
        ],
        ids=["asc-nulls-first", "asc-nulls-last"],
    )
    def test_null_position_parametrized(
        self,
        direction: SortDirection,
        nulls: NullsPosition,
        expected_first: int | None,
    ) -> None:
        items: list[dict[str, object]] = [{"v": 2}, {"v": None}, {"v": 1}]
        key = build_sort_key("v", direction, nulls)

        result = sorted(items, key=key)

        assert result[0]["v"] is expected_first


class TestSafeGetFallback:
    def test_missing_field_treated_as_none(self) -> None:
        items = [{"v": 2}, {"other": 1}]
        key = build_sort_key("v", SortDirection.ASC, NullsPosition.LAST)

        result = sorted(items, key=key)

        assert result[0]["v"] == 2
        assert "v" not in result[1]
