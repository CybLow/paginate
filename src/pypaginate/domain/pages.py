"""Pagination result pages.

OffsetPage and CursorPage are separate types with clean schemas.
No null leakage — each page has only the fields for its mode.

When msgspec is installed (``pypaginate[fast]``), page construction
uses msgspec.Struct for near-zero overhead. The returned object
duck-types as a Pydantic model with ``.model_dump()`` support.
"""

from __future__ import annotations

import math
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from pypaginate.domain.params import CursorParams, OffsetParams


ItemT = TypeVar("ItemT")

try:
    from pypaginate.domain.fast_pages import FastCursorPage, FastOffsetPage

    _HAS_MSGSPEC = True
except ImportError:
    _HAS_MSGSPEC = False


class BasePage(BaseModel, Generic[ItemT]):
    """Shared result fields for all pagination modes."""

    model_config = ConfigDict(frozen=True)

    items: list[ItemT]
    limit: int
    has_next: bool
    has_previous: bool

    def __iter__(self):  # type: ignore[override]  # noqa: ANN204
        """Iterate over items."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self.items)

    def __getitem__(self, index: int) -> ItemT:
        """Return item by index."""
        return self.items[index]


class OffsetPage(BasePage[ItemT]):
    """Offset pagination result.

    All fields are non-optional — clean serialization.
    """

    total: int
    page: int
    pages: int

    @classmethod
    def create(
        cls,
        items: list[ItemT],
        total: int,
        params: OffsetParams,
    ) -> Any:
        """Build from offset pagination results.

        Args:
            items: Items for this page.
            total: Total item count across all pages.
            params: Offset parameters used.

        Returns:
            OffsetPage or FastOffsetPage (if msgspec installed).
        """
        max_pages = math.ceil(total / params.limit)
        if _HAS_MSGSPEC:
            return FastOffsetPage(
                items=items,
                limit=params.limit,
                has_next=params.page < max_pages,
                has_previous=params.page > 1,
                total=total,
                page=params.page,
                pages=max_pages,
            )
        return cls(
            items=items,
            limit=params.limit,
            has_next=params.page < max_pages,
            has_previous=params.page > 1,
            total=total,
            page=params.page,
            pages=max_pages,
        )


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
    ) -> Any:
        """Build from cursor pagination results.

        Args:
            items: Items for this page.
            params: Cursor parameters used.
            next_cursor: Cursor for the next page.
            previous_cursor: Cursor for the previous page.

        Returns:
            CursorPage or FastCursorPage (if msgspec installed).
        """
        if _HAS_MSGSPEC:
            return FastCursorPage(
                items=items,
                limit=params.limit,
                has_next=next_cursor is not None,
                has_previous=previous_cursor is not None,
                next_cursor=next_cursor,
                previous_cursor=previous_cursor,
            )
        return cls(
            items=items,
            limit=params.limit,
            has_next=next_cursor is not None,
            has_previous=previous_cursor is not None,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )


__all__ = ["BasePage", "CursorPage", "OffsetPage"]
