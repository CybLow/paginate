"""Tests for operator registry module."""

from __future__ import annotations

import pytest

from pypaginator.filters.predicates.registry import OperatorRegistry


class TestOperatorRegistry:
    """Test OperatorRegistry class."""

    def test_default_creates_registry(self) -> None:
        """default() should create registry."""
        registry = OperatorRegistry.default()
        assert registry is not None

    def test_default_has_eq_operator(self) -> None:
        """Default registry should have eq operator."""
        registry = OperatorRegistry.default()
        predicate = registry.build("eq", 5)
        assert predicate(5) is True
        assert predicate(6) is False

    def test_default_has_ne_operator(self) -> None:
        """Default registry should have ne operator."""
        registry = OperatorRegistry.default()
        predicate = registry.build("ne", 5)
        assert predicate(5) is False
        assert predicate(6) is True

    def test_default_has_gt_operator(self) -> None:
        """Default registry should have gt operator."""
        registry = OperatorRegistry.default()
        predicate = registry.build("gt", 5)
        assert predicate(6) is True
        assert predicate(5) is False

    def test_default_has_gte_operator(self) -> None:
        """Default registry should have gte operator."""
        registry = OperatorRegistry.default()
        predicate = registry.build("gte", 5)
        assert predicate(5) is True
        assert predicate(4) is False

    def test_default_has_lt_operator(self) -> None:
        """Default registry should have lt operator."""
        registry = OperatorRegistry.default()
        predicate = registry.build("lt", 5)
        assert predicate(4) is True
        assert predicate(5) is False

    def test_default_has_lte_operator(self) -> None:
        """Default registry should have lte operator."""
        registry = OperatorRegistry.default()
        predicate = registry.build("lte", 5)
        assert predicate(5) is True
        assert predicate(6) is False

    def test_default_has_in_operator(self) -> None:
        """Default registry should have in operator."""
        registry = OperatorRegistry.default()
        predicate = registry.build("in", [1, 2, 3])
        assert predicate(2) is True
        assert predicate(5) is False
