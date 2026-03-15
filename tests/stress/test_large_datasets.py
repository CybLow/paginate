"""Stress tests with large datasets (50k-100k items)."""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import FilterSpec, OffsetParams, SortSpec, paginate
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry
from pypaginate.sorting.engine import SortEngine


pytestmark = [pytest.mark.stress, pytest.mark.slow]


def _build_large(count: int) -> list[dict[str, Any]]:
    """Generate user dicts for stress testing."""
    return [{"id": i, "name": f"user_{i}", "age": 20 + i % 50} for i in range(count)]


class TestLargeDatasetPagination:
    def test_paginate_100k_items(self) -> None:
        """Paginate 100,000 items verifying total and pages."""
        data = _build_large(100_000)
        result = paginate(data, OffsetParams(page=1, limit=100))

        assert result.total == 100_000
        assert result.pages == 1_000

    def test_paginate_100k_last_page(self) -> None:
        """Last page of 100,000 items has correct count."""
        data = _build_large(100_000)
        result = paginate(data, OffsetParams(page=1000, limit=100))

        assert len(result.items) == 100
        assert result.has_next is False


class TestLargeDatasetFilter:
    def test_filter_100k_items(self) -> None:
        """Filter 100,000 items returns correct subset."""
        data = _build_large(100_000)
        engine = FilterEngine(create_default_registry())
        specs = [FilterSpec(field="age", operator="gte", value=50)]

        result = engine.apply(data, specs)

        assert len(result) < len(data)
        assert all(item["age"] >= 50 for item in result)


class TestLargeDatasetSort:
    def test_sort_100k_items(self) -> None:
        """Sort 100,000 items verifying order."""
        data = _build_large(100_000)
        engine = SortEngine()

        result = engine.apply(data, [SortSpec(field="age")])

        assert result[0]["age"] <= result[-1]["age"]


class TestLargeDatasetPipeline:
    def test_pipeline_50k_items(self) -> None:
        """Full pipeline on 50,000 items."""
        data = _build_large(50_000)
        fe = FilterEngine(create_default_registry())
        se = SortEngine()

        filtered = fe.apply(data, [FilterSpec(field="age", operator="gte", value=30)])
        sorted_items = se.apply(filtered, [SortSpec(field="age")])
        result = paginate(sorted_items, OffsetParams(page=1, limit=50))

        assert result.total > 0
        assert len(result.items) <= 50
