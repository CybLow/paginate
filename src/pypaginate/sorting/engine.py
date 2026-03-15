"""In-memory sort engine applying SortSpec sequences.

Applies multiple sort specifications in priority order using
Python's stable sort guarantee. Each spec controls direction
and null placement independently.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.exceptions import SortError
from pypaginate.domain.specs import SortSpec
from pypaginate.sorting.keys import build_sort_key


T = TypeVar("T")


class SortEngine:
    """Stateless engine that sorts sequences by SortSpec rules.

    Uses Python's stable sort: applies specs in reverse order
    so the first spec has highest priority.
    """

    def apply(self, items: Sequence[T], sorting: Sequence[SortSpec]) -> list[T]:
        """Sort items according to the given sort specifications.

        Args:
            items: Input sequence to sort.
            sorting: Sort specs in priority order (first = highest).

        Returns:
            New sorted list (original unchanged).

        Raises:
            SortError: If sorting fails for any reason.
        """
        if not sorting:
            return list(items)
        return self._apply_specs(list(items), sorting)

    def _apply_specs(self, result: list[T], sorting: Sequence[SortSpec]) -> list[T]:
        """Apply each spec in reverse for stable multi-key sorting.

        Args:
            result: Mutable list to sort in place.
            sorting: Sort specs to apply.

        Returns:
            The sorted list.
        """
        for spec in reversed(sorting):
            self._apply_single(result, spec)
        return result

    @staticmethod
    def _apply_single(result: list[T], spec: SortSpec) -> None:
        """Apply a single sort specification.

        Args:
            result: List to sort in place.
            spec: Sort spec defining field, direction, nulls.
        """
        try:
            key = build_sort_key(spec.field, spec.direction, spec.nulls)
            reverse = spec.direction is SortDirection.DESC
            result.sort(key=key, reverse=reverse)
        except (TypeError, AttributeError) as exc:
            raise SortError(str(exc), details={"field": spec.field}) from exc


__all__ = ["SortEngine"]
