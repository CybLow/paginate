"""Sorting engine with natural ordering and tie-breaking.

This module provides sorting services with:
- Natural ordering with deterministic fallbacks
- Null value positioning (first/last)
- Reverse sorting
"""

from __future__ import annotations

from functools import partial
from numbers import Number
from operator import attrgetter
from typing import TYPE_CHECKING, Generic, Literal, TypeVar


if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")
"""Generic type variable for item types in sorting operations."""

Nulls = Literal["first", "last"]
"""Literal type for null value positioning in sort results."""


class SortEngine(Generic[T]):  # ← Renommé de SortService
    """Sort items using natural ordering with deterministic fallbacks."""

    # fmt: off
    @staticmethod
    def sort(items: list[T], sort_field: str, *, reverse: bool, nulls_position: Nulls, tie_breaker_field: str | None) -> list[T]:
        """Sort items by sort_field with stable tie-breaking.

        Args:
            items: List of items to sort (modified by index only).
            sort_field: Attribute name used for primary ordering.
            reverse: Whether to reverse the ordering.
            nulls_position: Where to place None values ("first"/"last").
            tie_breaker_field: Optional secondary attribute used for stable ordering.

        Returns:
            A new list with items sorted according to the provided options.
        """
        accessor = attrgetter(sort_field)
        tie_getter = attrgetter(tie_breaker_field) if tie_breaker_field else None
        indexed = list(enumerate(items))
        ordered, null_items = _partition_items(indexed, accessor)
        sorted_items = _sort_payloads(ordered, accessor=accessor, tie_getter=tie_getter, reverse=reverse)
        return _merge_nulls(sorted_items, null_items, nulls_position, reverse)
    # fmt: on


def _value_key(
    payload: tuple[int, T],
    *,
    accessor: Callable[[T], object],
    tie_getter: Callable[[T], object] | None,
) -> tuple[tuple[int, object], tuple[int, object], int]:
    """Build a composite sort key from payload including tie-breaker.

    Args:
        payload: Tuple of (index, item).
        accessor: Function to extract primary sort value.
        tie_getter: Optional function to extract tie-breaker value.

    Returns:
        Composite key tuple for sorting.
    """
    index, item = payload
    primary = accessor(item)
    tie_value = tie_getter(item) if tie_getter else None
    return _normalize(primary), _normalize(tie_value), index


def _partition_items(
    indexed: list[tuple[int, T]],
    accessor: Callable[[T], object],
) -> tuple[list[tuple[int, T]], list[T]]:
    """Partition indexed items into non-null and null groups.

    Args:
        indexed: List of (index, item) tuples.
        accessor: Function to extract sort value.

    Returns:
        Tuple of (non_null_payloads, null_items).
    """
    ordered = [payload for payload in indexed if accessor(payload[1]) is not None]
    null_items = [item for _, item in indexed if accessor(item) is None]
    return ordered, null_items


def _sort_payloads(
    payloads: list[tuple[int, T]],
    *,
    accessor: Callable[[T], object],
    tie_getter: Callable[[T], object] | None,
    reverse: bool,
) -> list[T]:
    """Sort payloads using tuple-based keys including tie-breakers.

    Args:
        payloads: List of (index, item) tuples.
        accessor: Function to extract primary sort value.
        tie_getter: Optional function to extract tie-breaker value.
        reverse: Whether to reverse the sort.

    Returns:
        Sorted list of items.
    """
    key = partial(_value_key, accessor=accessor, tie_getter=tie_getter)
    ordered = sorted(payloads, key=key, reverse=reverse)
    return [item for _, item in ordered]


def _merge_nulls(
    ordered: list[T],
    null_items: list[T],
    position: Nulls,
    reverse: bool,
) -> list[T]:
    """Merge None items before/after ordered results according to policy.

    Args:
        ordered: Sorted non-null items.
        null_items: Items with null sort values.
        position: Where to place nulls ("first"/"last").
        reverse: Whether sort is reversed.

    Returns:
        Merged list with nulls positioned correctly.
    """
    if _nulls_first(position, reverse):
        return [*null_items, *ordered]
    return [*ordered, *null_items]


def _nulls_first(position: Nulls, reverse: bool) -> bool:
    """Return True when nulls should be placed first for the settings.

    Args:
        position: Null position setting.
        reverse: Whether sort is reversed.

    Returns:
        True if nulls should be first.
    """
    if not reverse:
        return position == "first"
    return position == "last"


def _normalize(value: object) -> tuple[int, object]:
    """Normalize heterogeneous values into a sortable key tuple.

    Args:
        value: Value to normalize.

    Returns:
        Tuple of (type_priority, value) for sorting.
    """
    if value is None:
        return 2, ""
    if isinstance(value, Number):
        return 0, value
    if isinstance(value, str):
        return 1, value
    return 1, str(value)


def create_sort_service(
    *,
    _sort_method: Callable[..., list[object]] = SortEngine.sort,  # ← Mis à jour
) -> SortEngine[object]:  # ← Mis à jour
    """Return a stateless SortEngine instance.

    Args:
        _sort_method: Sort method reference for static analyzers.

    Returns:
        A new SortEngine instance.
    """
    _ = _sort_method
    return SortEngine()  # ← Mis à jour


# fmt: off
def sort_items(items: list[T], sort_field: str, *, reverse: bool, nulls_position: Nulls, tie_breaker_field: str | None) -> list[T]:
    """One-shot helper building a service and sorting items.

    Args:
        items: List of items to sort.
        sort_field: Attribute name used for primary ordering.
        reverse: Whether to reverse the ordering.
        nulls_position: Where to place None values.
        tie_breaker_field: Optional attribute used for stable ordering.

    Returns:
        The sorted list of items.
    """
    return SortEngine[T]().sort(
        items,
        sort_field,
        reverse=reverse,
        nulls_position=nulls_position,
        tie_breaker_field=tie_breaker_field,
    )
# fmt: on


__all__ = [
    "Nulls",
    "SortEngine",  # ← Mis à jour
    "create_sort_service",
    "sort_items",
]
