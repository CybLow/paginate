"""Unit tests for the And/Or group builders and search_spec validation."""

from __future__ import annotations

import pytest

from pypaginate import (
    And,
    FilterGroup,
    FilterSpec,
    Or,
    SearchSpec,
    search_spec,
)
from pypaginate._core import MAX_FILTER_DEPTH, MAX_QUERY_LEN
from pypaginate.errors import (
    FilterError,
    FilterValidationError,
    SearchError,
    SearchQueryError,
)


pytestmark = [pytest.mark.unit, pytest.mark.filters]


def _leaf() -> FilterSpec:
    return FilterSpec(field="age", operator="eq", value=1)


def _nested(depth: int) -> FilterGroup:
    """Build a group nested ``depth`` levels deep (And(And(...(leaf)))))."""
    node: FilterGroup = And(_leaf())
    for _ in range(depth - 1):
        node = And(node)
    return node


class TestGroupBuilders:
    def test_and_builds_and_group(self) -> None:
        group = And(_leaf(), _leaf())

        assert isinstance(group, FilterGroup)
        assert group.logic == "and"
        assert len(group.conditions) == 2

    def test_or_builds_or_group(self) -> None:
        group = Or(_leaf(), _leaf())

        assert group.logic == "or"
        assert len(group.conditions) == 2

    def test_groups_nest(self) -> None:
        group = And(_leaf(), Or(_leaf(), _leaf()))

        assert group.logic == "and"
        assert isinstance(group.conditions[1], FilterGroup)
        assert group.conditions[1].logic == "or"

    def test_max_depth_is_accepted(self) -> None:
        group = _nested(MAX_FILTER_DEPTH)

        assert isinstance(group, FilterGroup)

    def test_depth_beyond_limit_raises_filter_validation_error(self) -> None:
        with pytest.raises(FilterValidationError, match="nesting must not exceed"):
            _nested(MAX_FILTER_DEPTH + 1)

    def test_depth_error_is_a_filter_error(self) -> None:
        with pytest.raises(FilterError):
            _nested(MAX_FILTER_DEPTH + 1)


class TestSearchSpecValidation:
    def test_valid_query_returns_same_spec(self) -> None:
        spec = SearchSpec(query="alice", fields=["name"])

        assert search_spec(spec) is spec

    def test_query_over_limit_raises_search_query_error(self) -> None:
        spec = SearchSpec(query="x" * (MAX_QUERY_LEN + 1), fields=["name"])

        with pytest.raises(SearchQueryError, match="must not exceed"):
            search_spec(spec)

    def test_search_query_error_is_a_search_error(self) -> None:
        spec = SearchSpec(query="x" * (MAX_QUERY_LEN + 1), fields=["name"])

        with pytest.raises(SearchError):
            search_spec(spec)

    def test_query_at_limit_is_accepted(self) -> None:
        spec = SearchSpec(query="x" * MAX_QUERY_LEN, fields=["name"])

        assert search_spec(spec) is spec
