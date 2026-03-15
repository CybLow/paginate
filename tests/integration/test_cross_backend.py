"""Cross-backend consistency tests — ONE test, TWO backends.

Every test runs twice: once with memory backends and once with
SQLAlchemy + SQLite. If results diverge, the test fails.
"""

from __future__ import annotations

from typing import Any

from pypaginate import OffsetParams, SortDirection
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec
from pypaginate.engine.paginator import AsyncPaginator, Paginator


# -- Helpers -----------------------------------------------------------------


async def _count(mode: str, backend: Any, query: Any) -> int:
    """Count items via sync or async backend."""
    if mode == "sync":
        return backend.count(query)
    return await backend.count(query)


async def _fetch(mode: str, backend: Any, query: Any, offset: int, limit: int) -> list[Any]:
    """Fetch items via sync or async backend."""
    if mode == "sync":
        return backend.fetch(query, offset, limit)
    return await backend.fetch(query, offset, limit)


async def _paginate(mode: str, backend: Any, query: Any, params: OffsetParams) -> Any:
    """Run paginator on either backend."""
    if mode == "sync":
        return Paginator(backend).paginate(query, params)
    return await AsyncPaginator(backend).paginate(query, params)


# -- Pagination tests --------------------------------------------------------


class TestCountMatches:
    """Both backends report the same total count."""

    async def test_count_matches(self, pagination_env: tuple) -> None:
        """Count returns 8 on both backends."""
        mode, backend, query, expected = pagination_env

        total = await _count(mode, backend, query)

        assert total == expected


class TestFetchPageMatches:
    """Both backends return same item count for a page slice."""

    async def test_fetch_page_matches(self, pagination_env: tuple) -> None:
        """Fetch offset=0 limit=3 returns 3 items on both."""
        mode, backend, query, _total = pagination_env

        items = await _fetch(mode, backend, query, offset=0, limit=3)

        assert len(items) == 3


class TestPaginationAllPages:
    """Iterate all pages on both backends, verify same total."""

    async def test_all_pages_collect_all_items(self, pagination_env: tuple) -> None:
        """Iterating pages collects exactly 8 items on both."""
        mode, backend, query, expected = pagination_env
        collected: list[Any] = []
        page_num = 1

        while True:
            page = await _paginate(mode, backend, query, OffsetParams(page=page_num, limit=3))
            collected.extend(page.items)
            if not page.has_next:
                break
            page_num += 1

        assert len(collected) == expected


# -- Filter tests ------------------------------------------------------------


class TestFilterEqMatches:
    """Both backends filter eq on name correctly."""

    async def test_filter_eq_name(self, full_env: dict) -> None:
        """Filter name='Alice' returns 1 item on both."""
        mode = full_env["mode"]
        spec = FilterSpec(field="name", operator="eq", value="Alice")
        filtered = full_env["filter"].apply_filters(full_env["query"], [spec])

        total = await _count(mode, full_env["pagination"], filtered)

        assert total == 1


class TestFilterGteMatches:
    """Both backends filter gte on id correctly."""

    async def test_filter_gte_id(self, full_env: dict) -> None:
        """Filter id >= 5 returns 4 items on both."""
        mode = full_env["mode"]
        spec = FilterSpec(field="id", operator="gte", value=5)
        filtered = full_env["filter"].apply_filters(full_env["query"], [spec])

        total = await _count(mode, full_env["pagination"], filtered)

        assert total == 4


# -- Sort tests --------------------------------------------------------------


class TestSortOrderMatches:
    """Both backends sort by name ASC in the same order."""

    async def test_sort_name_asc(self, full_env: dict) -> None:
        """Sort by name ASC yields alphabetical order on both."""
        mode = full_env["mode"]
        spec = SortSpec(field="name", direction=SortDirection.ASC)
        sorted_q = full_env["sort"].apply_sorting(full_env["query"], [spec])

        items = await _fetch(mode, full_env["pagination"], sorted_q, 0, 8)
        names = [_get_name(item) for item in items]

        assert names == sorted(names)


# -- Combined tests ----------------------------------------------------------


class TestFilterThenPaginate:
    """Filter + paginate yields consistent results on both."""

    async def test_filter_then_paginate(self, full_env: dict) -> None:
        """Filter id >= 3 then paginate page 1 limit 3."""
        mode = full_env["mode"]
        spec = FilterSpec(field="id", operator="gte", value=3)
        filtered = full_env["filter"].apply_filters(full_env["query"], [spec])

        page = await _paginate(
            mode, full_env["pagination"], filtered, OffsetParams(page=1, limit=3)
        )

        assert page.total == 6
        assert len(page.items) == 3


class TestSearchMatches:
    """Search on name field matches on both backends."""

    async def test_search_contains_alice(self, full_env: dict) -> None:
        """Search 'alice' in name returns at least 1 on both."""
        spec = SearchSpec(query="alice", fields=("name",))
        searched = full_env["search"].apply_search(full_env["query"], spec)

        total = await _count(full_env["mode"], full_env["pagination"], searched)

        assert total >= 1


# -- Helpers for extracting fields from dict or ORM --------------------------


def _get_name(item: Any) -> str:
    """Extract name from dict or ORM model."""
    if isinstance(item, dict):
        return str(item["name"])
    return str(item.name)
