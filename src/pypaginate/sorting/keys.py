"""Sort key building utilities.

Constructs callable sort keys that handle null placement and
direction for use with Python's built-in ``sorted()``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pypaginate.domain.enums import NullsPosition, SortDirection
from pypaginate.domain.exceptions import PaginationError
from pypaginate.filtering.accessor import get_value


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

    def _key(item: object) -> tuple[bool, Any]:
        value = _safe_get(item, field)
        if value is None:
            return not null_first, ""
        return null_first, value

    return _key


def _safe_get(item: object, field: str) -> Any:
    """Extract a field value, returning None on failure.

    Args:
        item: The item to extract from.
        field: Dotted field path.

    Returns:
        The field value, or None if not found.
    """
    try:
        return get_value(item, field)
    except PaginationError:
        return None


def _null_sorts_first(
    direction: SortDirection,
    nulls: NullsPosition,
) -> bool:
    """Determine whether nulls sort before non-null values.

    For DESC with LAST, nulls go to the logical end (sort first
    in reversed order). This function accounts for that inversion.

    Args:
        direction: Current sort direction.
        nulls: Requested null placement.

    Returns:
        True if nulls should appear first in the raw sort order.
    """
    wants_first = nulls is NullsPosition.FIRST
    is_desc = direction is SortDirection.DESC
    return wants_first != is_desc


__all__ = ["build_sort_key"]
