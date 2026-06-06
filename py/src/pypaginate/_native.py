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
fallback. Filtering, sorting, ranked search (including fuzzy/token-sort and
per-field weights), and text normalization all run natively. ``normalize_text``
adds a bounded process-local cache over the native call (repeated field values
are common across rows), and is the single Python entry point for normalization.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pypaginate._core import (
    filter_group_indices,
    filter_indices,
    match_indices,
    normalize_text as _core_normalize,
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

_NORM_CACHE: dict[str, str] = {}
_NORM_CACHE_MAX = 8192


def normalize_text(value: str) -> str:
    """Normalize text for search and filtering (native), with a bounded cache.

    Delegates the actual NFKD accent-strip + case-fold + whitespace collapse to
    the native ``_core`` engine, so Python and Rust agree byte-for-byte; a
    bounded dict cache avoids the FFI hop for repeated field values.
    """
    result = _NORM_CACHE.get(value)
    if result is not None:
        return result
    result = _core_normalize(value)
    if len(_NORM_CACHE) < _NORM_CACHE_MAX:
        _NORM_CACHE[value] = result
    return result


def clear_normalize_cache() -> None:
    """Clear the ``normalize_text`` cache (free memory in long-lived processes)."""
    _NORM_CACHE.clear()


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


def match_filter(items: Sequence[Any], spec: SearchSpec) -> list[Any]:
    """Match-filter: keep items where any field matches the whole query, in
    original order (the in-memory search-backend semantics).

    ``EXACT`` fuzzy uses contains/prefix/exact per ``spec.mode``; fuzzy and
    token-sort gate by ``spec.threshold`` (rapidfuzz scoring in the engine).
    """
    rows = list(items)
    return _take(
        rows,
        lambda: match_indices(
            rows,
            spec.query,
            list(spec.fields),
            mode=_SEARCH_MODE[spec.mode],
            fuzzy=_FUZZY[spec.fuzzy],
            threshold=spec.threshold,
        ),
        SearchError,
    )


def search_stage_tuple(spec: SearchSpec) -> tuple[str, list[str], str, str, int]:
    """Search-stage tuple ``(query, fields, mode, fuzzy, threshold)`` for the
    resident ``Dataset.page`` search arg — a match-filter applied in the native
    filter -> search -> sort -> paginate pass (so explicit sorting still orders)."""
    return (
        spec.query,
        list(spec.fields),
        _SEARCH_MODE[spec.mode],
        _FUZZY[spec.fuzzy],
        spec.threshold,
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
    "clear_normalize_cache",
    "filter_and",
    "filter_group",
    "filter_logic",
    "match_filter",
    "normalize_text",
    "search",
    "search_stage_tuple",
    "sort_by",
    "sort_tuples",
]
