"""Tests for sort engine module."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pypaginator.sorting.engine import SortEngine, sort_items


@dataclass
class _SortItem:
    """Test item for sorting."""

    id: int
    name: str
    score: float


class TestSortEngine:
    """Test SortEngine class."""

    @pytest.fixture
    def items(self) -> list[_SortItem]:
        """Create test items."""
        return [
            _SortItem(id=1, name="Charlie", score=90.0),
            _SortItem(id=2, name="Alice", score=85.0),
            _SortItem(id=3, name="Bob", score=95.0),
        ]

    def test_creation(self) -> None:
        """Should create engine."""
        engine = SortEngine()
        assert engine is not None

    def test_sort_by_name_asc(self, items: list[_SortItem]) -> None:
        """Should sort by name ascending."""
        result = SortEngine.sort(
            items, sort_field="name", reverse=False, nulls_position="last", tie_breaker_field=None
        )
        assert result[0].name == "Alice"
        assert result[1].name == "Bob"
        assert result[2].name == "Charlie"

    def test_sort_by_name_desc(self, items: list[_SortItem]) -> None:
        """Should sort by name descending."""
        result = SortEngine.sort(
            items, sort_field="name", reverse=True, nulls_position="last", tie_breaker_field=None
        )
        assert result[0].name == "Charlie"
        assert result[1].name == "Bob"
        assert result[2].name == "Alice"

    def test_sort_by_score_asc(self, items: list[_SortItem]) -> None:
        """Should sort by score ascending."""
        result = SortEngine.sort(
            items, sort_field="score", reverse=False, nulls_position="last", tie_breaker_field=None
        )
        assert result[0].score == 85.0
        assert result[1].score == 90.0
        assert result[2].score == 95.0

    def test_sort_by_score_desc(self, items: list[_SortItem]) -> None:
        """Should sort by score descending."""
        result = SortEngine.sort(
            items, sort_field="score", reverse=True, nulls_position="last", tie_breaker_field=None
        )
        assert result[0].score == 95.0
        assert result[1].score == 90.0
        assert result[2].score == 85.0

    def test_sort_by_id(self, items: list[_SortItem]) -> None:
        """Should sort by id."""
        result = SortEngine.sort(
            items, sort_field="id", reverse=False, nulls_position="last", tie_breaker_field=None
        )
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[2].id == 3

    def test_sort_with_tie_breaker(self, items: list[_SortItem]) -> None:
        """Should use tie breaker field."""
        result = SortEngine.sort(
            items, sort_field="score", reverse=False, nulls_position="last", tie_breaker_field="id"
        )
        assert len(result) == 3


class TestSortItems:
    """Test sort_items function."""

    @pytest.fixture
    def items(self) -> list[_SortItem]:
        """Create test items."""
        return [
            _SortItem(id=1, name="Charlie", score=90.0),
            _SortItem(id=2, name="Alice", score=85.0),
            _SortItem(id=3, name="Bob", score=95.0),
        ]

    def test_sort_ascending(self, items: list[_SortItem]) -> None:
        """Should sort ascending."""
        result = sort_items(
            items, sort_field="name", reverse=False, nulls_position="last", tie_breaker_field=None
        )
        assert result[0].name == "Alice"

    def test_sort_descending(self, items: list[_SortItem]) -> None:
        """Should sort descending."""
        result = sort_items(
            items, sort_field="name", reverse=True, nulls_position="last", tie_breaker_field=None
        )
        assert result[0].name == "Charlie"

    def test_empty_list(self) -> None:
        """Should handle empty list."""
        result = sort_items(
            [], sort_field="name", reverse=False, nulls_position="last", tie_breaker_field=None
        )
        assert result == []

    def test_nulls_first(self) -> None:
        """Should position nulls first."""

        @dataclass
        class NullableItem:
            id: int
            name: str | None

        items = [NullableItem(1, "Bob"), NullableItem(2, None), NullableItem(3, "Alice")]
        result = sort_items(
            items, sort_field="name", reverse=False, nulls_position="first", tie_breaker_field=None
        )
        assert result[0].name is None

    def test_nulls_last(self) -> None:
        """Should position nulls last."""

        @dataclass
        class NullableItem:
            id: int
            name: str | None

        items = [NullableItem(1, "Bob"), NullableItem(2, None), NullableItem(3, "Alice")]
        result = sort_items(
            items, sort_field="name", reverse=False, nulls_position="last", tie_breaker_field=None
        )
        assert result[-1].name is None
