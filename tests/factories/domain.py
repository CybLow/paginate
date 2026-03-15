"""Factory functions for domain models.

Each function builds a single domain object with sensible
defaults that callers can override via keyword arguments.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.pages import CursorPage, OffsetPage
from pypaginate.domain.params import CursorParams, OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec


T = TypeVar("T")


# -- Params ------------------------------------------------------------------


def make_offset_params(page: int = 1, limit: int = 20) -> OffsetParams:
    """Build OffsetParams with defaults."""
    return OffsetParams(page=page, limit=limit)


def make_cursor_params(
    limit: int = 20,
    after: str | None = None,
    before: str | None = None,
) -> CursorParams:
    """Build CursorParams with defaults."""
    return CursorParams(limit=limit, after=after, before=before)


# -- Pages -------------------------------------------------------------------


def make_offset_page(
    items: list[Any] | None = None,
    total: int = 100,
    page: int = 1,
    limit: int = 20,
) -> OffsetPage[Any]:
    """Build OffsetPage with computed navigation flags."""
    items = items if items is not None else list(range(limit))
    return OffsetPage(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_next=page * limit < total,
        has_previous=page > 1,
    )


def make_cursor_page(
    items: list[Any] | None = None,
    limit: int = 20,
    next_cursor: str | None = None,
    previous_cursor: str | None = None,
) -> CursorPage[Any]:
    """Build CursorPage with defaults."""
    items = items if items is not None else list(range(limit))
    return CursorPage(
        items=items,
        limit=limit,
        has_next=next_cursor is not None,
        has_previous=previous_cursor is not None,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
    )


# -- Specs -------------------------------------------------------------------


def make_filter_spec(
    field: str = "age",
    operator: str = "eq",
    value: Any = 30,
) -> FilterSpec:
    """Build FilterSpec with defaults."""
    return FilterSpec(field=field, operator=operator, value=value)


def make_sort_spec(
    field: str = "name",
    direction: SortDirection = SortDirection.ASC,
) -> SortSpec:
    """Build SortSpec with defaults."""
    return SortSpec(field=field, direction=direction)


def make_search_spec(
    query: str = "test",
    fields: tuple[str, ...] = ("name",),
) -> SearchSpec:
    """Build SearchSpec with defaults."""
    return SearchSpec(query=query, fields=fields)


__all__ = [
    "make_cursor_page",
    "make_cursor_params",
    "make_filter_spec",
    "make_offset_page",
    "make_offset_params",
    "make_search_spec",
    "make_sort_spec",
]
