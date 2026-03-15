"""End-to-end tests for full pipeline flows with ALL adapters.

Verifies filter + sort + search + paginate working together
through complete workflows with correctness guarantees.
"""

from __future__ import annotations

import pytest

from pypaginate import (
    FilterSpec,
    OffsetParams,
    SearchSpec,
    SortDirection,
    SortSpec,
)
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


def _build_pipeline() -> SyncPipeline[dict[str, object]]:
    """Build a fully-wired SyncPipeline with all backends."""
    paginator: Paginator[dict[str, object]] = Paginator(MemoryBackend())
    return SyncPipeline(
        paginator,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
        search_backend=MemorySearchBackend(),
    )


def _make_dataset(count: int) -> list[dict[str, object]]:
    """Generate a dataset of user dicts."""
    return [
        {
            "id": i,
            "name": f"User_{i}",
            "age": 20 + (i % 50),
            "email": f"user{i}@test.com",
            "active": i % 3 != 0,
        }
        for i in range(count)
    ]


class TestFullPipelineFlow:
    """Full filter + sort + search + paginate."""

    def test_full_flow_first_page(self) -> None:
        """Filter active, sort age DESC, search 'user', paginate."""
        pipeline = _build_pipeline()
        data = _make_dataset(50)
        filters = [FilterSpec(field="active", operator="eq", value=True)]
        sorting = [SortSpec(field="age", direction=SortDirection.DESC)]
        search = SearchSpec(query="user", fields=("name",))

        page = pipeline.execute(
            data,
            OffsetParams(page=1, limit=5),
            filters=filters,
            sorting=sorting,
            search=search,
        )

        assert len(page.items) <= 5
        assert all(item["active"] is True for item in page.items)

    def test_iterate_all_pages_no_items_lost(self) -> None:
        """Paginate all pages of a filtered+sorted dataset."""
        pipeline = _build_pipeline()
        data = _make_dataset(100)
        filters = [FilterSpec(field="age", operator="gte", value=30)]
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            page = pipeline.execute(
                data,
                OffsetParams(page=page_num, limit=10),
                filters=filters,
                sorting=sorting,
            )
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        expected = [d for d in data if d["age"] >= 30]
        assert len(collected) == len(expected)

    def test_filter_reduces_to_zero(self) -> None:
        """Pipeline with filter matching nothing yields empty page."""
        pipeline = _build_pipeline()
        data = _make_dataset(50)
        filters = [FilterSpec(field="age", operator="gt", value=999)]

        page = pipeline.execute(data, OffsetParams(page=1, limit=10), filters=filters)

        assert page.items == []
        assert page.total == 0


class TestPipelineConsistency:
    """Pipeline idempotency and ordering guarantees."""

    def test_idempotent_execution(self) -> None:
        """Same pipeline on same data gives identical results."""
        pipeline = _build_pipeline()
        data = _make_dataset(50)
        filters = [FilterSpec(field="active", operator="eq", value=True)]
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        params = OffsetParams(page=1, limit=10)

        first = pipeline.execute(data, params, filters=filters, sorting=sorting)
        second = pipeline.execute(data, params, filters=filters, sorting=sorting)

        assert first.items == second.items
        assert first.total == second.total

    def test_filter_before_sort(self) -> None:
        """Filter removes items before sort orders remaining."""
        pipeline = _build_pipeline()
        data = _make_dataset(100)
        filters = [FilterSpec(field="age", operator="lt", value=30)]
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]

        page = pipeline.execute(
            data,
            OffsetParams(page=1, limit=100),
            filters=filters,
            sorting=sorting,
        )

        assert all(item["age"] < 30 for item in page.items)
        ages = [item["age"] for item in page.items]
        assert ages == sorted(ages)


class TestPipelineDatasetSizes:
    """Parametrize over various dataset sizes."""

    @pytest.mark.parametrize(
        "count",
        [0, 1, 10, 100, 500],
        ids=["empty", "single", "small", "medium", "large"],
    )
    def test_pipeline_handles_dataset_size(self, count: int) -> None:
        """Pipeline works correctly for datasets of various sizes."""
        pipeline = _build_pipeline()
        data = _make_dataset(count)
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]

        page = pipeline.execute(
            data,
            OffsetParams(page=1, limit=20),
            sorting=sorting,
        )

        assert page.total == count
        assert len(page.items) == min(count, 20)


class TestLargePipelineFlow:
    """Pipeline with larger datasets."""

    def test_500_items_filter_sort_paginate(self) -> None:
        """500 items: filter + sort + paginate consistency."""
        pipeline = _build_pipeline()
        data = _make_dataset(500)
        filters = [FilterSpec(field="active", operator="eq", value=True)]
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            page = pipeline.execute(
                data,
                OffsetParams(page=page_num, limit=50),
                filters=filters,
                sorting=sorting,
            )
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        ages = [item["age"] for item in collected]
        assert ages == sorted(ages)
        assert all(item["active"] is True for item in collected)
