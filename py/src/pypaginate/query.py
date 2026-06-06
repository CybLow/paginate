"""One-shot filter / sort / search over in-memory sequences.

The ergonomic complement to :func:`pypaginate.paginate`: filter, sort, or search
a list directly through the native engine. Each returns a new list of matching
host items (search in ranked relevance order).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from pypaginate import _native
from pypaginate.specs import FilterGroup, FilterSpec, SearchSpec, SortSpec


ItemT = TypeVar("ItemT")

#: A single spec, a sequence of them (each keeps its own logic), or a group.
FilterWhere = FilterSpec | Sequence[FilterSpec] | FilterGroup
#: A single sort key or a sequence applied in priority order.
SortBy = SortSpec | Sequence[SortSpec]


def filter(items: Sequence[ItemT], where: FilterWhere) -> list[ItemT]:  # noqa: A001
    """Return the items matching ``where``, in original order."""
    rows = list(items)
    if isinstance(where, FilterGroup):
        indices = _native.filter_group_indices(rows, where)
    else:
        specs = [where] if isinstance(where, FilterSpec) else list(where)
        indices = _native.filter_indices(rows, specs)
    return [rows[i] for i in indices]


def sort(items: Sequence[ItemT], by: SortBy) -> list[ItemT]:
    """Return the items ordered by ``by`` (stable, null-aware)."""
    rows = list(items)
    specs = [by] if isinstance(by, SortSpec) else list(by)
    return [rows[i] for i in _native.sort_indices(rows, specs)]


def search(items: Sequence[ItemT], spec: SearchSpec) -> list[ItemT]:
    """Return the items matching ``spec`` in ranked (relevance) order."""
    rows = list(items)
    return [rows[i] for i in _native.search_indices(rows, spec)]


__all__ = ["FilterWhere", "SortBy", "filter", "search", "sort"]
