"""Tests for FilterGroup, And(), Or(), and nested group compilation."""

from __future__ import annotations

from pypaginate.domain.specs import And, FilterGroup, FilterSpec, Or
from tests.support.engines import FilterEngine


_ITEMS = [
    {"x": 1, "y": "a"},
    {"x": 2, "y": "b"},
    {"x": 3, "y": "a"},
    {"x": 4, "y": "b"},
]


class TestAndGroup:
    def test_and_with_two_specs_returns_intersection(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = And(
            FilterSpec(field="x", operator="gte", value=2),
            FilterSpec(field="y", operator="eq", value="a"),
        )

        result = filter_engine.apply(_ITEMS, group)

        assert result == [{"x": 3, "y": "a"}]

    def test_and_with_no_match_returns_empty(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = And(
            FilterSpec(field="x", operator="eq", value=1),
            FilterSpec(field="y", operator="eq", value="b"),
        )

        assert filter_engine.apply(_ITEMS, group) == []


class TestOrGroup:
    def test_or_with_two_specs_returns_union(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = Or(
            FilterSpec(field="x", operator="eq", value=1),
            FilterSpec(field="x", operator="eq", value=4),
        )

        result = filter_engine.apply(_ITEMS, group)

        assert len(result) == 2
        assert result[0]["x"] == 1
        assert result[1]["x"] == 4

    def test_or_with_no_match_returns_empty(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = Or(
            FilterSpec(field="x", operator="eq", value=99),
            FilterSpec(field="x", operator="eq", value=100),
        )

        assert filter_engine.apply(_ITEMS, group) == []


class TestNestedGroups:
    def test_and_of_or_groups(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = And(
            Or(
                FilterSpec(field="x", operator="eq", value=1),
                FilterSpec(field="x", operator="eq", value=3),
            ),
            Or(
                FilterSpec(field="y", operator="eq", value="a"),
                FilterSpec(field="y", operator="eq", value="b"),
            ),
        )

        result = filter_engine.apply(_ITEMS, group)

        assert len(result) == 2
        xs = [r["x"] for r in result]
        assert xs == [1, 3]

    def test_or_of_and_groups(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = Or(
            And(
                FilterSpec(field="x", operator="eq", value=1),
                FilterSpec(field="y", operator="eq", value="a"),
            ),
            And(
                FilterSpec(field="x", operator="eq", value=4),
                FilterSpec(field="y", operator="eq", value="b"),
            ),
        )

        result = filter_engine.apply(_ITEMS, group)

        assert len(result) == 2
        xs = [r["x"] for r in result]
        assert xs == [1, 4]

    def test_deeply_nested(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = And(
            Or(
                And(
                    FilterSpec(field="x", operator="gte", value=1),
                    FilterSpec(field="x", operator="lte", value=2),
                ),
                FilterSpec(field="x", operator="eq", value=4),
            ),
        )

        result = filter_engine.apply(_ITEMS, group)

        xs = [r["x"] for r in result]
        assert xs == [1, 2, 4]

    def test_single_spec_in_group(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = And(FilterSpec(field="x", operator="eq", value=2))

        result = filter_engine.apply(_ITEMS, group)

        assert result == [{"x": 2, "y": "b"}]

    def test_empty_group_returns_all(
        self,
        filter_engine: FilterEngine,
    ) -> None:
        group = FilterGroup(conditions=())

        result = filter_engine.apply(_ITEMS, group)

        assert result == _ITEMS
