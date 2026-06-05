"""In-memory sort backend.

Implements the ``SortBackend`` protocol for Python sequences by delegating to
the native ``pypaginate._core`` engine, which applies the ordered sort specs
(direction + null placement per key) and returns a row permutation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pypaginate import _native


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import SortSpec


class MemorySortBackend:
    """Sort backend for in-memory sequences (native ``_core``)."""

    __slots__ = ()

    @staticmethod
    def apply_sorting(
        query: object,
        sorting: Sequence[SortSpec],
    ) -> object:
        """Apply sort specs to a sequence.

        Args:
            query: A Python sequence of items.
            sorting: Sort specifications (applied in priority order).

        Returns:
            New sorted list of items.
        """
        items = cast("Sequence[object]", query)
        if not sorting:
            return list(items)
        return _native.sort_by(items, sorting)


__all__ = ["MemorySortBackend"]
