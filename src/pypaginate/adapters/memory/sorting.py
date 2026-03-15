"""In-memory sort backend delegating to sort key builder.

Implements SortBackend protocol for Python sequences.
Uses the sort key builder for null-aware, direction-aware ordering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypaginate.domain.enums import SortDirection


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import SortSpec


class MemorySortBackend:
    """Sort backend for in-memory sequences.

    Satisfies ``SortBackend`` protocol by building composite
    sort keys from SortSpec instances and applying them.
    """

    @staticmethod
    def apply_sorting(
        query: object,
        sorting: Sequence[SortSpec],
    ) -> object:
        """Apply sort specs to a sequence.

        Args:
            query: A Python sequence of items.
            sorting: Sort specifications (applied in order).

        Returns:
            New sorted list of items.
        """
        items = list(query)  # type: ignore[call-overload]
        for spec in reversed(sorting):
            items = _sort_by_spec(items, spec)
        return items


def _sort_by_spec(items: list[object], spec: SortSpec) -> list[object]:
    """Sort items by a single sort specification."""
    reverse = spec.direction is SortDirection.DESC
    return sorted(
        items,
        key=lambda item: _sort_key(item, spec.field),
        reverse=reverse,
    )


def _sort_key(item: object, field: str) -> tuple[bool, object]:
    """Build a sort key placing None values last.

    Args:
        item: The item to extract a sort value from.
        field: Dotted field path to extract.

    Returns:
        Tuple of (is_none, value) for stable null ordering.
    """
    from pypaginate.filtering.accessor import get_value

    value = get_value(item, field)
    if value is None:
        return True, ""
    return False, value


__all__ = ["MemorySortBackend"]
