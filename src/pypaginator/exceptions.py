"""Exceptions for pypaginator.

This module defines all custom exceptions used by the pagination system.
"""

from __future__ import annotations


class PaginatorException(Exception):
    """Base exception for all pypaginator errors."""

    pass


class PaginationConfigurationError(PaginatorException):
    """Raised when pagination configuration is invalid."""

    def __init__(self, field: str, value: object, reason: str) -> None:
        """Initialize the configuration error.

        Args:
            field: The field name that has invalid configuration.
            value: The invalid value.
            reason: Human-readable reason for the error.
        """
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {field}={value!r}: {reason}")


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


class SearchException(PaginatorException):
    """Raised when search operations fail."""

    pass


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

