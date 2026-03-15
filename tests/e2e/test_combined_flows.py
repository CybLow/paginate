"""End-to-end tests for combined pipeline flows.

Verifies filter + sort + search + paginate working together
through the SyncPipeline orchestrator.
"""

from __future__ import annotations

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
    backend = MemoryBackend()
    paginator: Paginator[dict[str, object]] = Paginator(backend)
    return SyncPipeline(
        paginator,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
        search_backend=MemorySearchBackend(),
    )


class TestFilterSortPaginate:
    """Filter + sort + paginate pipeline."""

    def test_filter_sort_first_page(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Filter age>=25, sort name ASC, paginate page 1."""
        pipeline = _build_pipeline()
        filters = [FilterSpec(field="age", operator="gte", value=25)]
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]

        page = pipeline.execute(
            large_dataset,
            OffsetParams(page=1, limit=10),
            filters=filters,
            sorting=sorting,
        )

        assert all(item["age"] >= 25 for item in page.items)
        names = [item["name"] for item in page.items]
        assert names == sorted(names)

    def test_sorted_order_across_pages(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Sort order preserved when paginating across pages."""
        pipeline = _build_pipeline()
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            page = pipeline.execute(
                large_dataset,
                OffsetParams(page=page_num, limit=20),
                sorting=sorting,
            )
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        ages = [item["age"] for item in collected]
        assert ages == sorted(ages)


class TestSearchPaginate:
    """Search + paginate pipeline."""

    def test_search_then_paginate(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Search 'User_5' then paginate the results."""
        pipeline = _build_pipeline()
        search = SearchSpec(query="User_5", fields=("name",))

        page = pipeline.execute(
            large_dataset,
            OffsetParams(page=1, limit=50),
            search=search,
        )

        assert page.total > 0
        assert all("5" in str(item["name"]) for item in page.items)


class TestFullPipeline:
    """Filter + sort + search + paginate (all four)."""

    def test_full_pipeline_across_pages(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Full pipeline: filter + sort + search + paginate multi-page."""
        pipeline = _build_pipeline()
        filters = [FilterSpec(field="active", operator="eq", value=True)]
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
        search = SearchSpec(query="User_1", fields=("name",))
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            page = pipeline.execute(
                large_dataset,
                OffsetParams(page=page_num, limit=5),
                filters=filters,
                sorting=sorting,
                search=search,
            )
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        assert all(item["active"] is True for item in collected)
        names = [item["name"] for item in collected]
        assert names == sorted(names)

    def test_pipeline_no_specs_just_paginate(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Pipeline with no specs delegates to plain pagination."""
        pipeline = _build_pipeline()

        page = pipeline.execute(
            large_dataset,
            OffsetParams(page=1, limit=10),
        )

        assert len(page.items) == 10
        assert page.total == 100
