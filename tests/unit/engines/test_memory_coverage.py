"""Additional tests for memory engine to improve coverage.

This module adds tests for the memory pagination engine's
edge cases and streaming functionality.
"""

from __future__ import annotations

import pytest

from pypaginate import PageParams
from pypaginate.engines.memory import (
    MemoryPaginator,
    SliceBounds,
    collect_window,
    compute_bounds,
    filter_iter,
)


pytestmark = pytest.mark.unit


class TestFilterIter:
    """Tests for the filter_iter function."""

    def test_filter_iter_with_none_predicate(self) -> None:
        """Should yield all items when predicate is None."""
        items = [1, 2, 3, 4, 5]
        result = list(filter_iter(items, None))
        assert result == [1, 2, 3, 4, 5]

    def test_filter_iter_with_predicate(self) -> None:
        """Should yield only items matching predicate."""
        items = [1, 2, 3, 4, 5]
        result = list(filter_iter(items, lambda x: x % 2 == 0))
        assert result == [2, 4]

    def test_filter_iter_with_all_matching(self) -> None:
        """Should yield all items when all match predicate."""
        items = [2, 4, 6, 8]
        result = list(filter_iter(items, lambda x: x % 2 == 0))
        assert result == [2, 4, 6, 8]

    def test_filter_iter_with_none_matching(self) -> None:
        """Should yield nothing when no items match."""
        items = [1, 3, 5, 7]
        result = list(filter_iter(items, lambda x: x % 2 == 0))
        assert result == []

    def test_filter_iter_with_empty_iterable(self) -> None:
        """Should handle empty iterables."""
        items: list[int] = []
        result = list(filter_iter(items, lambda x: x > 0))
        assert result == []

    def test_filter_iter_with_generator(self) -> None:
        """Should work with generators."""
        def gen():
            yield from range(10)

        result = list(filter_iter(gen(), lambda x: x < 5))
        assert result == [0, 1, 2, 3, 4]


class TestSliceBounds:
    """Tests for SliceBounds dataclass."""

    def test_slice_bounds_creation(self) -> None:
        """Should create SliceBounds correctly."""
        bounds = SliceBounds(start=10, end=20)
        assert bounds.start == 10
        assert bounds.end == 20

    def test_slice_bounds_is_frozen(self) -> None:
        """SliceBounds should be immutable."""
        bounds = SliceBounds(start=0, end=10)
        with pytest.raises(AttributeError):
            bounds.start = 5  # type: ignore


class TestComputeBounds:
    """Tests for compute_bounds function."""

    def test_compute_bounds_first_page(self) -> None:
        """Should compute correct bounds for first page."""
        params = PageParams(page=1, limit=10)
        bounds = compute_bounds(params)
        assert bounds.start == 0
        assert bounds.end == 10

    def test_compute_bounds_second_page(self) -> None:
        """Should compute correct bounds for second page."""
        params = PageParams(page=2, limit=10)
        bounds = compute_bounds(params)
        assert bounds.start == 10
        assert bounds.end == 20

    def test_compute_bounds_large_page(self) -> None:
        """Should compute correct bounds for large page numbers."""
        params = PageParams(page=100, limit=50)
        bounds = compute_bounds(params)
        assert bounds.start == 4950
        assert bounds.end == 5000

    def test_compute_bounds_limit_one(self) -> None:
        """Should handle limit of 1."""
        params = PageParams(page=5, limit=1)
        bounds = compute_bounds(params)
        assert bounds.start == 4
        assert bounds.end == 5


class TestCollectWindow:
    """Tests for collect_window function."""

    def test_collect_window_first_page(self) -> None:
        """Should collect first page correctly."""
        items = iter(range(100))
        bounds = SliceBounds(start=0, end=10)
        window, total = collect_window(items, bounds)
        assert window == list(range(10))
        assert total == 100

    def test_collect_window_middle_page(self) -> None:
        """Should collect middle page correctly."""
        items = iter(range(100))
        bounds = SliceBounds(start=20, end=30)
        window, total = collect_window(items, bounds)
        assert window == list(range(20, 30))
        assert total == 100

    def test_collect_window_last_page(self) -> None:
        """Should collect last page correctly."""
        items = iter(range(95))
        bounds = SliceBounds(start=90, end=100)
        window, total = collect_window(items, bounds)
        assert window == list(range(90, 95))
        assert total == 95

    def test_collect_window_beyond_data(self) -> None:
        """Should handle bounds beyond available data."""
        items = iter(range(50))
        bounds = SliceBounds(start=60, end=70)
        window, total = collect_window(items, bounds)
        assert window == []
        assert total == 50

    def test_collect_window_empty_iterator(self) -> None:
        """Should handle empty iterator."""
        items = iter([])
        bounds = SliceBounds(start=0, end=10)
        window, total = collect_window(items, bounds)
        assert window == []
        assert total == 0


class TestMemoryPaginatorClamp:
    """Tests for MemoryPaginator with clamping."""

    def test_paginate_with_clamp_sequence(self) -> None:
        """Should clamp page for sequence beyond bounds."""
        paginator: MemoryPaginator[int] = MemoryPaginator(clamp=True)
        items = list(range(100))
        params = PageParams(page=100, limit=10)  # Way beyond

        result = paginator.paginate(items, params)

        # Should clamp to last valid page
        assert result.page <= 10
        assert len(result.items) > 0

    def test_paginate_without_clamp_sequence(self) -> None:
        """Should not clamp when clamp=False."""
        paginator: MemoryPaginator[int] = MemoryPaginator(clamp=False)
        items = list(range(100))
        params = PageParams(page=100, limit=10)

        result = paginator.paginate(items, params)

        assert result.page == 100
        assert result.items == []

    def test_paginate_stream_with_clamp(self) -> None:
        """Should clamp page for stream pagination."""
        paginator: MemoryPaginator[int] = MemoryPaginator(clamp=True)
        # Use a generator to force stream pagination
        def gen():
            yield from range(100)

        params = PageParams(page=100, limit=10)
        result = paginator.paginate(gen(), params)

        # Should return valid page
        assert result.total == 100

    def test_paginate_stream_with_predicate(self) -> None:
        """Should handle stream with predicate."""
        paginator: MemoryPaginator[int] = MemoryPaginator(clamp=False)
        items = list(range(100))
        params = PageParams(page=1, limit=10)
        predicate = lambda x: x % 2 == 0

        result = paginator.paginate(items, params, predicate)

        assert len(result.items) == 10
        assert all(x % 2 == 0 for x in result.items)
        assert result.total == 50  # 50 even numbers

    def test_paginate_stream_with_clamp_and_predicate(self) -> None:
        """Should handle stream with both clamp and predicate."""
        paginator: MemoryPaginator[int] = MemoryPaginator(clamp=True)
        items = list(range(100))
        params = PageParams(page=10, limit=10)  # Beyond filtered count
        predicate = lambda x: x < 30  # Only 30 items pass

        result = paginator.paginate(items, params, predicate)

        # Should clamp to valid page
        assert result.total == 30


class TestMemoryPaginatorEdgeCases:
    """Edge case tests for MemoryPaginator."""

    def test_paginate_single_item(self) -> None:
        """Should handle single item sequence."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = [42]
        params = PageParams(page=1, limit=10)

        result = paginator.paginate(items, params)

        assert result.items == [42]
        assert result.total == 1

    def test_paginate_empty_sequence(self) -> None:
        """Should handle empty sequence."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items: list[int] = []
        params = PageParams(page=1, limit=10)

        result = paginator.paginate(items, params)

        assert result.items == []
        assert result.total == 0

    def test_paginate_exact_page_boundary(self) -> None:
        """Should handle exact page boundary."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = list(range(100))  # Exactly 10 pages of 10
        params = PageParams(page=10, limit=10)

        result = paginator.paginate(items, params)

        assert result.items == list(range(90, 100))
        assert result.total == 100

    def test_paginate_with_tuple(self) -> None:
        """Should work with tuple (also a Sequence)."""
        paginator: MemoryPaginator[int] = MemoryPaginator()
        items = tuple(range(50))
        params = PageParams(page=2, limit=10)

        result = paginator.paginate(items, params)

        assert result.items == list(range(10, 20))
        assert result.total == 50

    def test_paginate_with_string(self) -> None:
        """Should work with string (also a Sequence)."""
        paginator: MemoryPaginator[str] = MemoryPaginator()
        items = "abcdefghij"
        params = PageParams(page=1, limit=5)

        result = paginator.paginate(items, params)

        assert result.items == ["a", "b", "c", "d", "e"]
        assert result.total == 10
