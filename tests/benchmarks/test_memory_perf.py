"""Performance benchmarks for memory pagination.

These tests use pytest-benchmark to measure and track performance
of memory-based pagination operations.
"""

from __future__ import annotations

import pytest

from pypaginate import PageParams
from pypaginate.engines.memory import MemoryPaginator, filter_iter, compute_bounds, collect_window


pytestmark = pytest.mark.benchmark


class TestMemoryPaginatorBenchmarks:
    """Benchmark tests for MemoryPaginator performance."""

    @pytest.fixture
    def small_dataset(self) -> list[int]:
        """Small dataset (1,000 items) for quick benchmarks."""
        return list(range(1_000))

    @pytest.fixture
    def medium_dataset(self) -> list[int]:
        """Medium dataset (10,000 items) for standard benchmarks."""
        return list(range(10_000))

    @pytest.fixture
    def large_dataset(self) -> list[int]:
        """Large dataset (100,000 items) for stress testing."""
        return list(range(100_000))

    def test_paginate_small_sequence_first_page(
        self,
        benchmark,
        small_dataset: list[int],
    ) -> None:
        """Benchmark pagination of small sequence - first page."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        params = PageParams(page=1, limit=20)

        result = benchmark(paginator.paginate, small_dataset, params)

        assert len(result.items) == 20
        assert result.total == 1_000

    def test_paginate_small_sequence_middle_page(
        self,
        benchmark,
        small_dataset: list[int],
    ) -> None:
        """Benchmark pagination of small sequence - middle page."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        params = PageParams(page=25, limit=20)  # Middle of 50 pages

        result = benchmark(paginator.paginate, small_dataset, params)

        assert len(result.items) == 20

    def test_paginate_medium_sequence_first_page(
        self,
        benchmark,
        medium_dataset: list[int],
    ) -> None:
        """Benchmark pagination of medium sequence - first page."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        params = PageParams(page=1, limit=50)

        result = benchmark(paginator.paginate, medium_dataset, params)

        assert len(result.items) == 50
        assert result.total == 10_000

    def test_paginate_large_sequence_first_page(
        self,
        benchmark,
        large_dataset: list[int],
    ) -> None:
        """Benchmark pagination of large sequence - first page."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        params = PageParams(page=1, limit=100)

        result = benchmark(paginator.paginate, large_dataset, params)

        assert len(result.items) == 100
        assert result.total == 100_000

    def test_paginate_large_sequence_late_page(
        self,
        benchmark,
        large_dataset: list[int],
    ) -> None:
        """Benchmark pagination of large sequence - late page (page 900)."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        params = PageParams(page=900, limit=100)

        result = benchmark(paginator.paginate, large_dataset, params)

        assert len(result.items) == 100

    def test_paginate_with_simple_predicate(
        self,
        benchmark,
        medium_dataset: list[int],
    ) -> None:
        """Benchmark pagination with a simple filter predicate."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        params = PageParams(page=1, limit=50)
        predicate = lambda x: x % 2 == 0  # Even numbers only

        result = benchmark(paginator.paginate, medium_dataset, params, predicate)

        assert len(result.items) == 50
        assert all(x % 2 == 0 for x in result.items)

    def test_paginate_with_complex_predicate(
        self,
        benchmark,
        medium_dataset: list[int],
    ) -> None:
        """Benchmark pagination with a more complex filter predicate."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        params = PageParams(page=1, limit=50)
        # More complex condition
        predicate = lambda x: x % 3 == 0 and x > 1000 and x < 8000

        result = benchmark(paginator.paginate, medium_dataset, params, predicate)

        assert all(predicate(x) for x in result.items)


class TestFilterIterBenchmarks:
    """Benchmark tests for filter_iter function."""

    @pytest.fixture
    def items(self) -> list[int]:
        """Dataset for filter benchmarks."""
        return list(range(10_000))

    def test_filter_iter_no_predicate(self, benchmark, items: list[int]) -> None:
        """Benchmark filter_iter with no predicate (pass-through)."""
        def run():
            return list(filter_iter(items, None))

        result = benchmark(run)
        assert len(result) == 10_000

    def test_filter_iter_simple_predicate(self, benchmark, items: list[int]) -> None:
        """Benchmark filter_iter with simple predicate."""
        predicate = lambda x: x % 2 == 0

        def run():
            return list(filter_iter(items, predicate))

        result = benchmark(run)
        assert len(result) == 5_000

    def test_filter_iter_complex_predicate(self, benchmark, items: list[int]) -> None:
        """Benchmark filter_iter with complex predicate."""
        predicate = lambda x: x % 7 == 0 and x > 100

        def run():
            return list(filter_iter(items, predicate))

        result = benchmark(run)
        assert all(predicate(x) for x in result)


class TestComputeBoundsBenchmarks:
    """Benchmark tests for compute_bounds function."""

    def test_compute_bounds_first_page(self, benchmark) -> None:
        """Benchmark compute_bounds for first page."""
        params = PageParams(page=1, limit=50)

        result = benchmark(compute_bounds, params)

        assert result.start == 0
        assert result.end == 50

    def test_compute_bounds_large_offset(self, benchmark) -> None:
        """Benchmark compute_bounds with large page number."""
        params = PageParams(page=10000, limit=100)

        result = benchmark(compute_bounds, params)

        assert result.start == 999_900
        assert result.end == 1_000_000


class TestCollectWindowBenchmarks:
    """Benchmark tests for collect_window function."""

    def test_collect_window_small(self, benchmark) -> None:
        """Benchmark collect_window for small window."""
        items = iter(range(1000))
        params = PageParams(page=1, limit=20)
        bounds = compute_bounds(params)

        def run():
            return collect_window(iter(range(1000)), bounds)

        result, total = benchmark(run)
        assert len(result) == 20
        assert total == 1000

    def test_collect_window_late_page(self, benchmark) -> None:
        """Benchmark collect_window for late page (requires iteration)."""
        params = PageParams(page=40, limit=20)  # Start at offset 780
        bounds = compute_bounds(params)

        def run():
            return collect_window(iter(range(1000)), bounds)

        result, total = benchmark(run)
        assert len(result) == 20
