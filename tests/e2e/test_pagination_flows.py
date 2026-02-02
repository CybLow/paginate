"""End-to-end tests for complete pagination flows.

These tests verify that all components work together correctly
in realistic usage scenarios.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from pypaginate import PageParams
from pypaginate.core.context import PaginationContext
from pypaginate.engines.memory import MemoryPaginator
from pypaginate.engines.sql import SqlPaginator
from tests.conftest import User


pytestmark = pytest.mark.e2e


class TestMemoryPaginationFlow:
    """E2E tests for in-memory pagination."""

    def test_complete_pagination_through_all_pages(self) -> None:
        """Should be able to paginate through all pages of data."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = list(range(1, 101))  # 100 items
        limit = 10

        all_collected = []
        page_num = 1
        total_pages = 0

        while True:
            params = PageParams(page=page_num, limit=limit)
            result = paginator.paginate(items, params)

            if not result.items:
                break

            all_collected.extend(result.items)
            total_pages = result.pages
            page_num += 1

            if not result.has_next:
                break

        assert len(all_collected) == 100
        assert all_collected == items
        assert total_pages == 10

    def test_filtered_pagination_flow(self) -> None:
        """Should paginate filtered data correctly."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = list(range(1, 101))

        def is_multiple_of_five(x: int) -> bool:
            return x % 5 == 0

        limit = 5

        all_collected = []
        page_num = 1

        while True:
            params = PageParams(page=page_num, limit=limit)
            result = paginator.paginate(items, params, is_multiple_of_five)

            all_collected.extend(result.items)

            if not result.has_next:
                break
            page_num += 1

        expected = [x for x in items if x % 5 == 0]
        assert all_collected == expected
        assert len(all_collected) == 20

    def test_random_page_access(self) -> None:
        """Should be able to access any page directly."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = list(range(1000))
        limit = 50

        # Access pages in random order
        for page_num in [5, 1, 20, 10, 3]:
            params = PageParams(page=page_num, limit=limit)
            result = paginator.paginate(items, params)

            expected_start = (page_num - 1) * limit
            expected_items = list(range(expected_start, expected_start + limit))

            assert result.items == expected_items
            assert result.page == page_num

    def test_pagination_with_dict_items(self) -> None:
        """Should paginate complex dict items."""
        paginator: MemoryPaginator[dict] = MemoryPaginator()
        items = [{"id": i, "name": f"Item {i}", "active": i % 2 == 0} for i in range(100)]
        params = PageParams(page=3, limit=10)

        result = paginator.paginate(items, params)

        assert len(result.items) == 10
        assert result.items[0]["id"] == 20
        assert result.items[9]["id"] == 29


class TestSqlPaginationFlow:
    """E2E tests for SQL pagination with SQLAlchemy."""

    @pytest.mark.sqlalchemy
    @pytest.mark.integration
    async def test_complete_sql_pagination(self, populated_session) -> None:
        """Should paginate SQL results through all pages."""
        paginator: SqlPaginator[User] = SqlPaginator(populated_session, clamp=False)
        query = select(User).order_by(User.id)
        limit = 3

        all_users = []
        page_num = 1

        while True:
            params = PageParams(page=page_num, limit=limit)
            context = PaginationContext(
                params=params,
                clamp=False,
                unique=False,
                count_query=None,
            )

            snapshot = await paginator.paginate(query, context, scalars=True)

            all_users.extend(snapshot.items)

            # Compute has_next from snapshot data
            total_pages = (snapshot.total + limit - 1) // limit if limit > 0 else 0
            has_next = page_num < total_pages
            if not has_next:
                break
            page_num += 1

        assert len(all_users) == 10
        assert all_users[0].name == "Alice"
        assert all_users[-1].name == "Jack"

    @pytest.mark.sqlalchemy
    @pytest.mark.integration
    async def test_sql_pagination_empty_table(self, async_session) -> None:
        """Should handle empty table gracefully."""
        paginator: SqlPaginator[User] = SqlPaginator(async_session, clamp=False)
        query = select(User).order_by(User.id)
        params = PageParams(page=1, limit=10)
        context = PaginationContext(
            params=params,
            clamp=False,
            unique=False,
            count_query=None,
        )

        snapshot = await paginator.paginate(query, context, scalars=True)

        assert snapshot.items == []
        assert snapshot.total == 0
        # PaginationSnapshot doesn't have has_next/has_previous - compute from data
        total_pages = (snapshot.total + params.limit - 1) // params.limit if params.limit > 0 else 0
        has_next = snapshot.params.page < total_pages
        has_previous = snapshot.params.page > 1
        assert has_next is False
        assert has_previous is False


class TestPaginationMetadataFlow:
    """E2E tests for pagination metadata correctness."""

    def test_page_navigation_properties(self) -> None:
        """Should have correct navigation properties throughout."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = list(range(100))
        limit = 10

        # First page
        result = paginator.paginate(items, PageParams(page=1, limit=limit))
        assert result.has_previous is False
        assert result.has_next is True
        assert result.page == 1
        assert result.pages == 10

        # Middle page
        result = paginator.paginate(items, PageParams(page=5, limit=limit))
        assert result.has_previous is True
        assert result.has_next is True
        assert result.page == 5

        # Last page
        result = paginator.paginate(items, PageParams(page=10, limit=limit))
        assert result.has_previous is True
        assert result.has_next is False
        assert result.page == 10

    def test_pages_calculation_edge_cases(self) -> None:
        """Should calculate pages correctly for various totals."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        limit = 10

        # Exact multiple
        result = paginator.paginate(list(range(100)), PageParams(page=1, limit=limit))
        assert result.pages == 10

        # Just over multiple
        result = paginator.paginate(list(range(101)), PageParams(page=1, limit=limit))
        assert result.pages == 11

        # Just under multiple
        result = paginator.paginate(list(range(99)), PageParams(page=1, limit=limit))
        assert result.pages == 10

        # Single item
        result = paginator.paginate([1], PageParams(page=1, limit=limit))
        assert result.pages == 1

        # Empty
        result = paginator.paginate([], PageParams(page=1, limit=limit))
        assert result.pages == 0  # 0 pages when empty


class TestIntegrationScenarios:
    """Real-world integration scenarios."""

    def test_api_style_pagination_response(self) -> None:
        """Should produce API-style pagination response."""
        paginator: MemoryPaginator[dict] = MemoryPaginator()
        items = [{"id": i, "title": f"Article {i}", "published": i < 50} for i in range(100)]
        params = PageParams(page=2, limit=20)

        result = paginator.paginate(items, params)

        # Simulate API response structure
        api_response = {
            "data": result.items,
            "meta": {
                "total": result.total,
                "page": result.page,
                "limit": result.limit,
                "pages": result.pages,
                "has_next": result.has_next,
                "has_previous": result.has_previous,
            },
        }

        assert api_response["meta"]["total"] == 100
        assert api_response["meta"]["page"] == 2
        assert api_response["meta"]["pages"] == 5
        assert len(api_response["data"]) == 20
        assert api_response["data"][0]["id"] == 20

    def test_infinite_scroll_simulation(self) -> None:
        """Should support infinite scroll pattern."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = list(range(1000))
        limit = 50

        visible_items: list[int] = []
        page = 1

        # Simulate user scrolling through 5 "screens"
        for _ in range(5):
            params = PageParams(page=page, limit=limit)
            result = paginator.paginate(items, params)
            visible_items.extend(result.items)
            page += 1

        assert len(visible_items) == 250
        assert visible_items == list(range(250))
