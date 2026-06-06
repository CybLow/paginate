"""One-shot query helpers over in-memory sequences.

The ergonomic complement to :func:`pypaginate.paginate`: filter, sort, or search
a list directly through the native engine, without constructing a backend. Each
returns a new list of the matching host items (search in ranked order)::

    from pypaginate import (
        search,
        filter,
        sort,
        FilterSpec,
        SortSpec,
        SearchSpec,
        SortDirection,
    )

    adults = filter(users, FilterSpec(field="age", operator="gte", value=18))
    newest = sort(users, SortSpec(field="created_at", direction=SortDirection.DESC))
    hits = search(users, SearchSpec(query="alice", fields=("name", "email")))
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pypaginate import _native
from pypaginate.domain.specs import FilterGroup, FilterSpec, SearchSpec, SortSpec


if TYPE_CHECKING:
    from collections.abc import Sequence

    FilterWhere = FilterSpec | Sequence[FilterSpec] | FilterGroup
    SortBy = SortSpec | Sequence[SortSpec]


ItemT = TypeVar("ItemT")


def filter(items: Sequence[ItemT], where: FilterWhere) -> list[ItemT]:  # noqa: A001
    """Return the items matching ``where``, in original order.

    ``where`` is a single :class:`FilterSpec`, a sequence of them (each spec's
    own ``logic`` decides AND/OR), or a nested :class:`FilterGroup`.
    """
    if isinstance(where, FilterGroup):
        return _native.filter_group(items, where)
    specs = [where] if isinstance(where, FilterSpec) else list(where)
    return _native.filter_logic(items, specs)


def sort(items: Sequence[ItemT], by: SortBy) -> list[ItemT]:
    """Return the items ordered by ``by`` (a single :class:`SortSpec` or a
    sequence applied in priority order); the sort is stable."""
    specs = [by] if isinstance(by, SortSpec) else list(by)
    return _native.sort_by(items, specs)


def search(items: Sequence[ItemT], spec: SearchSpec) -> list[ItemT]:
    """Return the items matching ``spec`` in ranked (relevance) order.

    Supports exact/prefix/contains matching, fuzzy / token-sort scoring, and
    optional per-field weights — see :class:`SearchSpec`.
    """
    return _native.search(items, spec)


__all__ = ["filter", "search", "sort"]
