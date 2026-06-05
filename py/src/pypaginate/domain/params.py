"""Pagination input parameters — Elysia-style type inference.

Each params class contains only the fields relevant to its mode.
Illegal states are unrepresentable.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from pypaginate._core import clamp_page as _clamp_page
from pypaginate.domain.exceptions import ValidationError


MAX_LIMIT = 1000
"""Maximum allowed page limit (DoS mitigation)."""


def _validate_limit(value: int) -> None:
    if value < 1:
        raise ValidationError(
            "limit must be >= 1",
            field="limit",
            details={"limit": value},
        )
    if value > MAX_LIMIT:
        raise ValidationError(
            f"limit must not exceed {MAX_LIMIT}",
            field="limit",
            details={"limit": value, "max": MAX_LIMIT},
        )


class BaseParams(BaseModel):
    """Shared pagination input — just limit."""

    model_config = ConfigDict(frozen=True)

    limit: int = 20

    @model_validator(mode="after")
    def _check_limit(self) -> Self:
        _validate_limit(self.limit)
        return self


class OffsetParams(BaseParams):
    """Offset pagination input.

    Example::

        OffsetParams(page=2, limit=20)
    """

    page: int = 1

    @model_validator(mode="after")
    def _check_page(self) -> Self:
        if self.page < 1:
            raise ValidationError(
                "page must be >= 1",
                field="page",
                details={"page": self.page},
            )
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def offset(self) -> int:
        """Zero-based offset for database queries."""
        return (self.page - 1) * self.limit

    def clamp(self, total: int) -> Self:
        """Clamp page number to valid bounds.

        Args:
            total: Total number of items available.

        Returns:
            New params clamped to valid range, or self if valid.
        """
        # Clamp math lives in the native engine (single source of truth). Guard
        # negative totals at 0 so the u64 boundary never rejects them.
        safe_page = _clamp_page(self.page, self.limit, max(total, 0))
        if safe_page == self.page:
            return self
        return self.model_copy(update={"page": safe_page})


class CursorParams(BaseParams):
    """Cursor pagination input.

    Example::

        CursorParams(limit=20, after="abc123")
        CursorParams(limit=20, before="xyz789")
    """

    after: str | None = None
    before: str | None = None

    @model_validator(mode="after")
    def _check_exclusivity(self) -> Self:
        if self.after is not None and self.before is not None:
            raise ValidationError(
                "after and before are mutually exclusive",
            )
        return self


__all__ = ["MAX_LIMIT", "BaseParams", "CursorParams", "OffsetParams"]
