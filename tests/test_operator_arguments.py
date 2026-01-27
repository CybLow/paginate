"""Tests for operator arguments module."""

from __future__ import annotations

import pytest

from pypaginator.filters.predicates.operator_arguments import (
    ensure_collection,
    ensure_pair,
)
from pypaginator.exceptions import FilterValidationError


class TestEnsureCollection:
    """Test ensure_collection function."""

    def test_list_passthrough(self) -> None:
        """List should pass through."""
        result = list(ensure_collection([1, 2, 3], "in"))
        assert result == [1, 2, 3]

    def test_tuple_passthrough(self) -> None:
        """Tuple should pass through."""
        result = list(ensure_collection((1, 2, 3), "in"))
        assert result == [1, 2, 3]

    def test_set_passthrough(self) -> None:
        """Set should pass through (as iterable)."""
        result = set(ensure_collection({1, 2, 3}, "in"))
        assert result == {1, 2, 3}

    def test_string_raises(self) -> None:
        """String should be wrapped as singleton (not treated as collection)."""
        result = ensure_collection("hello", "in")
        # Strings are wrapped as singleton
        assert result == ("hello",)

    def test_non_collection_wrapped_as_singleton(self) -> None:
        """Non-collection should be wrapped as singleton."""
        result = ensure_collection(123, "in")
        assert result == (123,)

    def test_none_raises(self) -> None:
        """None should raise."""
        with pytest.raises(FilterValidationError):
            ensure_collection(None, "in")

    def test_mapping_raises(self) -> None:
        """Mapping should raise."""
        with pytest.raises(FilterValidationError):
            ensure_collection({"key": "value"}, "in")


class TestEnsurePair:
    """Test ensure_pair function."""

    def test_list_of_two(self) -> None:
        """List of two should work."""
        lower, upper = ensure_pair([5, 10], "between")
        assert lower == 5
        assert upper == 10

    def test_tuple_of_two(self) -> None:
        """Tuple of two should work."""
        lower, upper = ensure_pair((5, 10), "between")
        assert lower == 5
        assert upper == 10

    def test_single_element_raises(self) -> None:
        """Single element should raise."""
        with pytest.raises(FilterValidationError):
            ensure_pair([5], "between")

    def test_three_elements_raises(self) -> None:
        """Three elements should raise."""
        with pytest.raises(FilterValidationError):
            ensure_pair([1, 2, 3], "between")

    def test_non_sequence_raises(self) -> None:
        """Non-sequence should raise."""
        with pytest.raises(FilterValidationError):
            ensure_pair(123, "between")

    def test_string_raises(self) -> None:
        """String should raise (not treated as sequence)."""
        with pytest.raises(FilterValidationError):
            ensure_pair("ab", "between")
