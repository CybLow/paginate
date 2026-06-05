"""In-memory filter backend.

Implements the ``FilterBackend`` protocol for Python sequences by delegating to
the native ``pypaginate._core`` engine: flat specs are combined with AND (the
established in-memory semantics) and matched rows are selected by index.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pypaginate import _native


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import FilterSpec


class MemoryFilterBackend:
    """Filter backend for in-memory sequences (native ``_core``)."""

    __slots__ = ()

    @staticmethod
    def apply_filters(
        query: object,
        filters: Sequence[FilterSpec],
    ) -> object:
        """Apply flat filter specs (combined with AND) to a sequence.

        Args:
            query: A Python sequence of items.
            filters: Filter specifications to apply.

        Returns:
            Filtered list of items matching all specs.
        """
        items = cast("Sequence[object]", query)
        if not filters:
            return list(items)
        return _native.filter_and(items, filters)


__all__ = ["MemoryFilterBackend"]
