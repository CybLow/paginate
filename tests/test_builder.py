"""Tests for JSON Logic predicate builder."""

from __future__ import annotations

import pytest

from pypaginate.filters.predicates.builder import JsonLogicPredicateBuilder
from pypaginate.filters.predicates.registry import OperatorRegistry


class TestJsonLogicPredicateBuilder:
    """Test JsonLogicPredicateBuilder class."""

    @pytest.fixture
    def registry(self) -> OperatorRegistry[object]:
        """Create default registry."""
        return OperatorRegistry.default()

    @pytest.fixture
    def builder(self, registry: OperatorRegistry[object]) -> JsonLogicPredicateBuilder:
        """Create builder."""
        return JsonLogicPredicateBuilder(registry)

    def test_creation(self, builder: JsonLogicPredicateBuilder) -> None:
        """Should create builder."""
        assert builder is not None

    def test_build_scalar_spec(self, builder: JsonLogicPredicateBuilder) -> None:
        """Should build from scalar spec (equality)."""
        predicate = builder.build(5)
        assert predicate(5) is True
        assert predicate(6) is False

    def test_build_mapping_spec(self, builder: JsonLogicPredicateBuilder) -> None:
        """Should build from mapping spec."""
        predicate = builder.build({"eq": 5})
        assert predicate(5) is True
        assert predicate(6) is False

    def test_build_multiple_conditions(self, builder: JsonLogicPredicateBuilder) -> None:
        """Should combine multiple conditions with AND."""
        spec = {"gt": 3, "lt": 10}
        predicate = builder.build(spec)
        assert predicate(5) is True
        assert predicate(2) is False
        assert predicate(15) is False

    def test_build_collection_spec(self, builder: JsonLogicPredicateBuilder) -> None:
        """Should build from collection spec (membership)."""
        predicate = builder.build([1, 2, 3])
        assert predicate(2) is True
        assert predicate(5) is False

    def test_build_tuple_spec(self, builder: JsonLogicPredicateBuilder) -> None:
        """Should build from tuple spec."""
        predicate = builder.build((1, 2, 3))
        assert predicate(2) is True
        assert predicate(5) is False

    def test_nested_mapping(self, builder: JsonLogicPredicateBuilder) -> None:
        """Should handle nested mappings."""
        spec = {"gte": 0, "lte": 100}
        predicate = builder.build(spec)
        assert predicate(50) is True
        assert predicate(-1) is False
        assert predicate(101) is False


class TestJsonLogicOperators:
    """Test various operators through the builder."""

    @pytest.fixture
    def builder(self) -> JsonLogicPredicateBuilder:
        """Create builder with default registry."""
        return JsonLogicPredicateBuilder(OperatorRegistry.default())

    def test_eq_operator(self, builder: JsonLogicPredicateBuilder) -> None:
        """Test eq operator."""
        predicate = builder.build({"eq": "hello"})
        assert predicate("hello") is True
        assert predicate("world") is False

    def test_ne_operator(self, builder: JsonLogicPredicateBuilder) -> None:
        """Test ne operator."""
        predicate = builder.build({"ne": "hello"})
        assert predicate("hello") is False
        assert predicate("world") is True

    def test_in_operator(self, builder: JsonLogicPredicateBuilder) -> None:
        """Test in operator."""
        predicate = builder.build({"in": [1, 2, 3]})
        assert predicate(2) is True
        assert predicate(5) is False

    def test_gt_operator(self, builder: JsonLogicPredicateBuilder) -> None:
        """Test gt operator."""
        predicate = builder.build({"gt": 5})
        assert predicate(6) is True
        assert predicate(5) is False

    def test_gte_operator(self, builder: JsonLogicPredicateBuilder) -> None:
        """Test gte operator."""
        predicate = builder.build({"gte": 5})
        assert predicate(5) is True
        assert predicate(4) is False

    def test_lt_operator(self, builder: JsonLogicPredicateBuilder) -> None:
        """Test lt operator."""
        predicate = builder.build({"lt": 5})
        assert predicate(4) is True
        assert predicate(5) is False

    def test_lte_operator(self, builder: JsonLogicPredicateBuilder) -> None:
        """Test lte operator."""
        predicate = builder.build({"lte": 5})
        assert predicate(5) is True
        assert predicate(6) is False
