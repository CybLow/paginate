"""Exception hierarchy — mirrors the TS package's ``errors.ts``.

Every error carries a structured ``details`` mapping for programmatic handling.
"""

from __future__ import annotations

from typing import Any


class PaginateError(Exception):
    """Base error for all paginate failures (aliased as ``PaginationError``)."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.details = details or {}
        super().__init__(message)


#: Cross-language alias — pypaginate historically named the base ``PaginationError``.
PaginationError = PaginateError


class ConfigurationError(PaginateError):
    """Invalid pagination configuration."""


class FilterError(PaginateError):
    """A filtering operation failed (optionally naming the ``field``)."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        super().__init__(message, details=details)


class FilterValidationError(FilterError):
    """A filter specification failed validation."""


class SearchError(PaginateError):
    """A search operation failed."""


class SearchQueryError(SearchError):
    """Search query processing failed."""


class SortError(PaginateError):
    """A sort operation failed."""


class ValidationError(PaginateError):
    """Generic input validation failure (bad page/limit, malformed cursor, ...)."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        super().__init__(message, details=details)
