"""Stress tests for boundary value conditions."""

from __future__ import annotations

import sys

import pytest

from pypaginate import OffsetParams, OverflowStrategy, paginate


pytestmark = pytest.mark.stress


class TestLimitOne:
    def test_limit_one_page_count(self) -> None:
        """limit=1 produces pages equal to total items."""
        data = list(range(10))
        result = paginate(data, OffsetParams(page=1, limit=1))

        assert result.pages == 10
        assert len(result.items) == 1

    def test_limit_one_last_page(self) -> None:
        """limit=1 last page has exactly 1 item."""
        data = list(range(10))
        result = paginate(data, OffsetParams(page=10, limit=1))

        assert len(result.items) == 1
        assert result.has_next is False


class TestMaxLimit:
    def test_max_limit_page_count(self) -> None:
        """limit=1000 on 5000 items yields 5 pages."""
        data = list(range(5_000))
        result = paginate(data, OffsetParams(page=1, limit=1000))

        assert result.pages == 5
        assert len(result.items) == 1000

    def test_max_limit_last_page(self) -> None:
        """limit=1000 last page is correct."""
        data = list(range(5_000))
        result = paginate(data, OffsetParams(page=5, limit=1000))

        assert len(result.items) == 1000
        assert result.has_next is False


class TestExactFit:
    def test_exact_n_items_one_page(self) -> None:
        """Exactly N items with limit=N yields 1 page."""
        data = list(range(20))
        result = paginate(data, OffsetParams(page=1, limit=20))

        assert result.pages == 1
        assert result.has_next is False

    def test_n_plus_one_two_pages(self) -> None:
        """N+1 items with limit=N yields 2 pages."""
        data = list(range(21))
        result = paginate(data, OffsetParams(page=2, limit=20))

        assert result.pages == 2
        assert len(result.items) == 1
        assert result.has_next is False


class TestEmptyDataset:
    def test_empty_first_page(self) -> None:
        """page=1 on empty dataset returns 0 total."""
        result = paginate([], OffsetParams(page=1, limit=20))

        assert result.total == 0
        assert result.items == []
        assert result.has_next is False
        assert result.has_previous is False


class TestLastPage:
    def test_last_page_flags(self) -> None:
        """Last page has has_next=False, has_previous=True."""
        data = list(range(50))
        result = paginate(data, OffsetParams(page=5, limit=10))

        assert result.has_next is False
        assert result.has_previous is True


class TestClampOverflow:
    def test_clamp_large_page(self) -> None:
        """Clamp strategy on very large page clamps to last."""
        data = list(range(100))
        result = paginate(
            data,
            OffsetParams(page=sys.maxsize, limit=10),
            overflow=OverflowStrategy.CLAMP,
        )

        assert result.page == 10
        assert result.has_next is False

    def test_clamp_on_empty(self) -> None:
        """Clamp on empty dataset returns page 1."""
        result = paginate(
            [],
            OffsetParams(page=999, limit=10),
            overflow=OverflowStrategy.CLAMP,
        )

        assert result.page == 1
        assert result.total == 0
