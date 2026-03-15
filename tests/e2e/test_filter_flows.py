"""End-to-end tests for filter + paginate workflows.

Verifies FilterSpec-based filtering followed by offset pagination.
"""

from __future__ import annotations

from pypaginate import FilterSpec, OffsetParams, OverflowStrategy, paginate
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


def _filter_and_paginate(
    data: list[dict[str, object]],
    filters: list[FilterSpec],
    page: int = 1,
    limit: int = 10,
) -> object:
    """Helper: filter then paginate via SyncPipeline."""
    backend = MemoryBackend()
    paginator: Paginator[dict[str, object]] = Paginator(backend)
    pipeline: SyncPipeline[dict[str, object]] = SyncPipeline(
        paginator,
        filter_backend=MemoryFilterBackend(),
    )
    return pipeline.execute(
        data,
        OffsetParams(page=page, limit=limit),
        filters=filters,
    )


class TestFilterThenPaginate:
    """Filter data and paginate through results."""

    def test_age_filter_paginates_all(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Filter age >= 30 then collect all pages."""
        filters = [FilterSpec(field="age", operator="gte", value=30)]
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            result = _filter_and_paginate(large_dataset, filters, page=page_num, limit=10)
            collected.extend(result.items)
            if not result.has_next:
                break
            page_num += 1

        assert all(item["age"] >= 30 for item in collected)
        assert len(collected) > 0

    def test_multiple_filters(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """age >= 25 AND name starts_with 'User_1' narrows results."""
        filters = [
            FilterSpec(field="age", operator="gte", value=25),
            FilterSpec(field="name", operator="starts_with", value="User_1"),
        ]

        result = _filter_and_paginate(large_dataset, filters, limit=100)

        assert all(item["age"] >= 25 for item in result.items)
        assert all(item["name"].startswith("User_1") for item in result.items)


class TestFilterEdgeCases:
    """Edge cases for filter flows."""

    def test_filter_matches_nothing(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Filter with no matches yields empty page."""
        filters = [FilterSpec(field="age", operator="gt", value=999)]

        result = _filter_and_paginate(large_dataset, filters)

        assert result.items == []
        assert result.total == 0

    def test_filter_with_overflow_clamp(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """CLAMP overflow on filtered data returns last page."""
        filters = [FilterSpec(field="active", operator="eq", value=True)]
        filter_backend = MemoryFilterBackend()
        filtered = filter_backend.apply_filters(large_dataset, filters)

        page = paginate(
            filtered,
            OffsetParams(page=999, limit=10),
            overflow=OverflowStrategy.CLAMP,
        )

        assert len(page.items) > 0
