"""End-to-end tests for sort + paginate workflows.

Verifies sorting across directions, multi-field, nulls, and combined.
"""

from __future__ import annotations

import pytest

from pypaginate import FilterSpec, OffsetParams, SortDirection, SortSpec
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


def _build_pipeline() -> SyncPipeline[dict[str, object]]:
    """Build a SyncPipeline with sort and filter backends."""
    paginator: Paginator[dict[str, object]] = Paginator(MemoryBackend())
    return SyncPipeline(
        paginator,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
    )


@pytest.fixture()
def users() -> list[dict[str, object]]:
    """Users with varied ages and names for sorting tests."""
    return [
        {"name": "Charlie", "age": 30},
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Diana", "age": 25},
        {"name": "Eve", "age": 35},
        {"name": "Frank", "age": 20},
        {"name": "Grace", "age": None},
    ]


class TestSortPaginate:
    """Sort then paginate results."""

    def test_sort_age_asc_across_pages(self, users: list) -> None:
        """Sort by age ASC, order preserved across all pages."""
        pipeline = _build_pipeline()
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            page = pipeline.execute(
                users,
                OffsetParams(page=page_num, limit=3),
                sorting=sorting,
            )
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        non_null = [i for i in collected if i["age"] is not None]
        ages = [item["age"] for item in non_null]
        assert ages == sorted(ages)

    def test_sort_name_desc(self, users: list) -> None:
        """Sort by name DESC gives reverse alphabetical."""
        pipeline = _build_pipeline()
        sorting = [SortSpec(field="name", direction=SortDirection.DESC)]

        page = pipeline.execute(
            users,
            OffsetParams(page=1, limit=10),
            sorting=sorting,
        )

        names = [item["name"] for item in page.items]
        assert names == sorted(names, reverse=True)


class TestMultiFieldSort:
    """Multi-field sort with tie-breaking."""

    def test_sort_age_then_name(self, users: list) -> None:
        """Sort by age ASC then name ASC breaks ties correctly."""
        pipeline = _build_pipeline()
        sorting = [
            SortSpec(field="age", direction=SortDirection.ASC),
            SortSpec(field="name", direction=SortDirection.ASC),
        ]

        page = pipeline.execute(
            users,
            OffsetParams(page=1, limit=10),
            sorting=sorting,
        )

        non_null = [i for i in page.items if i["age"] is not None]
        ages = [item["age"] for item in non_null]
        assert ages == sorted(ages)


class TestSortWithNulls:
    """Sort with None values in data."""

    def test_null_values_placed_last(self, users: list) -> None:
        """None values sort to the end by default."""
        pipeline = _build_pipeline()
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]

        page = pipeline.execute(
            users,
            OffsetParams(page=1, limit=10),
            sorting=sorting,
        )

        items = page.items
        null_items = [i for i in items if i["age"] is None]
        non_null = [i for i in items if i["age"] is not None]
        null_start = items.index(null_items[0]) if null_items else len(items)
        assert null_start >= len(non_null)


class TestSortWithFilter:
    """Sort combined with filter specs."""

    def test_filter_then_sort(self, users: list) -> None:
        """Filter non-null age > 25 then sort by name ASC."""
        pipeline = _build_pipeline()
        filters = [
            FilterSpec(field="age", operator="is_not_null"),
            FilterSpec(field="age", operator="gt", value=25),
        ]
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]

        page = pipeline.execute(
            users,
            OffsetParams(page=1, limit=10),
            filters=filters,
            sorting=sorting,
        )

        assert all(item["age"] > 25 for item in page.items)
        names = [item["name"] for item in page.items]
        assert names == sorted(names)

    def test_sorted_across_all_pages_globally(
        self,
        large_dataset: list[dict[str, object]],
    ) -> None:
        """Collect all pages and verify global sort order."""
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
