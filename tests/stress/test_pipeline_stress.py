"""Stress tests for the full pipeline under heavy loads.

Tests large datasets, repeated execution, and extreme pagination.
All tests marked slow to skip by default (use --run-slow).
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate import FilterSpec, OffsetParams, SortSpec, paginate
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


pytestmark = [pytest.mark.stress, pytest.mark.slow]


def _build_data(count: int) -> list[dict[str, Any]]:
    """Generate user dicts for stress testing."""
    return [
        {"id": i, "name": f"user_{i}", "age": 20 + i % 50, "active": i % 3 != 0}
        for i in range(count)
    ]


def _build_pipeline() -> SyncPipeline[dict[str, Any]]:
    """Build a pipeline with filter and sort backends."""
    paginator: Paginator[dict[str, Any]] = Paginator(MemoryBackend())
    return SyncPipeline(
        paginator,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
    )


class TestPipelineLargeDatasets:
    """Pipeline stress with 10k-100k items."""

    def test_10k_items_complex_filter_sort(self) -> None:
        """10,000 items with 3 AND filters + sort + paginate."""
        data = _build_data(10_000)
        pipeline = _build_pipeline()
        filters = [
            FilterSpec(field="age", operator="gte", value=25),
            FilterSpec(field="age", operator="lte", value=60),
            FilterSpec(field="active", operator="eq", value=True),
        ]
        sorting = [SortSpec(field="age")]

        page = pipeline.execute(
            data,
            OffsetParams(page=1, limit=50),
            filters=filters,
            sorting=sorting,
        )

        assert page.total > 0
        assert all(25 <= item["age"] <= 60 for item in page.items)

    def test_50k_paginate_all_pages_completeness(self) -> None:
        """50,000 items: filter then paginate ALL pages."""
        data = _build_data(50_000)
        pipeline = _build_pipeline()
        filters = [FilterSpec(field="active", operator="eq", value=True)]
        collected: list[dict[str, Any]] = []
        page_num = 1

        while True:
            page = pipeline.execute(
                data,
                OffsetParams(page=page_num, limit=1000),
                filters=filters,
            )
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        expected = [d for d in data if d["active"]]
        assert len(collected) == len(expected)


class TestPipelineFilterReduction:
    """Filter drastically reduces dataset."""

    def test_100k_filtered_to_small_set(self) -> None:
        """100,000 items filtered to ~100 items paginates correctly."""
        data = _build_data(100_000)
        pipeline = _build_pipeline()
        filters = [FilterSpec(field="age", operator="eq", value=69)]

        page = pipeline.execute(data, OffsetParams(page=1, limit=50), filters=filters)

        assert page.total == len([d for d in data if d["age"] == 69])


class TestPipelineRepeatedExecution:
    """Repeated execution consistency."""

    def test_100_repeated_executions_consistent(self) -> None:
        """Same pipeline, 100 runs, identical results."""
        data = _build_data(1_000)
        pipeline = _build_pipeline()
        filters = [FilterSpec(field="age", operator="gte", value=30)]
        params = OffsetParams(page=1, limit=20)

        first = pipeline.execute(data, params, filters=filters)
        for _ in range(99):
            result = pipeline.execute(data, params, filters=filters)
            assert result.items == first.items


class TestPipelineLimitOne:
    """Extreme pagination: limit=1."""

    def test_limit_one_many_pages(self) -> None:
        """limit=1 on 100 items: verify page count and completeness."""
        data = _build_data(100)
        ids_seen: set[int] = set()
        page_num = 1

        while True:
            page = paginate(data, OffsetParams(page=page_num, limit=1))
            for item in page.items:
                ids_seen.add(item["id"])
            if not page.has_next:
                break
            page_num += 1

        assert len(ids_seen) == 100
        assert page_num == 100
