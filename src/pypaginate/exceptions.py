"""Exceptions for pypaginate.

This module defines all custom exceptions used by the pagination system.
"""

from __future__ import annotations

from typing import Any


class PaginatorException(Exception):
    """Base exception for all pypaginate errors."""

    pass


class PaginationConfigurationError(PaginatorException):
    """Raised when pagination configuration is invalid."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: object = None,
        reason: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the configuration error.

        Args:
            message: Error message.
            field: Optional field name that has invalid configuration.
            value: Optional invalid value.
            reason: Optional human-readable reason for the error.
            details: Optional additional context details.
        """
        self.field = field
        self.value = value
        self.reason = reason
        self.details = details or {}
        super().__init__(message)


class FilterException(PaginatorException):
    """Raised when filtering operations fail."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize the filter exception.

        Args:
            message: Error message.
            field: Optional field name that caused the error.
        """
        self.field = field
        super().__init__(message)


class FilterValidationError(FilterException):
    """Raised when filter validation fails."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the filter validation error.

        Args:
            message: Error message.
            details: Optional additional context details.
        """
        self.details = details or {}
        super().__init__(message)


class SearchException(PaginatorException):
    """Raised when search operations fail."""

    pass


class SearchQueryError(SearchException):
    """Raised when search query processing fails."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the search query error.

        Args:
            message: Error message.
            details: Optional additional context details.
        """
        self.details = details or {}
        super().__init__(message)


class SearchNormalizationError(SearchException):
    """Raised when text normalization for search fails."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the search normalization error.

        Args:
            message: Error message.
            details: Optional additional context details.
        """
        self.details = details or {}
        super().__init__(message)


class SortException(PaginatorException):
    """Raised when sort operations fail."""

    pass


class ValidationException(PaginatorException):
    """Raised when validation fails."""

    def __init__(self, field: str, value: object, reason: str) -> None:
        """Initialize the validation exception.

        Args:
            field: The field name that failed validation.
            value: The invalid value.
            reason: Human-readable reason for the validation failure.
        """
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Validation failed for {field}={value!r}: {reason}")
