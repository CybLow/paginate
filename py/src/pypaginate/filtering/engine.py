"""Filter engine applying filter specs or nested groups to sequences.

Delegates to the native ``pypaginate._core`` engine. Accepts a flat
``FilterSpec`` list (each spec's ``logic`` honored, AND/OR) or a nested
``FilterGroup`` built with the ``And`` / ``Or`` helpers — the core evaluates
the full And/Or tree and returns matching row indices.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pypaginate import _native
from pypaginate.domain.specs import FilterGroup


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import FilterSpec


T = TypeVar("T")


class FilterEngine:
    """Apply filter specifications to in-memory sequences via ``_core``."""

    __slots__ = ()

    def apply(
        self,
        items: Sequence[T],
        filters: Sequence[FilterSpec] | FilterGroup,
    ) -> list[T]:
        """Apply filters to items. Accepts a flat list or a nested FilterGroup.

        Args:
            items: Source sequence to filter.
            filters: FilterSpec list or FilterGroup (via And/Or builders).

        Returns:
            Filtered list of items matching the filter logic.
        """
        if isinstance(filters, FilterGroup):
            return _native.filter_group(items, filters)
        if not filters:
            return list(items)
        return _native.filter_logic(items, filters)


__all__ = ["FilterEngine"]
