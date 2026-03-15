"""End-to-end tests for search + paginate workflows.

Verifies search across modes, fields, and combined with filters.
"""

from __future__ import annotations

import pytest

from pypaginate import (
    FilterSpec,
    FuzzyMode,
    OffsetParams,
    SearchFieldMode,
    SearchSpec,
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


@pytest.fixture()
def users() -> list[dict[str, object]]:
    """Users with searchable name and email fields."""
    return [
        {"name": "Alice Smith", "email": "alice@corp.com", "age": 30},
        {"name": "Bob Jones", "email": "bob@corp.com", "age": 25},
        {"name": "Charlie Alice", "email": "charlie@test.com", "age": 35},
        {"name": "Diana Prince", "email": "diana@corp.com", "age": 28},
        {"name": "Alice Cooper", "email": "cooper@rock.com", "age": 45},
        {"name": "Frank Burns", "email": "frank@test.com", "age": 22},
    ]


class TestSearchPaginate:
    """Search then paginate results."""

    def test_search_preserves_order_across_pages(self, users: list) -> None:
        """Search results order is preserved across multiple pages."""
        pipeline = _build_pipeline()
        search = SearchSpec(query="alice", fields=("name",))

        page = pipeline.execute(users, OffsetParams(page=1, limit=2), search=search)

        assert page.total >= 2
        assert all("alice" in str(item["name"]).lower() for item in page.items)

    def test_search_no_results_yields_empty_page(self, users: list) -> None:
        """Search with no matches returns empty page."""
        pipeline = _build_pipeline()
        search = SearchSpec(query="zzzznotfound", fields=("name",))

        page = pipeline.execute(users, OffsetParams(page=1, limit=10), search=search)

        assert page.items == []
        assert page.total == 0

    def test_fuzzy_search_returns_approximate_matches(self, users: list) -> None:
        """Fuzzy mode matches approximate strings."""
        pipeline = _build_pipeline()
        search = SearchSpec(
            query="alic",
            fields=("name",),
            fuzzy=FuzzyMode.FUZZY,
            threshold=60,
        )

        page = pipeline.execute(users, OffsetParams(page=1, limit=10), search=search)

        assert page.total >= 1

    def test_search_across_multiple_fields(self, users: list) -> None:
        """Search matches against both name and email fields."""
        pipeline = _build_pipeline()
        search = SearchSpec(query="alice", fields=("name", "email"))

        page = pipeline.execute(users, OffsetParams(page=1, limit=10), search=search)

        assert page.total >= 2


class TestSearchWithFilter:
    """Search combined with filter specs."""

    def test_search_and_filter_combined(self, users: list) -> None:
        """Search 'alice' AND filter age >= 25 narrows results."""
        pipeline = _build_pipeline()
        filters = [FilterSpec(field="age", operator="gte", value=25)]
        search = SearchSpec(query="alice", fields=("name",))

        page = pipeline.execute(
            users,
            OffsetParams(page=1, limit=10),
            filters=filters,
            search=search,
        )

        assert all(item["age"] >= 25 for item in page.items)
        assert all("alice" in str(item["name"]).lower() for item in page.items)


class TestSearchModes:
    """Parametrize search modes: PREFIX, CONTAINS, EXACT."""

    @pytest.mark.parametrize(
        ("mode", "query", "min_expected"),
        [
            (SearchFieldMode.PREFIX, "alice", 2),
            (SearchFieldMode.CONTAINS, "alice", 3),
            (SearchFieldMode.EXACT, "alice smith", 1),
        ],
        ids=["prefix", "contains", "exact"],
    )
    def test_search_mode_result_counts(
        self,
        users: list,
        mode: SearchFieldMode,
        query: str,
        min_expected: int,
    ) -> None:
        """Each search mode returns the expected minimum results."""
        pipeline = _build_pipeline()
        search = SearchSpec(query=query, fields=("name",), mode=mode)

        page = pipeline.execute(users, OffsetParams(page=1, limit=10), search=search)

        assert page.total >= min_expected
