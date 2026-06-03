"""Exception hierarchy for pypaginate.

Follows Python convention: XxxError naming (like ValueError, TypeError).
All exceptions carry structured ``details`` for programmatic handling.
"""

from __future__ import annotations

from typing import Any


class PaginationError(Exception):
    """Base exception for all pypaginate errors."""


class ConfigurationError(PaginationError):
    """Raised when pagination configuration is invalid."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.details = details or {}
        super().__init__(message)


class FilterError(PaginationError):
    """Raised when filtering operations fail."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        self.details = details or {}
        super().__init__(message)


class FilterValidationError(FilterError):
    """Raised when filter specification validation fails."""


class SearchError(PaginationError):
    """Raised when search operations fail."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.details = details or {}
        super().__init__(message)


class SearchQueryError(SearchError):
    """Raised when search query processing fails."""


class SortError(PaginationError):
    """Raised when sort operations fail."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.details = details or {}
        super().__init__(message)


class ValidationError(PaginationError):
    """Raised when generic validation fails."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        self.details = details or {}
        super().__init__(message)


__all__ = [
    "ConfigurationError",
    "FilterError",
    "FilterValidationError",
    "PaginationError",
    "SearchError",
    "SearchQueryError",
    "SortError",
    "ValidationError",
]
