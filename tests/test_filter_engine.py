"""Tests for filter engine module."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pypaginate.filters.predicates.engine import CompiledFilter, FilterEngine, filter_items


@dataclass
class _FilterItem:
    """Test item for filtering."""

    id: int
    name: str
    active: bool
    count: int | None = None


class TestFilterEngine:
    """Test FilterEngine class."""

    @pytest.fixture
    def engine(self) -> FilterEngine[_FilterItem]:
        """Create filter engine."""
        return FilterEngine()

    @pytest.fixture
    def items(self) -> list[_FilterItem]:
        """Create test items."""
        return [
            _FilterItem(id=1, name="Apple", active=True, count=5),
            _FilterItem(id=2, name="Banana", active=False, count=3),
            _FilterItem(id=3, name="Cherry", active=True, count=None),
            _FilterItem(id=4, name="Date", active=False, count=7),
        ]

    def test_creation(self, engine: FilterEngine[_FilterItem]) -> None:
        """Should create engine."""
        assert engine is not None

    def test_apply_by_bool(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """Should filter by boolean field."""
        result = engine.apply(items, {"active": True})
        assert len(result) == 2
        assert all(item.active for item in result)

    def test_apply_by_string_equality(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """Should filter by string equality."""
        result = engine.apply(items, {"name": {"eq": "Apple"}})
        assert len(result) == 1
        assert result[0].name == "Apple"

    def test_apply_by_numeric_greater_than(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """Should filter by numeric greater than."""
        result = engine.apply(items, {"count": {"gt": 4}})
        assert len(result) == 2  # Apple (5), Date (7)

    def test_apply_by_numeric_less_than(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """Should filter by numeric less than."""
        result = engine.apply(items, {"count": {"lt": 5}})
        assert len(result) == 1  # Banana (3)

    def test_apply_by_membership(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """Should filter by set membership."""
        result = engine.apply(items, {"name": {"in": ["Apple", "Cherry"]}})
        assert len(result) == 2

    def test_apply_combined_filters(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """Should apply multiple filters."""
        result = engine.apply(items, {"active": True, "name": {"in": ["Apple", "Cherry"]}})
        assert len(result) == 2

    def test_apply_none_spec_ignored(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """None spec should be ignored."""
        result = engine.apply(items, {"active": None})
        assert len(result) == 4  # All items pass

    def test_apply_empty_filters(
        self, engine: FilterEngine[_FilterItem], items: list[_FilterItem]
    ) -> None:
        """Empty filters should return all items."""
        result = engine.apply(items, {})
        assert len(result) == 4


class TestFilterItems:
    """Test filter_items function."""

    @pytest.fixture
    def items(self) -> list[_FilterItem]:
        """Create test items."""
        return [
            _FilterItem(id=1, name="Apple", active=True),
            _FilterItem(id=2, name="Banana", active=False),
            _FilterItem(id=3, name="Cherry", active=True),
        ]

    def test_filter_active_true(self, items: list[_FilterItem]) -> None:
        """Should filter active items."""
        result = filter_items(items, {"active": True})
        assert len(result) == 2
        assert all(item.active for item in result)

    def test_filter_active_false(self, items: list[_FilterItem]) -> None:
        """Should filter inactive items."""
        result = filter_items(items, {"active": False})
        assert len(result) == 1
        assert not result[0].active

    def test_filter_by_name(self, items: list[_FilterItem]) -> None:
        """Should filter by name."""
        result = filter_items(items, {"name": "Apple"})
        assert len(result) == 1
        assert result[0].name == "Apple"

    def test_filter_empty_list(self) -> None:
        """Should handle empty list."""
        result = filter_items([], {"active": True})
        assert result == []


class TestCompiledFilter:
    """Test CompiledFilter class."""

    def test_matches(self) -> None:
        """CompiledFilter.matches should work."""
        from pypaginate.filters.predicates.field_accessor import FieldAccessor

        accessor = FieldAccessor.from_string("active")

        def predicate(v: object) -> bool:
            return v is True

        compiled = CompiledFilter(accessor=accessor, predicate=predicate)
        item = {"active": True}
        assert compiled.matches(item) is True

    def test_not_matches(self) -> None:
        """CompiledFilter.matches should return False for non-matching."""
        from pypaginate.filters.predicates.field_accessor import FieldAccessor

        accessor = FieldAccessor.from_string("active")

        def predicate(v: object) -> bool:
            return v is True

        compiled = CompiledFilter(accessor=accessor, predicate=predicate)
        item = {"active": False}
        assert compiled.matches(item) is False
