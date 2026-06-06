"""Pagination input parameters — Elysia-style type inference.

Each params class contains only the fields relevant to its mode. The validation
rules and the ``MAX_LIMIT`` bound live **once** in the Rust core
(``pypaginate._core``) — shared with the TS package so they cannot drift, and so
no validator (Pydantic, zod, …) is load-bearing for them. These models are thin
holders that delegate to the core and re-raise its error as the public
:class:`ValidationError`.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from pypaginate._core import (
    MAX_LIMIT,
    clamp_page as _clamp_page,
    validate_cursor as _validate_cursor,
    validate_offset as _validate_offset,
)
from pypaginate.domain.exceptions import ValidationError


__all__ = ["MAX_LIMIT", "BaseParams", "CursorParams", "OffsetParams"]


class BaseParams(BaseModel):
    """Shared pagination input — just limit (concrete subclasses validate)."""

    model_config = ConfigDict(frozen=True)

    limit: int = 20


class OffsetParams(BaseParams):
    """Offset pagination input.

    Example::

        OffsetParams(page=2, limit=20)
    """

    page: int = 1

    @model_validator(mode="after")
    def _validate(self) -> Self:
        try:
            _validate_offset(self.page, self.limit)
        except ValueError as exc:  # the core raises a ValueError; surface it as ours
            raise ValidationError(str(exc)) from exc
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def offset(self) -> int:
        """Zero-based offset for database queries."""
        return (self.page - 1) * self.limit

    def clamp(self, total: int) -> Self:
        """Clamp the page number into valid bounds.

        Args:
            total: Total number of items available.

        Returns:
            New params clamped to the valid range, or ``self`` if already valid.
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
    def _validate(self) -> Self:
        try:
            _validate_cursor(self.limit, self.after is not None, self.before is not None)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return self
