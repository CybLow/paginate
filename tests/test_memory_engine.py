"""Tests for memory paginator engine."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pypaginate.core.pages import PageParams
from pypaginate.engines.memory import MemoryPaginator


@dataclass
class _PageItem:
    """Test item for pagination."""

    id: int
    name: str


class TestMemoryPaginator:
    """Test MemoryPaginator class."""

    @pytest.fixture
    def paginator(self) -> MemoryPaginator[_PageItem]:
        """Create paginator."""
        return MemoryPaginator()

    @pytest.fixture
    def items(self) -> list[_PageItem]:
        """Create test items."""
        return [
            _PageItem(id=1, name="apple"),
            _PageItem(id=2, name="banana"),
            _PageItem(id=3, name="cherry"),
            _PageItem(id=4, name="date"),
            _PageItem(id=5, name="elderberry"),
        ]

    def test_creation(self, paginator: MemoryPaginator[_PageItem]) -> None:
        """Should create paginator."""
        assert paginator is not None

    def test_first_page(
        self, paginator: MemoryPaginator[_PageItem], items: list[_PageItem]
    ) -> None:
        """Should return first page correctly."""
        params = PageParams(page=1, limit=2)
        page = paginator.paginate(items, params)
        assert len(page.items) == 2
        assert page.items[0].name == "apple"
        assert page.items[1].name == "banana"
        assert page.total == 5
        assert page.page == 1

    def test_second_page(
        self, paginator: MemoryPaginator[_PageItem], items: list[_PageItem]
    ) -> None:
        """Should return second page correctly."""
        params = PageParams(page=2, limit=2)
        page = paginator.paginate(items, params)
        assert len(page.items) == 2
        assert page.items[0].name == "cherry"
        assert page.items[1].name == "date"
        assert page.page == 2

    def test_last_page_partial(
        self, paginator: MemoryPaginator[_PageItem], items: list[_PageItem]
    ) -> None:
        """Should handle partial last page."""
        params = PageParams(page=3, limit=2)
        page = paginator.paginate(items, params)
        assert len(page.items) == 1
        assert page.items[0].name == "elderberry"

    def test_page_beyond_total(
        self, paginator: MemoryPaginator[_PageItem], items: list[_PageItem]
    ) -> None:
        """Should return empty for page beyond total."""
        params = PageParams(page=10, limit=2)
        page = paginator.paginate(items, params)
        assert len(page.items) == 0

    def test_single_large_page(
        self, paginator: MemoryPaginator[_PageItem], items: list[_PageItem]
    ) -> None:
        """Should handle large page size."""
        params = PageParams(page=1, limit=100)
        page = paginator.paginate(items, params)
        assert len(page.items) == 5
        assert page.total == 5

    def test_empty_collection(self, paginator: MemoryPaginator[_PageItem]) -> None:
        """Should handle empty collection."""
        params = PageParams(page=1, limit=10)
        page = paginator.paginate([], params)
        assert len(page.items) == 0
        assert page.total == 0

    def test_page_has_limit(
        self, paginator: MemoryPaginator[_PageItem], items: list[_PageItem]
    ) -> None:
        """Page should have limit from params."""
        params = PageParams(page=1, limit=2)
        page = paginator.paginate(items, params)
        assert page.limit == 2

    def test_total_reflects_entire_collection(
        self, paginator: MemoryPaginator[_PageItem], items: list[_PageItem]
    ) -> None:
        """Total should reflect entire collection."""
        params = PageParams(page=1, limit=1)
        page = paginator.paginate(items, params)
        assert page.total == 5
        assert len(page.items) == 1
