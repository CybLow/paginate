"""Tests for core context module."""

from __future__ import annotations

import pytest

from pypaginate.core.context import PaginationContext, clamp_page_params
from pypaginate.core.pages import PageParams


class TestClampPageParams:
    """Test clamp_page_params function."""

    def test_no_clamping_needed(self) -> None:
        """Should return unchanged if within bounds."""
        params = PageParams(page=1, limit=10)
        result = clamp_page_params(total=100, params=params)
        assert result.page == 1
        assert result.limit == 10

    def test_clamp_page_to_max(self) -> None:
        """Should clamp page to max valid page."""
        params = PageParams(page=100, limit=10)
        result = clamp_page_params(total=50, params=params)
        # 50 items / 10 per page = 5 pages max
        assert result.page <= 5

    def test_zero_total(self) -> None:
        """Should handle zero total."""
        params = PageParams(page=1, limit=10)
        result = clamp_page_params(total=0, params=params)
        assert result.page == 1

    def test_clamp_high_page(self) -> None:
        """Should clamp page higher than available pages."""
        params = PageParams(page=999, limit=10)
        result = clamp_page_params(total=20, params=params)
        # 20 items / 10 per page = 2 pages
        assert result.page == 2


class TestPaginationContext:
    """Test PaginationContext class."""

    def test_creation_with_required_fields(self) -> None:
        """Should create with required fields."""
        params = PageParams(page=1, limit=10)
        context = PaginationContext(params=params, clamp=False, unique=False)
        assert context.params == params
        assert context.clamp is False
        assert context.unique is False
        assert context.count_query is None

    def test_creation_with_options(self) -> None:
        """Should create with custom options."""
        params = PageParams(page=1, limit=10)
        context = PaginationContext(
            params=params,
            clamp=True,
            unique=True,
        )
        assert context.clamp is True
        assert context.unique is True

    def test_immutability(self) -> None:
        """Context should be immutable (frozen dataclass)."""
        params = PageParams(page=1, limit=10)
        context = PaginationContext(params=params, clamp=False, unique=False)
        with pytest.raises(Exception):  # FrozenInstanceError
            context.clamp = True  # type: ignore[misc]
