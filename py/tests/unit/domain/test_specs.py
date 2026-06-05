"""Tests for FilterSpec, SortSpec, SearchSpec, and FilterGroup."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pypaginate.domain.enums import (
    FilterLogic,
    FuzzyMode,
    NullsPosition,
    SearchFieldMode,
    SortDirection,
)
from pypaginate.domain.specs import (
    And,
    FilterOperator,
    FilterSpec,
    SearchSpec,
    SortSpec,
)


ALL_OPERATORS: list[FilterOperator] = [
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "not_in",
    "contains",
    "starts_with",
    "ends_with",
    "like",
    "ilike",
    "between",
    "is_null",
    "is_not_null",
    "regex",
    "empty",
    "not_empty",
    "exists",
]


class TestFilterSpec:
    def test_default_operator_is_eq(self) -> None:
        spec = FilterSpec(field="name", value="Alice")

        assert spec.operator == "eq"

    def test_default_logic_is_and(self) -> None:
        spec = FilterSpec(field="name", value="Alice")

        assert spec.logic is FilterLogic.AND

    def test_custom_operator_accepted(self) -> None:
        spec = FilterSpec(field="age", operator="gte", value=18)

        assert spec.operator == "gte"

    @pytest.mark.parametrize("operator", ALL_OPERATORS)
    def test_all_operators_accepted(self, operator: FilterOperator) -> None:
        spec = FilterSpec(field="x", operator=operator)

        assert spec.operator == operator

    def test_invalid_operator_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            FilterSpec(field="x", operator="invalid_op")  # type: ignore[arg-type]


class TestSortSpec:
    def test_default_direction_is_asc(self) -> None:
        spec = SortSpec(field="name")

        assert spec.direction is SortDirection.ASC

    def test_default_nulls_is_last(self) -> None:
        spec = SortSpec(field="name")

        assert spec.nulls is NullsPosition.LAST

    def test_desc_direction_accepted(self) -> None:
        spec = SortSpec(field="created_at", direction=SortDirection.DESC)

        assert spec.direction is SortDirection.DESC


class TestSearchSpec:
    def test_requires_query_and_fields(self) -> None:
        spec = SearchSpec(query="hello", fields=("name", "email"))

        assert spec.query == "hello"
        assert spec.fields == ("name", "email")

    def test_default_mode_is_contains(self) -> None:
        spec = SearchSpec(query="hi", fields=("name",))

        assert spec.mode is SearchFieldMode.CONTAINS

    def test_default_fuzzy_is_exact(self) -> None:
        spec = SearchSpec(query="hi", fields=("name",))

        assert spec.fuzzy is FuzzyMode.EXACT

    def test_default_threshold_is_trigram_default(self) -> None:
        # Trigram similarity default (pg_trgm's 0.3), not the old rapidfuzz 75.
        spec = SearchSpec(query="hi", fields=("name",))

        assert spec.threshold == 30

    def test_custom_threshold(self) -> None:
        spec = SearchSpec(query="hi", fields=("name",), threshold=90)

        assert spec.threshold == 90

    def test_query_exceeding_500_chars_raises(self) -> None:
        long_query = "a" * 501
        with pytest.raises(ValidationError, match="500 characters"):
            SearchSpec(query=long_query, fields=("name",))


class TestFilterGroupNesting:
    def test_depth_exceeding_5_levels_raises(self) -> None:
        """Build a 6-deep FilterGroup tree; expect validation failure."""
        leaf = FilterSpec(field="x", value=1)
        # Build depth 5 (the maximum allowed)
        group = And(leaf)  # depth 1
        for _ in range(4):
            group = And(group)  # depths 2, 3, 4, 5

        # Wrapping once more creates depth 6, which exceeds 5
        with pytest.raises(ValidationError, match="5 levels"):
            And(group)
