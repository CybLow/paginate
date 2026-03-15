"""Integration tests for SyncPipeline with memory backends.

Verifies cross-module wiring of filter, sort, search, and paginate.
"""

from __future__ import annotations

from pypaginate import (
    FilterSpec,
    OffsetParams,
    SearchSpec,
    SortDirection,
    SortSpec,
)
from pypaginate.engine.pipeline import SyncPipeline


class TestPipelineFilterPaginate:
    """Pipeline: filter + paginate."""

    def test_filter_active_then_paginate(
        self,
        memory_pipeline: SyncPipeline[dict[str, object]],
        sample_users: list[dict[str, object]],
    ) -> None:
        """Filter active users then paginate result."""
        filters = [FilterSpec(field="age", operator="gte", value=28)]

        page = memory_pipeline.execute(
            sample_users,
            OffsetParams(page=1, limit=10),
            filters=filters,
        )

        assert all(item["age"] >= 28 for item in page.items)
        assert page.total == len(page.items)


class TestPipelineSortPaginate:
    """Pipeline: sort + paginate."""

    def test_sort_by_age_asc(
        self,
        memory_pipeline: SyncPipeline[dict[str, object]],
        sample_users: list[dict[str, object]],
    ) -> None:
        """Sort users by age ascending then paginate."""
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]

        page = memory_pipeline.execute(
            sample_users,
            OffsetParams(page=1, limit=10),
            sorting=sorting,
        )

        ages = [item["age"] for item in page.items]
        assert ages == sorted(ages)


class TestPipelineSearchPaginate:
    """Pipeline: search + paginate."""

    def test_search_name_then_paginate(
        self,
        memory_pipeline: SyncPipeline[dict[str, object]],
        sample_users: list[dict[str, object]],
    ) -> None:
        """Search for 'user_0' then paginate results."""
        search = SearchSpec(query="user_0", fields=("name",))

        page = memory_pipeline.execute(
            sample_users,
            OffsetParams(page=1, limit=10),
            search=search,
        )

        assert page.total >= 1
        assert any("User_0" in str(item["name"]) for item in page.items)


class TestPipelineFullSpecs:
    """Pipeline: filter + sort + search + paginate."""

    def test_all_specs_combined(
        self,
        memory_pipeline: SyncPipeline[dict[str, object]],
        sample_users: list[dict[str, object]],
    ) -> None:
        """All specs applied together produce correct result."""
        filters = [FilterSpec(field="age", operator="gte", value=25)]
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
        search = SearchSpec(query="user", fields=("name", "email"))

        page = memory_pipeline.execute(
            sample_users,
            OffsetParams(page=1, limit=10),
            filters=filters,
            sorting=sorting,
            search=search,
        )

        assert all(item["age"] >= 25 for item in page.items)
        names = [item["name"] for item in page.items]
        assert names == sorted(names)


class TestPipelineNoSpecs:
    """Pipeline with no filter/sort/search."""

    def test_plain_paginate(
        self,
        memory_pipeline: SyncPipeline[dict[str, object]],
        sample_users: list[dict[str, object]],
    ) -> None:
        """No specs just paginates the raw data."""
        page = memory_pipeline.execute(
            sample_users,
            OffsetParams(page=1, limit=2),
        )

        assert len(page.items) == 2
        assert page.total == len(sample_users)


class TestPipelineMatchesManual:
    """Pipeline results match manual filter-sort-paginate."""

    def test_pipeline_equals_manual(
        self,
        memory_pipeline: SyncPipeline[dict[str, object]],
        sample_users: list[dict[str, object]],
    ) -> None:
        """Pipeline output matches manual stepwise application."""
        from pypaginate.adapters.memory.backend import MemoryBackend
        from pypaginate.adapters.memory.filters import MemoryFilterBackend
        from pypaginate.adapters.memory.sorting import MemorySortBackend
        from pypaginate.engine.paginator import Paginator

        filters = [FilterSpec(field="age", operator="gte", value=28)]
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        params = OffsetParams(page=1, limit=10)

        pipeline_page = memory_pipeline.execute(
            sample_users,
            params,
            filters=filters,
            sorting=sorting,
        )

        filtered = MemoryFilterBackend().apply_filters(sample_users, filters)
        sorted_data = MemorySortBackend().apply_sorting(filtered, sorting)
        manual_page = Paginator(MemoryBackend()).paginate(sorted_data, params)

        assert pipeline_page.items == manual_page.items
        assert pipeline_page.total == manual_page.total
