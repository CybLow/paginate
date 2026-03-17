"""Sort key building utilities.

Constructs callable sort keys that handle null placement and
direction for use with Python's built-in ``sorted()``.

Uses compiled field accessors to avoid per-item string splitting.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pypaginate.domain.enums import NullsPosition, SortDirection
from pypaginate.domain.exceptions import PaginationError
from pypaginate.filtering.accessor import compile_accessor


def build_sort_key(
    field: str,
    direction: SortDirection,
    nulls: NullsPosition,
) -> Callable[[object], tuple[bool, Any]]:
    """Build a sort key function for a single field.

    Returns a tuple key ``(is_null_flag, value)`` so that nulls
    sort to the requested position independently of direction.

    Args:
        field: Dotted field path to extract.
        direction: ASC or DESC ordering.
        nulls: Where to place None values.

    Returns:
        A callable that produces a sortable tuple from an item.
    """
    null_first = _null_sorts_first(direction, nulls)
    accessor = compile_accessor(field)

    def _key(item: object) -> tuple[bool, Any]:
        value = _safe_get(item, accessor)
        if value is None:
            return not null_first, ""
        return null_first, value

    return _key


def _safe_get(
    item: object,
    accessor: Callable[[object], object],
) -> Any:
    """Extract a field value, returning None on failure."""
    try:
        return accessor(item)
    except PaginationError:
        return None


def _null_sorts_first(
    direction: SortDirection,
    nulls: NullsPosition,
) -> bool:
    """Determine whether nulls sort before non-null values."""
    wants_first = nulls is NullsPosition.FIRST
    is_desc = direction is SortDirection.DESC
    return wants_first != is_desc


__all__ = ["build_sort_key"]
