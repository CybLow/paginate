"""Pagination parameters — validated at construction by the Rust core.

The validation *rules* live once in the core (`paginate_core::validate`); these
thin dataclasses delegate to them and re-raise as the package's ValidationError.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pypaginate import _core
from pypaginate.errors import ValidationError


#: Maximum page size — the single source of truth, shared with the core + TS.
MAX_LIMIT: int = _core.MAX_LIMIT


def _checked(validate: Callable[[], None]) -> None:
    """Run a core validator, re-raising its ``ValueError`` as ``ValidationError``."""
    try:
        validate()
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class OffsetParams:
    """Offset pagination: a 1-based ``page`` and a ``limit`` (1..=MAX_LIMIT)."""

    page: int = 1
    limit: int = 20

    def __post_init__(self) -> None:
        _checked(lambda: _core.validate_offset(self.page, self.limit))

    @property
    def offset(self) -> int:
        """Zero-based row offset for this page."""
        return (self.page - 1) * self.limit


@dataclass(frozen=True, slots=True)
class CursorParams:
    """Cursor pagination: a ``limit`` and at most one of ``after`` / ``before``."""

    limit: int = 20
    after: str | None = None
    before: str | None = None

    def __post_init__(self) -> None:
        _checked(
            lambda: _core.validate_cursor(
                self.limit, self.after is not None, self.before is not None
            )
        )
