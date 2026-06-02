"""Bridge from domain specs to the bundled native ``_core`` engine.

pypaginate runs all in-memory filtering, sorting, and ranked search through the
Rust ``pypaginate._core`` engine. This module is the single translation point:

* it converts the domain specs (``FilterSpec`` / ``FilterGroup`` / ``SortSpec`` /
  ``SearchSpec``) into the wire-forms the engine accepts,
* selects the original host items by the row indices the engine returns, and
* normalizes the engine's boundary errors — a ``KeyError`` for a missing field,
  a ``ValueError`` for a bad operator or operand — into the domain exception
  hierarchy, so callers always see ``FilterError`` / ``SortError`` / ``SearchError``
  regardless of the engine underneath.

The engine is mandatory (built into the wheel); there is no pure-Python
fallback. Filtering, sorting, and ranked search (including fuzzy/token-sort and
per-field weights) all run natively.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pypaginate._core import (
    filter_group_indices,
    filter_indices,
    match_indices,
    search_indices,
    sort_indices,
)
from pypaginate.domain.enums import (
    FilterLogic,
    FuzzyMode,
    NullsPosition,
    SearchFieldMode,
    SortDirection,
)
from pypaginate.domain.exceptions import FilterError, SearchError, SortError
from pypaginate.domain.specs import FilterGroup


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec

_LOGIC = {FilterLogic.AND: "and", FilterLogic.OR: "or"}
_DIRECTION = {SortDirection.ASC: "asc", SortDirection.DESC: "desc"}
_NULLS = {NullsPosition.FIRST: "first", NullsPosition.LAST: "last"}
_SEARCH_MODE = {
    SearchFieldMode.PREFIX: "prefix",
    SearchFieldMode.CONTAINS: "contains",
    SearchFieldMode.EXACT: "exact",
}
_FUZZY = {
    FuzzyMode.EXACT: "exact",
    FuzzyMode.FUZZY: "fuzzy",
    FuzzyMode.TOKEN_SORT: "token_sort",
}


def and_filter_tuples(
    filters: Sequence[FilterSpec],
) -> list[tuple[str, str, Any, str]]:
    """Flat spec tuples combined with AND (resident Dataset + memory backend)."""
    return [(f.field, f.operator, f.value, "and") for f in filters]


def sort_tuples(sorting: Sequence[SortSpec]) -> list[tuple[str, str, str]]:
    """Sort spec tuples ``(field, direction, null placement)`` for the engine."""
    return [(s.field, _DIRECTION[s.direction], _NULLS[s.nulls]) for s in sorting]


def filter_and(items: Sequence[Any], filters: Sequence[FilterSpec]) -> list[Any]:
    """Filter flat specs combined with AND (in-memory backend semantics)."""
    rows = list(items)
    specs = and_filter_tuples(filters)
    return _take(rows, lambda: filter_indices(rows, specs), FilterError)


def filter_logic(items: Sequence[Any], filters: Sequence[FilterSpec]) -> list[Any]:
    """Filter flat specs, honoring each spec's own AND/OR ``logic``."""
    rows = list(items)
    specs = [(f.field, f.operator, f.value, _LOGIC[f.logic]) for f in filters]
    return _take(rows, lambda: filter_indices(rows, specs), FilterError)


def filter_group(items: Sequence[Any], group: FilterGroup) -> list[Any]:
    """Filter by a nested ``FilterGroup`` (And/Or tree)."""
    rows = list(items)
    node = _to_node(group)
    return _take(rows, lambda: filter_group_indices(rows, node), FilterError)


def sort_by(items: Sequence[Any], sorting: Sequence[SortSpec]) -> list[Any]:
    """Sort by ordered sort specs (direction + null placement per key)."""
    rows = list(items)
    specs = sort_tuples(sorting)
    return _take(rows, lambda: sort_indices(rows, specs), SortError)


def search(items: Sequence[Any], spec: SearchSpec) -> list[Any]:
    """Ranked search via the native engine.

    Supports exact/prefix/contains matching, fuzzy / token-sort scoring, and
    optional per-field weights; returns items in ranked (relevance) order.
    """
    rows = list(items)
    return _take(
        rows,
        lambda: search_indices(
            rows,
            spec.query,
            list(spec.fields),
            mode=_SEARCH_MODE[spec.mode],
            fuzzy=_FUZZY[spec.fuzzy],
            threshold=spec.threshold,
            min_length=spec.min_length,
            max_results=spec.max_results,
            weights=dict(spec.weights) if spec.weights else None,
        ),
        SearchError,
    )


def match_filter(
    items: Sequence[Any],
    query: str,
    fields: Sequence[str],
    mode: SearchFieldMode,
) -> list[Any]:
    """Match-filter (exact/prefix/contains): keep items where any field matches
    the whole query, in original order (the in-memory search-backend semantics)."""
    rows = list(items)
    return _take(
        rows,
        lambda: match_indices(rows, query, list(fields), mode=_SEARCH_MODE[mode]),
        SearchError,
    )


def _take(
    rows: list[Any],
    indices: Callable[[], list[int]],
    error: type[FilterError | SortError | SearchError],
) -> list[Any]:
    """Run a native index query, normalize errors, and select matched rows."""
    try:
        return [rows[i] for i in indices()]
    except (KeyError, ValueError) as exc:
        raise error(str(exc)) from exc


def _to_node(node: FilterSpec | FilterGroup) -> Any:
    """Convert a FilterSpec/FilterGroup tree to the recursive ``_core`` form."""
    if isinstance(node, FilterGroup):
        return (_LOGIC[node.logic], [_to_node(c) for c in node.conditions])
    return (node.field, node.operator, node.value, _LOGIC[node.logic])


__all__ = [
    "and_filter_tuples",
    "filter_and",
    "filter_group",
    "filter_logic",
    "match_filter",
    "search",
    "sort_by",
    "sort_tuples",
]
