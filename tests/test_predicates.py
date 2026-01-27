"""Tests for filter predicates modules."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pypaginator.filters.predicates.field_accessor import FieldAccessor
from pypaginator.filters.predicates.registry import OperatorRegistry
from pypaginator.filters.predicates.engine import FilterEngine, filter_items


@dataclass
class _FilterTestItem:
    """Test item for filtering."""

    id: int
    name: str
    active: bool
    count: int | None = None


class TestFieldAccessor:
    """Test FieldAccessor class."""

    def test_simple_field(self) -> None:
        """Should get simple field value."""
        accessor = FieldAccessor.from_string("name")
        item = _FilterTestItem(id=1, name="test", active=True)
        result = accessor.resolve(item)
        assert result == "test"

    def test_nested_dict_field(self) -> None:
        """Should get nested dict field."""
        accessor = FieldAccessor.from_string("user.name")
        data = {"user": {"name": "John"}}
        result = accessor.resolve(data)
        assert result == "John"

    def test_deep_nesting(self) -> None:
        """Should handle deep nesting."""
        accessor = FieldAccessor.from_string("a.b.c")
        data = {"a": {"b": {"c": "value"}}}
        result = accessor.resolve(data)
        assert result == "value"

    def test_none_field(self) -> None:
        """Should return None for None field."""
        accessor = FieldAccessor.from_string("count")
        item = _FilterTestItem(id=1, name="test", active=True, count=None)
        result = accessor.resolve(item)
        assert result is None

    def test_array_index(self) -> None:
        """Should handle array indexing."""
        accessor = FieldAccessor.from_string("items.0")
        data = {"items": ["first", "second", "third"]}
        result = accessor.resolve(data)
        assert result == "first"

    def test_missing_field(self) -> None:
        """Should return None for missing field."""
        accessor = FieldAccessor.from_string("nonexistent")
        data = {"name": "test"}
        result = accessor.resolve(data)
        assert result is None


class TestOperatorRegistry:
    """Test OperatorRegistry class."""

    def test_default_registry(self) -> None:
        """Default registry should have operators."""
        registry = OperatorRegistry.default()
        assert registry is not None

    def test_build_eq_predicate(self) -> None:
        """Should build eq predicate."""
        registry = OperatorRegistry.default()
        predicate = registry.build("eq", 5)
        assert predicate(5) is True
        assert predicate(6) is False

    def test_build_unknown_operator_raises(self) -> None:
        """Building unknown operator should raise."""
        from pypaginator.exceptions import FilterValidationError

        registry = OperatorRegistry.default()
        with pytest.raises(FilterValidationError):
            registry.build("unknown_operator", 5)

    def test_register_custom_operator(self) -> None:
        """Should allow registering custom operators."""
        registry: OperatorRegistry[object] = OperatorRegistry()

        def custom_factory(arg: object) -> object:
            return lambda x: str(x) == str(arg)

        registry.register(["custom"], custom_factory)
        predicate = registry.build("custom", "test")
        assert predicate("test") is True


class TestFilterEngine:
    """Test FilterEngine class."""

    @pytest.fixture
    def items(self) -> list[_FilterTestItem]:
        """Create test items."""
        return [
            _FilterTestItem(id=1, name="apple", active=True, count=10),
            _FilterTestItem(id=2, name="banana", active=False, count=20),
            _FilterTestItem(id=3, name="cherry", active=True, count=30),
        ]

    def test_apply_eq_filter(self, items: list[_FilterTestItem]) -> None:
        """Should filter with eq operator."""
        engine: FilterEngine[_FilterTestItem] = FilterEngine()
        filters = {"name": {"eq": "banana"}}
        result = engine.apply(items, filters)
        assert len(result) == 1
        assert result[0].name == "banana"

    def test_apply_multiple_filters(self, items: list[_FilterTestItem]) -> None:
        """Should apply multiple filters."""
        engine: FilterEngine[_FilterTestItem] = FilterEngine()
        filters = {
            "active": {"eq": True},
            "count": {"gt": 15},
        }
        result = engine.apply(items, filters)
        assert len(result) == 1
        assert result[0].name == "cherry"

    def test_apply_no_match(self, items: list[_FilterTestItem]) -> None:
        """Should return empty when no match."""
        engine: FilterEngine[_FilterTestItem] = FilterEngine()
        filters = {"name": {"eq": "xyz"}}
        result = engine.apply(items, filters)
        assert len(result) == 0

    def test_apply_empty_filters(self, items: list[_FilterTestItem]) -> None:
        """Should return all items when no filters."""
        engine: FilterEngine[_FilterTestItem] = FilterEngine()
        result = engine.apply(items, {})
        assert len(result) == 3


class TestFilterItemsFunction:
    """Test filter_items convenience function."""

    @pytest.fixture
    def items(self) -> list[dict[str, object]]:
        """Create test items."""
        return [
            {"id": 1, "name": "apple", "price": 1.0},
            {"id": 2, "name": "banana", "price": 2.0},
            {"id": 3, "name": "cherry", "price": 3.0},
        ]

    def test_filter_items(self, items: list[dict[str, object]]) -> None:
        """Should filter items."""
        result = filter_items(items, {"price": {"gt": 1.5}})
        assert len(result) == 2

    def test_filter_items_empty_filters(
        self, items: list[dict[str, object]]
    ) -> None:
        """Should return all items when no filters."""
        result = filter_items(items, {})
        assert len(result) == 3
