"""Tests for the __init__ module exports."""

from __future__ import annotations


class TestPackageExports:
    """Test that main package exports are available."""

    def test_page_params_export(self) -> None:
        """PageParams should be exported."""
        from pypaginate import PageParams

        params = PageParams(page=1, limit=10)
        assert params.page == 1
        assert params.limit == 10

    def test_page_export(self) -> None:
        """Page should be exported."""
        from pypaginate import Page

        page = Page(items=[1, 2, 3], total=3, page=1, limit=10)
        assert len(page.items) == 3
        assert page.total == 3

    def test_keyset_page_params_export(self) -> None:
        """KeysetPageParams should be exported."""
        from pypaginate import KeysetPageParams

        params = KeysetPageParams(limit=10)
        assert params.limit == 10

    def test_paginator_exception_export(self) -> None:
        """PaginatorException should be exported."""
        from pypaginate import PaginatorException

        assert PaginatorException is not None

    def test_filter_exception_export(self) -> None:
        """FilterException should be exported."""
        from pypaginate import FilterException

        assert FilterException is not None

    def test_search_exception_export(self) -> None:
        """SearchException should be exported."""
        from pypaginate import SearchException

        assert SearchException is not None

    def test_sort_exception_export(self) -> None:
        """SortException should be exported."""
        from pypaginate import SortException

        assert SortException is not None

    def test_pagination_configuration_error_export(self) -> None:
        """PaginationConfigurationError should be exported."""
        from pypaginate import PaginationConfigurationError

        assert PaginationConfigurationError is not None

    def test_version_export(self) -> None:
        """__version__ should be exported."""
        from pypaginate import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)


class TestSubmoduleImports:
    """Test that submodule imports work."""

    def test_memory_paginator_import(self) -> None:
        """MemoryPaginator should be importable from engines."""
        from pypaginate.engines import MemoryPaginator

        paginator = MemoryPaginator()
        assert paginator is not None

    def test_filter_engine_import(self) -> None:
        """FilterEngine should be importable from filters."""
        from pypaginate.filters.predicates import FilterEngine

        engine = FilterEngine()
        assert engine is not None

    def test_sort_engine_import(self) -> None:
        """SortEngine should be importable from sorting."""
        from pypaginate.sorting import SortEngine

        engine = SortEngine()
        assert engine is not None
