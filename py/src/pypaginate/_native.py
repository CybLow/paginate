"""Bridge from the package's specs to the bundled native ``_core`` engine.

Marshals the generated dataclass specs into the plain wire-forms ``_core``
accepts, runs the pure engine, and lets callers select host rows by the returned
indices. Engine-boundary errors (a bad operator/field) are normalized to the
package's ``FilterError`` / ``SortError`` / ``SearchError``. Spec defaults are
applied here because the generated shapes leave them ``Optional``.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from pypaginate import _core
from pypaginate.errors import FilterError, SearchError, SortError
from pypaginate.pages import OffsetPage
from pypaginate.params import OffsetParams
from pypaginate.specs import FilterGroup, FilterSpec, SearchSpec, SortSpec


_NORM_CACHE: dict[str, str] = {}
_NORM_CACHE_MAX = 8192

#: Wire-form tuples the engine accepts.
FilterTuple = tuple[str, str, Any, str]
SortTuple = tuple[str, str, str]
SearchStage = tuple[str, list[str], str, str, int]


def normalize_text(value: str) -> str:
    """Normalize text via the native engine, with a bounded process cache."""
    cached = _NORM_CACHE.get(value)
    if cached is not None:
        return cached
    result = _core.normalize_text(value)
    if len(_NORM_CACHE) < _NORM_CACHE_MAX:
        _NORM_CACHE[value] = result
    return result


def clear_normalize_cache() -> None:
    """Clear the ``normalize_text`` cache (free memory in long-lived processes)."""
    _NORM_CACHE.clear()


def _filter_tuple(spec: FilterSpec) -> FilterTuple:
    return (spec.field, spec.operator, spec.value, spec.logic or "and")


def _sort_tuple(spec: SortSpec) -> SortTuple:
    return spec.field, spec.direction or "asc", spec.nulls or "last"


def filter_tuples(filters: Sequence[FilterSpec]) -> list[FilterTuple]:
    """Flat filter wire-tuples (each spec keeps its own AND/OR ``logic``)."""
    return [_filter_tuple(f) for f in filters]


def sort_tuples(sorting: Sequence[SortSpec]) -> list[SortTuple]:
    """Sort wire-tuples ``(field, direction, null placement)``."""
    return [_sort_tuple(s) for s in sorting]


def search_stage(spec: SearchSpec) -> SearchStage:
    """Match-filter search-stage tuple for the resident ``Dataset.page`` pass."""
    threshold = spec.threshold if spec.threshold is not None else 30
    return (
        spec.query,
        list(spec.fields),
        spec.mode or "contains",
        spec.fuzzy or "exact",
        threshold,
    )


def _to_node(node: FilterSpec | FilterGroup) -> Any:
    """Convert a spec/group tree to the recursive tuple form ``_core`` expects."""
    if isinstance(node, FilterGroup):
        return (node.logic, [_to_node(c) for c in node.conditions])
    return _filter_tuple(node)


def _run(indices: Callable[[], list[int]], error: type[Exception]) -> list[int]:
    """Run a native index query, normalizing engine errors to ``error``."""
    try:
        return indices()
    except (KeyError, ValueError) as exc:
        raise error(str(exc)) from exc


def filter_indices(rows: Sequence[Any], filters: Sequence[FilterSpec]) -> list[int]:
    """Indices of ``rows`` matching the flat ``filters``."""
    specs = filter_tuples(filters)
    return _run(lambda: _core.filter_indices(rows, specs), FilterError)


def filter_group_indices(rows: Sequence[Any], group: FilterGroup) -> list[int]:
    """Indices of ``rows`` matching a nested ``And`` / ``Or`` group."""
    node = _to_node(group)
    return _run(lambda: _core.filter_group_indices(rows, node), FilterError)


def sort_indices(rows: Sequence[Any], sorting: Sequence[SortSpec]) -> list[int]:
    """Index permutation sorting ``rows`` by ``sorting`` (stable, null-aware)."""
    specs = sort_tuples(sorting)
    return _run(lambda: _core.sort_indices(rows, specs), SortError)


def _search_args(rows: Sequence[Any], spec: SearchSpec) -> tuple[Any, ...]:
    return (
        rows,
        spec.query,
        list(spec.fields),
        spec.mode or "contains",
        spec.fuzzy or "exact",
        spec.threshold if spec.threshold is not None else 30,
        spec.min_length if spec.min_length is not None else 1,
        spec.max_results,
        dict(spec.weights) if spec.weights else None,
    )


def search_indices(rows: Sequence[Any], spec: SearchSpec) -> list[int]:
    """Ranked-search indices over ``spec.fields`` (relevance order)."""
    return _run(lambda: _core.search_indices(*_search_args(rows, spec)), SearchError)


def build_offset_page(items: list[Any], total: int, params: OffsetParams) -> OffsetPage[Any]:
    """Build an :class:`OffsetPage` with core-derived metadata."""
    page, pages, has_next, has_previous = _core.offset_meta(params.page, params.limit, total)
    return OffsetPage(
        items=items,
        total=total,
        page=page,
        pages=pages,
        limit=params.limit,
        has_next=has_next,
        has_previous=has_previous,
    )
