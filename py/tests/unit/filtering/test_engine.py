"""Tests for FilterEngine."""

from __future__ import annotations

import pytest

from pypaginate.domain.enums import FilterLogic
from pypaginate.domain.exceptions import FilterError
from pypaginate.domain.specs import FilterSpec
from pypaginate.filtering.engine import FilterEngine


class TestFilterEngineSingle:
    def test_eq_filter_returns_matching_item(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [FilterSpec(field="name", operator="eq", value="Alice")]

        result = filter_engine.apply(sample_users, filters)

        assert len(result) == 1
        assert result[0]["name"] == "Alice"

    def test_gte_filter_returns_items_above_threshold(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [FilterSpec(field="age", operator="gte", value=30)]

        result = filter_engine.apply(sample_users, filters)

        assert len(result) == 2, "Expected Alice(30) and Charlie(35)"


class TestFilterEngineAnd:
    def test_and_filters_return_intersection(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [
            FilterSpec(field="age", operator="gte", value=25),
            FilterSpec(field="age", operator="lt", value=35),
        ]

        result = filter_engine.apply(sample_users, filters)

        names = {item["name"] for item in result}
        assert names == {"Alice", "Bob", "Diana"}


class TestFilterEngineOr:
    def test_or_filters_return_union(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [
            FilterSpec(field="name", value="Alice", logic=FilterLogic.OR),
            FilterSpec(field="name", value="Bob", logic=FilterLogic.OR),
        ]

        result = filter_engine.apply(sample_users, filters)

        assert len(result) == 2

    def test_or_with_value_filter(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [
            FilterSpec(field="age", operator="eq", value=25, logic=FilterLogic.OR),
            FilterSpec(field="age", operator="eq", value=35, logic=FilterLogic.OR),
        ]

        result = filter_engine.apply(sample_users, filters)

        names = {item["name"] for item in result}
        assert names == {"Bob", "Charlie"}


class TestFilterEngineMixed:
    def test_mixed_and_or_applies_both(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [
            FilterSpec(field="age", operator="gte", value=25),
            FilterSpec(field="name", value="Bob", logic=FilterLogic.OR),
            FilterSpec(field="name", value="Diana", logic=FilterLogic.OR),
        ]

        result = filter_engine.apply(sample_users, filters)

        names = {item["name"] for item in result}
        assert names == {"Bob", "Diana"}


class TestFilterEngineEdgeCases:
    def test_empty_filters_returns_all_items(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        result = filter_engine.apply(sample_users, [])

        assert len(result) == len(sample_users)

    def test_empty_items_returns_empty_list(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        filters = [FilterSpec(field="name", value="Alice")]

        result = filter_engine.apply([], filters)

        assert result == []

    def test_no_match_returns_empty_list(
        self,
        filter_engine: FilterEngine,
        sample_users: list[dict[str, object]],
    ) -> None:
        filters = [FilterSpec(field="name", value="Nonexistent")]

        result = filter_engine.apply(sample_users, filters)

        assert result == []

    def test_single_item_match(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        items = [{"name": "Solo"}]
        filters = [FilterSpec(field="name", value="Solo")]

        result = filter_engine.apply(items, filters)

        assert len(result) == 1

    def test_single_item_no_match(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        items = [{"name": "Solo"}]
        filters = [FilterSpec(field="name", value="Other")]

        result = filter_engine.apply(items, filters)

        assert result == []


class TestFilterEngineRegex:
    """Regex operator through FilterEngine."""

    def test_regex_happy_path(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        items = [{"code": "abc123"}, {"code": "xyz"}, {"code": "99"}]
        spec = FilterSpec(field="code", operator="regex", value=r"\d+")

        result = filter_engine.apply(items, [spec])

        assert len(result) == 2
        assert result[0]["code"] == "abc123"
        assert result[1]["code"] == "99"

    def test_regex_invalid_pattern_raises_filter_error(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        items = [{"code": "abc"}]
        spec = FilterSpec(field="code", operator="regex", value="[invalid")

        with pytest.raises(FilterError, match="Invalid regex"):
            filter_engine.apply(items, [spec])

    def test_regex_too_long_raises_filter_error(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        items = [{"code": "abc"}]
        long_pattern = "a" * 201
        spec = FilterSpec(field="code", operator="regex", value=long_pattern)

        with pytest.raises(FilterError, match="Invalid regex"):
            filter_engine.apply(items, [spec])
