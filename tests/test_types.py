"""Tests for types module - Protocols."""

from __future__ import annotations

import pytest

from pypaginator.types import (
    PageParamsProtocol,
    PageProtocol,
    SupportsTotalOrdering,
    SqlClause,
    SqlStringExpression,
)
from pypaginator.core.pages import PageParams, Page


class TestPageParamsProtocol:
    """Test PageParamsProtocol."""

    def test_protocol_exists(self) -> None:
        """Protocol should exist."""
        assert PageParamsProtocol is not None

    def test_page_params_implements_protocol(self) -> None:
        """PageParams should implement the protocol."""
        params = PageParams(page=1, limit=10)
        assert isinstance(params, PageParamsProtocol)

    def test_has_page_attribute(self) -> None:
        """Protocol should require page attribute."""
        params = PageParams(page=2, limit=10)
        assert hasattr(params, "page")
        assert params.page == 2

    def test_has_limit_attribute(self) -> None:
        """Protocol should require limit attribute."""
        params = PageParams(page=1, limit=20)
        assert hasattr(params, "limit")
        assert params.limit == 20

    def test_has_offset_property(self) -> None:
        """Protocol should require offset property."""
        params = PageParams(page=3, limit=10)
        assert hasattr(params, "offset")
        assert params.offset == 20


class TestPageProtocol:
    """Test PageProtocol."""

    def test_protocol_exists(self) -> None:
        """Protocol should exist."""
        assert PageProtocol is not None

    def test_page_implements_protocol(self) -> None:
        """Page should implement the protocol."""
        page = Page(items=[1, 2, 3], total=3, page=1, limit=10)
        assert isinstance(page, PageProtocol)

    def test_has_required_attributes(self) -> None:
        """Protocol should require items, total, page, limit."""
        page = Page(items=[1, 2], total=10, page=1, limit=10)
        assert hasattr(page, "items")
        assert hasattr(page, "total")
        assert hasattr(page, "page")
        assert hasattr(page, "limit")


class TestSupportsTotalOrdering:
    """Test SupportsTotalOrdering protocol."""

    def test_protocol_exists(self) -> None:
        """Protocol should exist."""
        assert SupportsTotalOrdering is not None

    def test_int_implements_protocol(self) -> None:
        """int should implement the protocol."""
        assert isinstance(5, SupportsTotalOrdering)

    def test_float_implements_protocol(self) -> None:
        """float should implement the protocol."""
        assert isinstance(5.0, SupportsTotalOrdering)

    def test_str_implements_protocol(self) -> None:
        """str should implement the protocol."""
        assert isinstance("hello", SupportsTotalOrdering)


class TestSqlClause:
    """Test SqlClause protocol."""

    def test_protocol_exists(self) -> None:
        """Protocol should exist."""
        assert SqlClause is not None


class TestSqlStringExpression:
    """Test SqlStringExpression protocol."""

    def test_protocol_exists(self) -> None:
        """Protocol should exist."""
        assert SqlStringExpression is not None
