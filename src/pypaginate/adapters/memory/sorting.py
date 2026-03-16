"""In-memory sort backend with partition-sort strategy.

Implements SortBackend protocol for Python sequences.
Partitions nulls from non-nulls, sorts non-nulls with a plain
key (no tuple wrapping), then concatenates for null placement.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypaginate.domain.enums import NullsPosition, SortDirection
from pypaginate.filtering.accessor import compile_accessor


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from pypaginate.domain.specs import SortSpec


class MemorySortBackend:
    """Sort backend for in-memory sequences."""

    __slots__ = ()

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
    """Sort items using partition-sort for null handling."""
    accessor = compile_accessor(spec.field)
    reverse = spec.direction is SortDirection.DESC
    nulls, non_nulls = _partition_nulls(items, accessor)

    non_nulls.sort(key=lambda item: accessor(item), reverse=reverse)  # type: ignore[arg-type,return-value]

    return _join_partitions(nulls, non_nulls, spec.nulls)


def _partition_nulls(
    items: list[object],
    accessor: Callable[[object], object],
) -> tuple[list[object], list[object]]:
    """Split items into null-valued and non-null-valued lists."""
    nulls: list[object] = []
    non_nulls: list[object] = []
    for item in items:
        if accessor(item) is None:
            nulls.append(item)
        else:
            non_nulls.append(item)
    return nulls, non_nulls


def _join_partitions(
    nulls: list[object],
    non_nulls: list[object],
    null_pos: NullsPosition,
) -> list[object]:
    """Concatenate partitions respecting null placement."""
    if null_pos is NullsPosition.FIRST:
        return nulls + non_nulls
    return non_nulls + nulls


__all__ = ["MemorySortBackend"]
