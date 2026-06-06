"""Test-only thin engine wrappers over :mod:`pypaginate._native`.

These classes previously lived in the shipped package (``pypaginate.filtering``,
``pypaginate.sorting``, ``pypaginate.search``). They were only ever a one-method
facade over the native ``_core`` engine and were consumed exclusively by the test
suite, so the v0.3 consolidation removed them from ``src/``: the shipped package
now exposes the in-memory engine via :mod:`pypaginate._native` directly, the
memory adapters (``pypaginate.adapters.memory.*``), and :class:`pypaginate.Dataset`.

They are kept here, in the test tree, so the existing behavioural assertions for
the filter / sort / search semantics continue to exercise the exact ``_native``
paths without re-introducing the indirection into the distributable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pypaginate import _native
from pypaginate.domain.specs import FilterGroup


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec


T = TypeVar("T")


class FilterEngine:
    """Apply filter specs or a nested ``FilterGroup`` via ``_native``."""

    __slots__ = ()

    def apply(
        self,
        items: Sequence[T],
        filters: Sequence[FilterSpec] | FilterGroup,
    ) -> list[T]:
        """Filter ``items`` by a flat spec list (each spec's logic) or a group."""
        if isinstance(filters, FilterGroup):
            return _native.filter_group(items, filters)
        if not filters:
            return list(items)
        return _native.filter_logic(items, filters)


class SortEngine:
    """Sort sequences by ordered ``SortSpec`` rules via ``_native``."""

    __slots__ = ()

    def apply(self, items: Sequence[T], sorting: Sequence[SortSpec]) -> list[T]:
        """Sort ``items`` by the given specs (direction + null placement)."""
        if not sorting:
            return list(items)
        return _native.sort_by(items, sorting)


class SearchEngine:
    """Ranked search over a ``SearchSpec`` via ``_native``."""

    __slots__ = ()

    def apply(self, items: Sequence[T], spec: SearchSpec) -> list[T]:
        """Filter and rank ``items`` by relevance (native ranked search)."""
        return _native.search(items, spec)


__all__ = ["FilterEngine", "SearchEngine", "SortEngine"]
