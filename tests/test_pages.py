"""Tests for page dataclasses comprehensive coverage."""

from __future__ import annotations

import pytest

from pypaginate.core.pages import KeysetPageParams, Page, PageParams


class TestPageParams:
    """Test PageParams dataclass."""

    def test_defaults(self) -> None:
        """Should have sensible defaults."""
        params = PageParams()
        assert params.page == 1
        assert params.limit == 20

    def test_custom_values(self) -> None:
        """Should accept custom values."""
        params = PageParams(page=5, limit=50)
        assert params.page == 5
        assert params.limit == 50

    def test_validation_page_zero_raises(self) -> None:
        """Page 0 should raise."""
        with pytest.raises(Exception):
            PageParams(page=0, limit=10)

    def test_validation_negative_page_raises(self) -> None:
        """Negative page should raise."""
        with pytest.raises(Exception):
            PageParams(page=-1, limit=10)

    def test_validation_limit_zero_raises(self) -> None:
        """Limit 0 should raise."""
        with pytest.raises(Exception):
            PageParams(page=1, limit=0)

    def test_validation_negative_limit_raises(self) -> None:
        """Negative limit should raise."""
        with pytest.raises(Exception):
            PageParams(page=1, limit=-5)

    def test_offset(self) -> None:
        """Offset should be calculated correctly."""
        params = PageParams(page=1, limit=20)
        assert params.offset == 0

        params = PageParams(page=2, limit=20)
        assert params.offset == 20

        params = PageParams(page=3, limit=10)
        assert params.offset == 20


class TestKeysetPageParams:
    """Test KeysetPageParams dataclass."""

    def test_defaults(self) -> None:
        """Should have sensible defaults."""
        params = KeysetPageParams()
        assert params.limit == 20
        assert params.after is None
        assert params.before is None

    def test_with_after(self) -> None:
        """Should accept after bookmark."""
        params = KeysetPageParams(limit=10, after="abc123")
        assert params.limit == 10
        assert params.after == "abc123"
        assert params.before is None

    def test_with_before(self) -> None:
        """Should accept before bookmark."""
        params = KeysetPageParams(limit=10, before="abc123")
        assert params.before == "abc123"
        assert params.after is None

    def test_custom_limit(self) -> None:
        """Should accept custom limit."""
        params = KeysetPageParams(limit=100)
        assert params.limit == 100


class TestPage:
    """Test Page dataclass."""

    def test_creation(self) -> None:
        """Should create Page."""
        page = Page(items=[1, 2, 3], total=10, page=1, limit=3)
        assert page.items == [1, 2, 3]
        assert page.total == 10
        assert page.page == 1
        assert page.limit == 3

    def test_empty_page(self) -> None:
        """Should create empty Page."""
        page = Page(items=[], total=0, page=1, limit=10)
        assert page.items == []
        assert page.total == 0

    def test_has_next_true(self) -> None:
        """has_next should be True when more pages exist."""
        page = Page(items=[1, 2], total=10, page=1, limit=2)
        assert page.has_next is True

    def test_has_next_false(self) -> None:
        """has_next should be False on last page."""
        page = Page(items=[9, 10], total=10, page=5, limit=2)
        assert page.has_next is False

    def test_has_next_on_empty(self) -> None:
        """has_next should be False for empty page."""
        page = Page(items=[], total=0, page=1, limit=10)
        assert page.has_next is False

    def test_generic_type(self) -> None:
        """Page should work with generic types."""
        from dataclasses import dataclass

        @dataclass
        class Item:
            id: int
            name: str

        items = [Item(1, "a"), Item(2, "b")]
        page: Page[Item] = Page(items=items, total=5, page=1, limit=2)
        assert page.items[0].name == "a"

    def test_items_list(self) -> None:
        """Items should be a list."""
        page = Page(items=["a", "b", "c"], total=3, page=1, limit=10)
        assert isinstance(page.items, list)
        assert len(page.items) == 3

    def test_total_zero(self) -> None:
        """Total can be zero."""
        page = Page(items=[], total=0, page=1, limit=10)
        assert page.total == 0

    def test_large_page_number(self) -> None:
        """Should handle large page numbers."""
        page = Page(items=[], total=100, page=999, limit=10)
        assert page.page == 999
        assert page.has_next is False
