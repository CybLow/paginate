"""Sort engine applying SortSpec sequences to in-memory sequences.

Delegates to the native ``pypaginate._core`` engine, which applies the ordered
sort specs (each controlling direction and null placement) and returns a row
permutation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pypaginate import _native


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import SortSpec


T = TypeVar("T")


class SortEngine:
    """Stateless engine that sorts sequences by SortSpec rules (native)."""

    __slots__ = ()

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
        return _native.sort_by(items, sorting)


__all__ = ["SortEngine"]
