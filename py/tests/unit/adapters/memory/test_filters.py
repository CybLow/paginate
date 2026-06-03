"""Tests for MemoryFilterBackend."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.domain.specs import FilterSpec


@pytest.fixture()
def backend() -> MemoryFilterBackend:
    """MemoryFilterBackend with default registry."""
    return MemoryFilterBackend()


class TestApplyFiltersSingle:
    def test_eq_filter_returns_matching_items(
        self,
        backend: MemoryFilterBackend,
    ) -> None:
        items = [{"name": "Alice"}, {"name": "Bob"}]
        filters = [FilterSpec(field="name", operator="eq", value="Alice")]

        result: list[Any] = backend.apply_filters(items, filters)  # type: ignore[assignment]

        assert result == [{"name": "Alice"}]

    def test_no_matches_returns_empty(
        self,
        backend: MemoryFilterBackend,
    ) -> None:
        items = [{"name": "Alice"}, {"name": "Bob"}]
        filters = [FilterSpec(field="name", operator="eq", value="Zara")]

        result: list[Any] = backend.apply_filters(items, filters)  # type: ignore[assignment]

        assert result == []


class TestApplyFiltersMultiple:
    def test_multiple_and_filters_narrow_results(
        self,
        backend: MemoryFilterBackend,
    ) -> None:
        items = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
        filters = [
            FilterSpec(field="age", operator="gte", value=28),
            FilterSpec(field="age", operator="lt", value=35),
        ]

        result: list[Any] = backend.apply_filters(items, filters)  # type: ignore[assignment]

        assert result == [{"name": "Alice", "age": 30}]


class TestApplyFiltersEdgeCases:
    def test_empty_filters_returns_all(
        self,
        backend: MemoryFilterBackend,
    ) -> None:
        items = [{"x": 1}, {"x": 2}]

        result: list[Any] = backend.apply_filters(items, [])  # type: ignore[assignment]

        assert result == items

    def test_delegates_to_registry_operator(
        self,
        backend: MemoryFilterBackend,
    ) -> None:
        items = [{"v": "hello world"}, {"v": "goodbye"}]
        filters = [FilterSpec(field="v", operator="contains", value="hello")]

        result: list[Any] = backend.apply_filters(items, filters)  # type: ignore[assignment]

        assert len(result) == 1
        assert result[0]["v"] == "hello world"
