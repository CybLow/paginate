"""Filter / sort / search specifications + boolean-group builders.

The data shapes are generated from the Rust core's JSON Schema (see
``pypaginate._generated.types``); this module re-exports them and adds the
``And`` / ``Or`` builders with construction-time nesting-depth validation and a
validated ``search_spec`` factory — both delegating their limits to the core.
"""

from __future__ import annotations

from pypaginate import _core
from pypaginate._generated.types import (
    FilterGroup,
    FilterNode,
    FilterOperator,
    FilterSpec,
    FuzzyMode,
    NullsPosition,
    SearchFieldMode,
    SearchSpec,
    SortDirection,
    SortSpec,
)
from pypaginate.errors import FilterValidationError, SearchQueryError


def _measure_depth(group: FilterGroup) -> int:
    """Nesting depth: ``1 + deepest nested group`` (a leaves-only group is 1)."""
    deepest = 0
    for condition in group.conditions:
        if isinstance(condition, FilterGroup):
            deepest = max(deepest, _measure_depth(condition))
    return 1 + deepest


def _checked_group(group: FilterGroup) -> FilterGroup:
    """Validate a group's depth against the core limit before returning it."""
    try:
        _core.validate_filter_depth(_measure_depth(group))
    except ValueError as exc:
        raise FilterValidationError(str(exc)) from exc
    return group


def And(*conditions: FilterSpec | FilterGroup) -> FilterGroup:  # noqa: N802
    """Build an AND group of conditions (validates nesting depth at construction)."""
    return _checked_group(FilterGroup(logic="and", conditions=list(conditions)))


def Or(*conditions: FilterSpec | FilterGroup) -> FilterGroup:  # noqa: N802
    """Build an OR group of conditions (validates nesting depth at construction)."""
    return _checked_group(FilterGroup(logic="or", conditions=list(conditions)))


def search_spec(spec: SearchSpec) -> SearchSpec:
    """Validate a search spec's query length against the core limit, then return it."""
    try:
        _core.validate_search_query(spec.query)
    except ValueError as exc:
        raise SearchQueryError(str(exc)) from exc
    return spec


__all__ = [
    "And",
    "FilterGroup",
    "FilterNode",
    "FilterOperator",
    "FilterSpec",
    "FuzzyMode",
    "NullsPosition",
    "Or",
    "SearchFieldMode",
    "SearchSpec",
    "SortDirection",
    "SortSpec",
    "search_spec",
]
