"""Tests for SortEngine."""

from __future__ import annotations

import pytest

from pypaginate.domain.enums import NullsPosition, SortDirection
from pypaginate.domain.exceptions import SortError
from pypaginate.domain.specs import SortSpec
from tests.support.engines import SortEngine


class TestSortAsc:
    def test_sort_by_name_asc(
        self,
        sort_engine: SortEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        specs = [SortSpec(field="name")]

        result = sort_engine.apply(sample_users, specs)

        names = [item["name"] for item in result]
        assert names == ["Alice", "Bob", "Charlie", "Diana"]

    def test_sort_by_age_asc(
        self,
        sort_engine: SortEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        specs = [SortSpec(field="age")]

        result = sort_engine.apply(sample_users, specs)

        ages = [item["age"] for item in result]
        assert ages == [25, 28, 30, 35]


class TestSortDesc:
    def test_sort_by_age_desc(
        self,
        sort_engine: SortEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        specs = [SortSpec(field="age", direction=SortDirection.DESC)]

        result = sort_engine.apply(sample_users, specs)

        ages = [item["age"] for item in result]
        assert ages == [35, 30, 28, 25]


class TestSortNulls:
    def test_nulls_placed_last(self, sort_engine: SortEngine) -> None:
        items = [
            {"name": "Alice", "score": None},
            {"name": "Bob", "score": 90},
            {"name": "Charlie", "score": 80},
        ]
        specs = [SortSpec(field="score", nulls=NullsPosition.LAST)]

        result = sort_engine.apply(items, specs)

        assert result[-1]["score"] is None

    def test_nulls_placed_first(self, sort_engine: SortEngine) -> None:
        items = [
            {"name": "Alice", "score": 95},
            {"name": "Bob", "score": None},
            {"name": "Charlie", "score": 80},
        ]
        specs = [SortSpec(field="score", nulls=NullsPosition.FIRST)]

        result = sort_engine.apply(items, specs)

        assert result[0]["score"] is None

    def test_all_none_values_sorted(self, sort_engine: SortEngine) -> None:
        items = [
            {"name": "Alice", "score": None},
            {"name": "Bob", "score": None},
        ]
        specs = [SortSpec(field="score", nulls=NullsPosition.LAST)]

        result = sort_engine.apply(items, specs)

        assert len(result) == 2
        assert all(r["score"] is None for r in result)


class TestMultiFieldSort:
    def test_two_field_sort_applies_priority(
        self,
        sort_engine: SortEngine,
    ) -> None:
        items = [
            {"dept": "B", "name": "Zara"},
            {"dept": "A", "name": "Bob"},
            {"dept": "A", "name": "Alice"},
            {"dept": "B", "name": "Adam"},
        ]
        specs = [SortSpec(field="dept"), SortSpec(field="name")]

        result = sort_engine.apply(items, specs)

        assert result[0] == {"dept": "A", "name": "Alice"}
        assert result[1] == {"dept": "A", "name": "Bob"}


class TestSortEdgeCases:
    def test_empty_specs_returns_original_order(
        self,
        sort_engine: SortEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        result = sort_engine.apply(sample_users, [])

        assert result == list(sample_users)

    def test_single_item_returns_single_item(
        self,
        sort_engine: SortEngine,
    ) -> None:
        items = [{"name": "Solo"}]
        specs = [SortSpec(field="name")]

        result = sort_engine.apply(items, specs)

        assert result == [{"name": "Solo"}]

    def test_empty_items_returns_empty_list(
        self,
        sort_engine: SortEngine,
    ) -> None:
        specs = [SortSpec(field="name")]

        result = sort_engine.apply([], specs)

        assert result == []

    def test_identical_values_preserves_order(
        self,
        sort_engine: SortEngine,
    ) -> None:
        items = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 30},
        ]
        specs = [SortSpec(field="age")]

        result = sort_engine.apply(items, specs)

        names = [item["name"] for item in result]
        assert names == ["Alice", "Bob", "Charlie"]

    def test_empty_dataset_with_multiple_specs(
        self,
        sort_engine: SortEngine,
    ) -> None:
        specs = [SortSpec(field="name"), SortSpec(field="age")]

        result = sort_engine.apply([], specs)

        assert result == []


class TestSortError:
    def test_incomparable_values_raise_sort_error(
        self,
        sort_engine: SortEngine,
    ) -> None:
        items = [{"v": 1}, {"v": "x"}]
        specs = [SortSpec(field="v")]

        with pytest.raises(SortError, match="comparable"):
            sort_engine.apply(items, specs)
