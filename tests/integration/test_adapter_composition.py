"""Integration tests for adapter composition.

Verifies adapters chain correctly: filter -> sort -> search -> paginate.
Manual chaining must match Pipeline.execute output.
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


def _sample_data() -> list[dict[str, object]]:
    """Eight users with varied attributes."""
    return [
        {"name": "Alice", "age": 30, "email": "alice@test.com"},
        {"name": "Bob", "age": 25, "email": "bob@test.com"},
        {"name": "Charlie", "age": 35, "email": "charlie@test.com"},
        {"name": "Diana", "age": 28, "email": "diana@test.com"},
        {"name": "Eve", "age": 22, "email": "eve@test.com"},
        {"name": "Frank", "age": 40, "email": "frank@test.com"},
        {"name": "Grace", "age": 33, "email": "grace@test.com"},
        {"name": "Hank", "age": 27, "email": "hank@test.com"},
    ]


class TestFilterToSort:
    """MemoryFilterBackend output feeds into MemorySortBackend."""

    def test_filter_output_sortable(self) -> None:
        """Filtered list is accepted by sort backend."""
        data = _sample_data()
        filters = [FilterSpec(field="age", operator="gte", value=28)]

        filtered = MemoryFilterBackend().apply_filters(data, filters)
        sorted_data = MemorySortBackend().apply_sorting(
            filtered,
            [SortSpec(field="age", direction=SortDirection.ASC)],
        )

        ages = [item["age"] for item in sorted_data]
        assert ages == sorted(ages)
        assert all(item["age"] >= 28 for item in sorted_data)

    def test_sort_output_searchable(self) -> None:
        """Sorted list is accepted by search backend."""
        data = _sample_data()
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]

        sorted_data = MemorySortBackend().apply_sorting(data, sorting)
        search_result = MemorySearchBackend().apply_search(
            sorted_data,
            SearchSpec(query="alice", fields=("name",)),
        )

        assert len(search_result) >= 1


class TestFullManualChain:
    """Full chain: filter -> sort -> search -> paginate (no Pipeline)."""

    def test_manual_chain_produces_correct_page(self) -> None:
        """Manual adapter chaining produces valid OffsetPage."""
        data = _sample_data()
        filters = [FilterSpec(field="age", operator="gte", value=25)]
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
        search = SearchSpec(query="a", fields=("name", "email"))
        params = OffsetParams(page=1, limit=10)

        filtered = MemoryFilterBackend().apply_filters(data, filters)
        sorted_data = MemorySortBackend().apply_sorting(filtered, sorting)
        searched = MemorySearchBackend().apply_search(sorted_data, search)
        page = Paginator(MemoryBackend()).paginate(searched, params)

        assert page.total == len(searched)
        assert all(item["age"] >= 25 for item in page.items)


class TestPipelineEquivalence:
    """Pipeline output matches manual chaining."""

    def test_pipeline_equals_manual_chain(self) -> None:
        """SyncPipeline gives same result as manual adapter chain."""
        data = _sample_data()
        filters = [FilterSpec(field="age", operator="gte", value=25)]
        sorting = [SortSpec(field="name", direction=SortDirection.ASC)]
        params = OffsetParams(page=1, limit=10)

        filtered = MemoryFilterBackend().apply_filters(data, filters)
        sorted_data = MemorySortBackend().apply_sorting(filtered, sorting)
        manual = Paginator(MemoryBackend()).paginate(sorted_data, params)

        pipeline = SyncPipeline(
            Paginator(MemoryBackend()),
            filter_backend=MemoryFilterBackend(),
            sort_backend=MemorySortBackend(),
        )
        piped = pipeline.execute(
            data,
            params,
            filters=filters,
            sorting=sorting,
        )

        assert manual.items == piped.items
        assert manual.total == piped.total


class TestTypeConsistency:
    """Each adapter returns a type the next can consume."""

    def test_chain_returns_list_types(self) -> None:
        """Each adapter step returns a list-like Sequence."""
        data = _sample_data()
        filtered = MemoryFilterBackend().apply_filters(data, [])
        sorted_data = MemorySortBackend().apply_sorting(filtered, [])
        searched = MemorySearchBackend().apply_search(
            sorted_data,
            SearchSpec(
                query="",
                fields=("name",),
            ),
        )

        assert isinstance(filtered, list)
        assert isinstance(sorted_data, list)
        assert isinstance(searched, list)
