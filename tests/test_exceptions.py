"""Tests for exceptions module."""

from __future__ import annotations

import pytest

from pypaginator.exceptions import (
    FilterException,
    FilterValidationError,
    PaginationConfigurationError,
    PaginatorException,
    SearchException,
    SearchNormalizationError,
    SearchQueryError,
    SortException,
    ValidationException,
)


class TestPaginatorException:
    """Test base exception."""

    def test_message(self) -> None:
        """Exception should store message."""
        exc = PaginatorException("test message")
        assert str(exc) == "test message"

    def test_inheritance(self) -> None:
        """Should inherit from Exception."""
        assert issubclass(PaginatorException, Exception)


class TestPaginationConfigurationError:
    """Test configuration error."""

    def test_basic_message(self) -> None:
        """Should store message."""
        exc = PaginationConfigurationError("config error")
        assert "config error" in str(exc)

    def test_with_details(self) -> None:
        """Should store details."""
        exc = PaginationConfigurationError("error", details={"key": "value"})
        assert exc.details == {"key": "value"}

    def test_inheritance(self) -> None:
        """Should inherit from PaginatorException."""
        assert issubclass(PaginationConfigurationError, PaginatorException)


class TestFilterException:
    """Test filter exception."""

    def test_message(self) -> None:
        """Should store message."""
        exc = FilterException("filter error")
        assert str(exc) == "filter error"

    def test_inheritance(self) -> None:
        """Should inherit from PaginatorException."""
        assert issubclass(FilterException, PaginatorException)


class TestFilterValidationError:
    """Test filter validation error."""

    def test_message(self) -> None:
        """Should store message."""
        exc = FilterValidationError("validation error")
        assert str(exc) == "validation error"

    def test_inheritance(self) -> None:
        """Should inherit from FilterException."""
        assert issubclass(FilterValidationError, FilterException)


class TestSearchException:
    """Test search exception."""

    def test_message(self) -> None:
        """Should store message."""
        exc = SearchException("search error")
        assert str(exc) == "search error"

    def test_inheritance(self) -> None:
        """Should inherit from PaginatorException."""
        assert issubclass(SearchException, PaginatorException)


class TestSearchQueryError:
    """Test search query error."""

    def test_message(self) -> None:
        """Should store message."""
        exc = SearchQueryError("query error")
        assert str(exc) == "query error"

    def test_inheritance(self) -> None:
        """Should inherit from SearchException."""
        assert issubclass(SearchQueryError, SearchException)


class TestSearchNormalizationError:
    """Test search normalization error."""

    def test_message(self) -> None:
        """Should store message."""
        exc = SearchNormalizationError("normalization error")
        assert str(exc) == "normalization error"

    def test_inheritance(self) -> None:
        """Should inherit from SearchException."""
        assert issubclass(SearchNormalizationError, SearchException)


class TestSortException:
    """Test sort exception."""

    def test_message(self) -> None:
        """Should store message."""
        exc = SortException("sort error")
        assert str(exc) == "sort error"

    def test_inheritance(self) -> None:
        """Should inherit from PaginatorException."""
        assert issubclass(SortException, PaginatorException)


class TestValidationException:
    """Test validation exception."""

    def test_message(self) -> None:
        """Should store message."""
        exc = ValidationException(field="age", value=-1, reason="must be positive")
        assert "age" in str(exc)
        assert "must be positive" in str(exc)

    def test_attributes(self) -> None:
        """Should store attributes."""
        exc = ValidationException(field="age", value=-1, reason="must be positive")
        assert exc.field == "age"
        assert exc.value == -1
        assert exc.reason == "must be positive"

    def test_inheritance(self) -> None:
        """Should inherit from PaginatorException."""
        assert issubclass(ValidationException, PaginatorException)

