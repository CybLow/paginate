"""Integration tests for memory backends satisfying protocols.

Verifies that each backend implements its protocol and that
chaining backends manually produces correct results.
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
from pypaginate.domain.protocols import (
    FilterBackend,
    SearchBackend,
    SortBackend,
    SyncPaginationBackend,
)


class TestProtocolSatisfaction:
    """Each backend satisfies its runtime-checkable protocol."""

    def test_memory_backend_satisfies_sync_protocol(self) -> None:
        """MemoryBackend is a SyncPaginationBackend."""
        backend = MemoryBackend()

        assert isinstance(backend, SyncPaginationBackend)

    def test_filter_backend_satisfies_protocol(self) -> None:
        """MemoryFilterBackend is a FilterBackend."""
        backend = MemoryFilterBackend()

        assert isinstance(backend, FilterBackend)

    def test_sort_backend_satisfies_protocol(self) -> None:
        """MemorySortBackend is a SortBackend."""
        backend = MemorySortBackend()

        assert isinstance(backend, SortBackend)

    def test_search_backend_satisfies_protocol(self) -> None:
        """MemorySearchBackend is a SearchBackend."""
        backend = MemorySearchBackend()

        assert isinstance(backend, SearchBackend)


class TestFilterBackendResults:
    """MemoryFilterBackend returns filtered sequences."""

    def test_apply_filters_returns_matching(
        self,
        sample_users: list[dict[str, object]],
    ) -> None:
        """Filtered result contains only matching items."""
        backend = MemoryFilterBackend()
        filters = [FilterSpec(field="age", operator="gte", value=30)]

        result = backend.apply_filters(sample_users, filters)

        assert all(item["age"] >= 30 for item in result)

    def test_apply_filters_empty_on_no_match(
        self,
        sample_users: list[dict[str, object]],
    ) -> None:
        """No matches returns empty list."""
        backend = MemoryFilterBackend()
        filters = [FilterSpec(field="age", operator="gt", value=999)]

        result = backend.apply_filters(sample_users, filters)

        assert result == []


class TestSortBackendResults:
    """MemorySortBackend returns sorted sequences."""

    def test_apply_sorting_ascending(
        self,
        sample_users: list[dict[str, object]],
    ) -> None:
        """Ascending sort orders items correctly."""
        backend = MemorySortBackend()
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]

        result = backend.apply_sorting(sample_users, sorting)

        ages = [item["age"] for item in result]
        assert ages == sorted(ages)

    def test_apply_sorting_descending(
        self,
        sample_users: list[dict[str, object]],
    ) -> None:
        """Descending sort orders items correctly."""
        backend = MemorySortBackend()
        sorting = [SortSpec(field="age", direction=SortDirection.DESC)]

        result = backend.apply_sorting(sample_users, sorting)

        ages = [item["age"] for item in result]
        assert ages == sorted(ages, reverse=True)


class TestSearchBackendResults:
    """MemorySearchBackend returns matching items."""

    def test_apply_search_finds_match(
        self,
        sample_users: list[dict[str, object]],
    ) -> None:
        """Search finds items containing the query."""
        backend = MemorySearchBackend()
        spec = SearchSpec(query="user_0", fields=("name",))

        result = backend.apply_search(sample_users, spec)

        assert len(result) >= 1


class TestManualChaining:
    """Chain backends manually: filter -> sort -> paginate."""

    def test_filter_sort_paginate_chain(
        self,
        sample_users: list[dict[str, object]],
    ) -> None:
        """Manual chaining produces correct filtered+sorted page."""
        filters = [FilterSpec(field="age", operator="gte", value=28)]
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        params = OffsetParams(page=1, limit=10)

        filtered = MemoryFilterBackend().apply_filters(sample_users, filters)
        sorted_data = MemorySortBackend().apply_sorting(filtered, sorting)
        from pypaginate.engine.paginator import Paginator

        page = Paginator(MemoryBackend()).paginate(sorted_data, params)

        assert all(item["age"] >= 28 for item in page.items)
        ages = [item["age"] for item in page.items]
        assert ages == sorted(ages)
        assert page.total == len(sorted_data)
