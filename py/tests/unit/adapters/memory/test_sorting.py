"""Tests for MemorySortBackend."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.domain.enums import SortDirection
from pypaginate.domain.specs import SortSpec


@pytest.fixture()
def backend() -> MemorySortBackend:
    """MemorySortBackend instance."""
    return MemorySortBackend()


class TestSortDirection:
    def test_asc_orders_correctly(self, backend: MemorySortBackend) -> None:
        items = [{"age": 30}, {"age": 10}, {"age": 20}]

        result: list[dict[str, Any]] = backend.apply_sorting(items, [SortSpec(field="age")])  # type: ignore[assignment]

        assert [r["age"] for r in result] == [10, 20, 30]

    def test_desc_orders_correctly(self, backend: MemorySortBackend) -> None:
        items = [{"age": 10}, {"age": 30}, {"age": 20}]
        spec = SortSpec(field="age", direction=SortDirection.DESC)

        result: list[dict[str, Any]] = backend.apply_sorting(items, [spec])  # type: ignore[assignment]

        assert [r["age"] for r in result] == [30, 20, 10]


class TestSortEdgeCases:
    def test_empty_specs_returns_copy(self, backend: MemorySortBackend) -> None:
        items = [{"a": 2}, {"a": 1}]

        result: list[Any] = backend.apply_sorting(items, [])  # type: ignore[assignment]

        assert result == items

    def test_none_values_placed_last(self, backend: MemorySortBackend) -> None:
        items = [{"v": None}, {"v": 1}, {"v": 3}]

        result: list[dict[str, Any]] = backend.apply_sorting(items, [SortSpec(field="v")])  # type: ignore[assignment]

        assert result[-1]["v"] is None

    def test_multi_field_sort(self, backend: MemorySortBackend) -> None:
        items = [
            {"dept": "B", "name": "Zara"},
            {"dept": "A", "name": "Bob"},
            {"dept": "A", "name": "Alice"},
        ]
        specs = [SortSpec(field="dept"), SortSpec(field="name")]

        result: list[dict[str, Any]] = backend.apply_sorting(items, specs)  # type: ignore[assignment]

        assert result[0] == {"dept": "A", "name": "Alice"}
        assert result[1] == {"dept": "A", "name": "Bob"}
