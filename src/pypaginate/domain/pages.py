"""Pagination result pages.

OffsetPage and CursorPage are separate types with clean schemas.
No null leakage — each page has only the fields for its mode.
"""

from __future__ import annotations

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, computed_field

from pypaginate.domain.params import CursorParams, OffsetParams


ItemT = TypeVar("ItemT")


class BasePage(BaseModel, Generic[ItemT]):
    """Shared result fields for all pagination modes."""

    model_config = ConfigDict(frozen=True)

    items: list[ItemT]
    limit: int
    has_next: bool
    has_previous: bool


class OffsetPage(BasePage[ItemT]):
    """Offset pagination result.

    All fields are non-optional — clean serialization.
    """

    total: int
    page: int

    @classmethod
    def create(
        cls,
        items: list[ItemT],
        total: int,
        params: OffsetParams,
    ) -> OffsetPage[ItemT]:
        """Build from offset pagination results.

        Args:
            items: Items for this page.
            total: Total item count across all pages.
            params: Offset parameters used.
        """
        max_pages = math.ceil(total / params.limit)
        return cls(
            items=items,
            limit=params.limit,
            has_next=params.page < max_pages,
            has_previous=params.page > 1,
            total=total,
            page=params.page,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pages(self) -> int:
        """Total number of pages."""
        return math.ceil(self.total / self.limit)


class CursorPage(BasePage[ItemT]):
    """Cursor pagination result.

    No total, no page — those are offset-only concepts.
    """

    next_cursor: str | None = None
    previous_cursor: str | None = None

    @classmethod
    def create(
        cls,
        items: list[ItemT],
        params: CursorParams,
        *,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
    ) -> CursorPage[ItemT]:
        """Build from cursor pagination results.

        Args:
            items: Items for this page.
            params: Cursor parameters used.
            next_cursor: Cursor for the next page.
            previous_cursor: Cursor for the previous page.
        """
        return cls(
            items=items,
            limit=params.limit,
            has_next=next_cursor is not None,
            has_previous=previous_cursor is not None,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )


__all__ = ["BasePage", "CursorPage", "OffsetPage"]
