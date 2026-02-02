"""Snapshot tests for Page serialization.

These tests use syrupy to verify that Page serialization
remains consistent across changes.
"""

from __future__ import annotations

import pytest


try:
    from syrupy.assertion import SnapshotAssertion

    SYRUPY_AVAILABLE = True
except ImportError:
    SYRUPY_AVAILABLE = False

from pypaginate import Page, PageParams


pytestmark = [pytest.mark.snapshot]


@pytest.mark.skipif(not SYRUPY_AVAILABLE, reason="syrupy not installed")
class TestPageSnapshots:
    """Snapshot tests for Page serialization."""

    def test_empty_page_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Empty page serialization should match snapshot."""
        page: Page[int] = Page(items=[], total=0, page=1, limit=10)

        result = {
            "items": page.items,
            "total": page.total,
            "page": page.page,
            "limit": page.limit,
            "pages": page.pages,
            "has_next": page.has_next,
            "has_previous": page.has_previous,
        }

        assert result == snapshot

    def test_first_page_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """First page serialization should match snapshot."""
        page: Page[int] = Page(items=[1, 2, 3, 4, 5], total=50, page=1, limit=5)

        result = {
            "items": page.items,
            "total": page.total,
            "page": page.page,
            "limit": page.limit,
            "pages": page.pages,
            "has_next": page.has_next,
            "has_previous": page.has_previous,
        }

        assert result == snapshot

    def test_middle_page_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Middle page serialization should match snapshot."""
        page: Page[int] = Page(items=[21, 22, 23, 24, 25], total=50, page=5, limit=5)

        result = {
            "items": page.items,
            "total": page.total,
            "page": page.page,
            "limit": page.limit,
            "pages": page.pages,
            "has_next": page.has_next,
            "has_previous": page.has_previous,
        }

        assert result == snapshot

    def test_last_page_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Last page serialization should match snapshot."""
        page: Page[int] = Page(items=[46, 47, 48, 49, 50], total=50, page=10, limit=5)

        result = {
            "items": page.items,
            "total": page.total,
            "page": page.page,
            "limit": page.limit,
            "pages": page.pages,
            "has_next": page.has_next,
            "has_previous": page.has_previous,
        }

        assert result == snapshot

    def test_page_with_dict_items_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Page with dict items serialization should match snapshot."""
        items = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]
        page: Page[dict] = Page(items=items, total=100, page=1, limit=10)

        result = {
            "items": page.items,
            "total": page.total,
            "page": page.page,
            "limit": page.limit,
            "pages": page.pages,
            "has_next": page.has_next,
            "has_previous": page.has_previous,
        }

        assert result == snapshot


@pytest.mark.skipif(not SYRUPY_AVAILABLE, reason="syrupy not installed")
class TestPageParamsSnapshots:
    """Snapshot tests for PageParams serialization."""

    def test_default_params_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Default PageParams serialization should match snapshot."""
        params = PageParams()

        result = {
            "page": params.page,
            "limit": params.limit,
            "offset": params.offset,
        }

        assert result == snapshot

    def test_custom_params_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Custom PageParams serialization should match snapshot."""
        params = PageParams(page=5, limit=25)

        result = {
            "page": params.page,
            "limit": params.limit,
            "offset": params.offset,
        }

        assert result == snapshot

    def test_large_page_params_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Large page number PageParams serialization should match snapshot."""
        params = PageParams(page=1000, limit=100)

        result = {
            "page": params.page,
            "limit": params.limit,
            "offset": params.offset,
        }

        assert result == snapshot
