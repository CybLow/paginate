"""Pagination result pages.

OffsetPage and CursorPage are separate types with clean schemas.
No null leakage — each page has only the fields for its mode.

When msgspec is installed (``pypaginate[fast]``), page construction
uses msgspec.Struct for near-zero overhead. The returned object
duck-types as a Pydantic model with ``.model_dump()`` support.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar, cast

from pydantic import BaseModel, ConfigDict

from pypaginate._core import offset_meta as _offset_meta
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

    def __iter__(self) -> Iterator[ItemT]:  # ty: ignore[invalid-method-override]
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
    ) -> OffsetPage[ItemT]:
        """Build from offset pagination results.

        Args:
            items: Items for this page.
            total: Total item count across all pages.
            params: Offset parameters used.

        Returns:
            An ``OffsetPage`` (a ``FastOffsetPage`` when msgspec is installed,
            which duck-types it field-for-field with ``.model_dump()``).
        """
        # Page metadata comes from the native engine (single source of truth):
        # (page, pages, has_next, has_previous) — no Python recompute.
        page, pages, has_next, has_previous = _offset_meta(params.page, params.limit, total)
        if _HAS_MSGSPEC:
            # Cast at this single boundary so every caller gets a precise type.
            return cast(
                "OffsetPage[ItemT]",
                FastOffsetPage(
                    items=items,
                    limit=params.limit,
                    has_next=has_next,
                    has_previous=has_previous,
                    total=total,
                    page=page,
                    pages=pages,
                ),
            )
        return cls(
            items=items,
            limit=params.limit,
            has_next=has_next,
            has_previous=has_previous,
            total=total,
            page=page,
            pages=pages,
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
    ) -> CursorPage[ItemT]:
        """Build from cursor pagination results.

        Args:
            items: Items for this page.
            params: Cursor parameters used.
            next_cursor: Cursor for the next page.
            previous_cursor: Cursor for the previous page.

        Returns:
            A ``CursorPage`` (a ``FastCursorPage`` when msgspec is installed,
            which duck-types it field-for-field with ``.model_dump()``).
        """
        if _HAS_MSGSPEC:
            # Cast at this single boundary so every caller gets a precise type.
            return cast(
                "CursorPage[ItemT]",
                FastCursorPage(
                    items=items,
                    limit=params.limit,
                    has_next=next_cursor is not None,
                    has_previous=previous_cursor is not None,
                    next_cursor=next_cursor,
                    previous_cursor=previous_cursor,
                ),
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
