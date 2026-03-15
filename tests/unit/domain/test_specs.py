"""Tests for FilterSpec, SortSpec, and SearchSpec."""

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
from pypaginate.domain.specs import FilterOperator, FilterSpec, SearchSpec, SortSpec


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

    def test_default_threshold_is_75(self) -> None:
        spec = SearchSpec(query="hi", fields=("name",))

        assert spec.threshold == 75

    def test_custom_threshold(self) -> None:
        spec = SearchSpec(query="hi", fields=("name",), threshold=90)

        assert spec.threshold == 90
