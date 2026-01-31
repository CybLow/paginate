"""Property-based tests for pagination logic.

These tests use Hypothesis to verify invariants and properties
that should hold for all valid inputs.
"""

from __future__ import annotations

import pytest

try:
    from hypothesis import given, strategies as st, assume, settings
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Create dummy decorators for when hypothesis is not installed
    def given(*args, **kwargs):
        def decorator(func):
            return pytest.mark.skip(reason="hypothesis not installed")(func)
        return decorator
    
    class st:
        @staticmethod
        def integers(*args, **kwargs):
            return None
        @staticmethod
        def lists(*args, **kwargs):
            return None
        @staticmethod
        def text(*args, **kwargs):
            return None
    
    def assume(condition):
        pass
    
    def settings(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from pypaginate import Page, PageParams


pytestmark = pytest.mark.property


class TestPageParamsProperties:
    """Property-based tests for PageParams invariants."""

    @given(
        page=st.integers(min_value=1, max_value=10000),
        limit=st.integers(min_value=1, max_value=1000),
    )
    def test_offset_is_non_negative(self, page: int, limit: int) -> None:
        """Offset should always be non-negative for valid page numbers."""
        params = PageParams(page=page, limit=limit)
        assert params.offset >= 0

    @given(
        page=st.integers(min_value=1, max_value=10000),
        limit=st.integers(min_value=1, max_value=1000),
    )
    def test_offset_formula_is_correct(self, page: int, limit: int) -> None:
        """Offset should always equal (page - 1) * limit."""
        params = PageParams(page=page, limit=limit)
        expected_offset = (page - 1) * limit
        assert params.offset == expected_offset

    @given(
        page=st.integers(min_value=1, max_value=10000),
        limit=st.integers(min_value=1, max_value=1000),
    )
    def test_page_params_are_immutable_after_creation(self, page: int, limit: int) -> None:
        """PageParams values should remain consistent."""
        params = PageParams(page=page, limit=limit)
        # Read values multiple times
        assert params.page == page
        assert params.limit == limit
        assert params.page == page  # Still the same


class TestPageProperties:
    """Property-based tests for Page container invariants."""

    @given(
        items_count=st.integers(min_value=0, max_value=100),
        total=st.integers(min_value=0, max_value=10000),
        page=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=1, max_value=100),
    )
    def test_pages_calculation_formula(
        self,
        items_count: int,
        total: int,
        page: int,
        limit: int,
    ) -> None:
        """Total pages should be ceil(total / limit)."""
        items = list(range(items_count))
        pg = Page(items=items, total=total, page=page, limit=limit)
        
        # Formula: (total + limit - 1) // limit
        # When total=0, this returns 0 (no pages needed)
        expected_pages = (total + limit - 1) // limit
        
        assert pg.pages == expected_pages

    @given(
        items_count=st.integers(min_value=0, max_value=100),
        total=st.integers(min_value=0, max_value=10000),
        limit=st.integers(min_value=1, max_value=100),
    )
    def test_has_previous_is_false_for_first_page(
        self,
        items_count: int,
        total: int,
        limit: int,
    ) -> None:
        """First page should never have a previous page."""
        items = list(range(items_count))
        pg = Page(items=items, total=total, page=1, limit=limit)
        assert pg.has_previous is False

    @given(
        items_count=st.integers(min_value=0, max_value=100),
        total=st.integers(min_value=0, max_value=10000),
        page=st.integers(min_value=2, max_value=100),
        limit=st.integers(min_value=1, max_value=100),
    )
    def test_has_previous_is_true_for_non_first_page(
        self,
        items_count: int,
        total: int,
        page: int,
        limit: int,
    ) -> None:
        """Non-first pages should always have a previous page."""
        items = list(range(items_count))
        pg = Page(items=items, total=total, page=page, limit=limit)
        assert pg.has_previous is True

    @given(
        items_count=st.integers(min_value=0, max_value=100),
        total=st.integers(min_value=1, max_value=10000),
        limit=st.integers(min_value=1, max_value=100),
    )
    def test_last_page_has_no_next(
        self,
        items_count: int,
        total: int,
        limit: int,
    ) -> None:
        """The last page should not have a next page."""
        items = list(range(items_count))
        # Calculate the last page
        last_page = max(1, (total + limit - 1) // limit)
        pg = Page(items=items, total=total, page=last_page, limit=limit)
        assert pg.has_next is False

    @given(
        items=st.lists(st.integers(), min_size=0, max_size=50),
        total=st.integers(min_value=0, max_value=10000),
        page=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=1, max_value=100),
    )
    def test_items_preserved_correctly(
        self,
        items: list[int],
        total: int,
        page: int,
        limit: int,
    ) -> None:
        """Items list should be preserved exactly as provided."""
        pg = Page(items=items, total=total, page=page, limit=limit)
        assert pg.items == items
        assert len(pg.items) == len(items)


class TestPaginationMathProperties:
    """Property-based tests for pagination math correctness."""

    @given(
        total=st.integers(min_value=0, max_value=10000),
        limit=st.integers(min_value=1, max_value=100),
    )
    def test_all_items_are_reachable(self, total: int, limit: int) -> None:
        """All items should be reachable through valid page numbers."""
        # Calculate number of pages
        if total == 0:
            pages = 1
        else:
            pages = (total + limit - 1) // limit
        
        # Verify all items are covered
        items_covered = 0
        for page_num in range(1, pages + 1):
            params = PageParams(page=page_num, limit=limit)
            # Calculate items on this page
            start = params.offset
            end = min(start + limit, total)
            if start < total:
                items_covered += end - start
        
        assert items_covered == total

    @given(
        page=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=1, max_value=1000),
    )
    def test_consecutive_pages_dont_overlap(self, page: int, limit: int) -> None:
        """Consecutive pages should not have overlapping offsets."""
        params1 = PageParams(page=page, limit=limit)
        params2 = PageParams(page=page + 1, limit=limit)
        
        # End of page 1 should be start of page 2
        end_of_page1 = params1.offset + limit
        start_of_page2 = params2.offset
        
        assert end_of_page1 == start_of_page2

    @given(
        page=st.integers(min_value=1, max_value=1000),
        limit=st.integers(min_value=1, max_value=1000),
    )
    def test_no_gaps_between_pages(self, page: int, limit: int) -> None:
        """There should be no gaps between consecutive pages."""
        if page == 1:
            params = PageParams(page=page, limit=limit)
            assert params.offset == 0
        else:
            params_prev = PageParams(page=page - 1, limit=limit)
            params_curr = PageParams(page=page, limit=limit)
            assert params_curr.offset == params_prev.offset + limit
