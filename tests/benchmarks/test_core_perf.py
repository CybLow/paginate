"""Performance benchmarks for core pagination components.

These tests measure the performance of PageParams and Page operations.
"""

from __future__ import annotations

import pytest

from pypaginate import Page, PageParams


pytestmark = pytest.mark.benchmark


class TestPageParamsBenchmarks:
    """Benchmark tests for PageParams creation and operations."""

    def test_pageparams_creation(self, benchmark) -> None:
        """Benchmark PageParams instantiation."""
        result = benchmark(PageParams, page=5, limit=20)
        assert result.page == 5
        assert result.limit == 20

    def test_pageparams_offset_calculation(self, benchmark) -> None:
        """Benchmark offset calculation."""
        params = PageParams(page=100, limit=50)

        result = benchmark(lambda: params.offset)

        assert result == 4950

    def test_pageparams_creation_batch(self, benchmark) -> None:
        """Benchmark creating many PageParams instances."""

        def create_many():
            return [PageParams(page=i, limit=20) for i in range(1, 101)]

        result = benchmark(create_many)
        assert len(result) == 100


class TestPageBenchmarks:
    """Benchmark tests for Page container operations."""

    @pytest.fixture
    def sample_items(self) -> list[int]:
        """Sample items for Page benchmarks."""
        return list(range(100))

    def test_page_creation(self, benchmark, sample_items: list[int]) -> None:
        """Benchmark Page instantiation."""
        result = benchmark(
            Page,
            items=sample_items,
            total=1000,
            page=1,
            limit=100,
        )
        assert len(result.items) == 100

    def test_page_pages_calculation(self, benchmark, sample_items: list[int]) -> None:
        """Benchmark pages calculation."""
        page = Page(items=sample_items, total=10000, page=1, limit=100)

        result = benchmark(lambda: page.pages)

        assert result == 100

    def test_page_has_next_check(self, benchmark, sample_items: list[int]) -> None:
        """Benchmark has_next property."""
        page = Page(items=sample_items, total=10000, page=50, limit=100)

        result = benchmark(lambda: page.has_next)

        assert result is True

    def test_page_has_previous_check(self, benchmark, sample_items: list[int]) -> None:
        """Benchmark has_previous property."""
        page = Page(items=sample_items, total=10000, page=50, limit=100)

        result = benchmark(lambda: page.has_previous)

        assert result is True

    def test_page_create_factory(self, benchmark, sample_items: list[int]) -> None:
        """Benchmark Page.create factory method."""
        params = PageParams(page=1, limit=100)

        result = benchmark(Page.create, sample_items, 1000, params)

        assert len(result.items) == 100

    def test_page_items_access(self, benchmark, sample_items: list[int]) -> None:
        """Benchmark items access."""
        page = Page(items=sample_items, total=1000, page=1, limit=100)

        result = benchmark(lambda: page.items)

        assert len(result) == 100

    def test_page_iteration(self, benchmark, sample_items: list[int]) -> None:
        """Benchmark iterating over page items."""
        page = Page(items=sample_items, total=1000, page=1, limit=100)

        def iterate():
            return list(page.items)

        result = benchmark(iterate)
        assert len(result) == 100
