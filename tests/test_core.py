"""Basic tests for pypaginate core functionality."""

from __future__ import annotations

import pytest

from pypaginate import Page, PageParams, __version__


class TestVersion:
    """Test version information."""

    def test_version_exists(self) -> None:
        """Version should be defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_format(self) -> None:
        """Version should follow semver format."""
        parts = __version__.split(".")
        assert len(parts) >= 2
        assert all(part.isdigit() for part in parts[:2])


class TestPageParams:
    """Test PageParams dataclass."""

    def test_default_values(self) -> None:
        """PageParams should have sensible defaults."""
        params = PageParams()
        assert params.page >= 1
        assert params.limit > 0

    def test_custom_values(self) -> None:
        """PageParams should accept custom values."""
        params = PageParams(page=2, limit=50)
        assert params.page == 2
        assert params.limit == 50

    def test_offset_calculation(self) -> None:
        """PageParams should calculate correct offset."""
        params = PageParams(page=3, limit=10)
        assert params.offset == 20  # (3-1) * 10


class TestPage:
    """Test Page container."""

    def test_empty_page(self) -> None:
        """Empty page should work correctly."""
        page: Page[int] = Page(items=[], total=0, page=1, limit=10)
        assert page.items == []
        assert page.total == 0
        assert len(page.items) == 0

    def test_page_with_items(self) -> None:
        """Page with items should work correctly."""
        items = [1, 2, 3]
        page: Page[int] = Page(items=items, total=3, page=1, limit=10)
        assert page.items == items
        assert len(page.items) == 3

    def test_page_navigation(self) -> None:
        """Page should calculate navigation correctly."""
        # Page 2 of 5 total
        page: Page[int] = Page(items=[1, 2], total=50, page=2, limit=10)
        assert page.pages == 5
        assert page.has_previous is True
        assert page.has_next is True

    def test_first_page_navigation(self) -> None:
        """First page should not have previous."""
        page: Page[int] = Page(items=[1, 2], total=50, page=1, limit=10)
        assert page.has_previous is False
        assert page.has_next is True

    def test_last_page_navigation(self) -> None:
        """Last page should not have next."""
        page: Page[int] = Page(items=[1, 2], total=50, page=5, limit=10)
        assert page.has_previous is True
        assert page.has_next is False


@pytest.mark.unit
class TestCoreImports:
    """Test that core modules import correctly."""

    def test_import_exceptions(self) -> None:
        """Exceptions should be importable."""
        from pypaginate import (
            FilterException,
            PaginationConfigurationError,
            PaginatorException,
            SearchException,
            SortException,
            ValidationException,
        )

        assert issubclass(PaginatorException, Exception)
        assert issubclass(PaginationConfigurationError, PaginatorException)
        assert issubclass(FilterException, PaginatorException)
        assert issubclass(SearchException, PaginatorException)
        assert issubclass(SortException, PaginatorException)
        assert issubclass(ValidationException, PaginatorException)
