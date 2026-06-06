"""User-facing specification objects for filtering, sorting, and search.

Specs are immutable Pydantic models that users construct to describe
what they want. Engines consume specs to execute the operations.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from pypaginate._core import (
    validate_filter_depth as _validate_filter_depth,
    validate_search_query as _validate_search_query,
)
from pypaginate.domain.enums import (
    FilterLogic,
    FuzzyMode,
    NullsPosition,
    SearchFieldMode,
    SortDirection,
)


FilterOperator = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "not_in",
    "contains",
    "starts_with",
    "ends_with",
    "like",
    "ilike",
    "between",
    "is_null",
    "is_not_null",
    "regex",
    "empty",
    "not_empty",
    "exists",
]
"""Supported filter operator names (type-checked at definition time)."""


class FilterSpec(BaseModel):
    """Declarative filter specification.

    Example::

        FilterSpec(field="age", operator="gte", value=18)
        FilterSpec(field="name", operator="contains", value="john")
    """

    model_config = ConfigDict(frozen=True)

    field: str
    operator: FilterOperator = "eq"
    value: Any = None
    logic: FilterLogic = FilterLogic.AND


class SortSpec(BaseModel):
    """Declarative sort specification.

    Example::

        SortSpec(field="name")
        SortSpec(field="created_at", direction=SortDirection.DESC)
    """

    model_config = ConfigDict(frozen=True)

    field: str
    direction: SortDirection = SortDirection.ASC
    nulls: NullsPosition = NullsPosition.LAST


class SearchSpec(BaseModel):
    """Declarative search specification.

    Example::

        SearchSpec(query="john doe", fields=("name", "email"))
        SearchSpec(query="jhn", fields=("name",), fuzzy=FuzzyMode.FUZZY)
        SearchSpec(query="alice", fields=("name", "bio"), weights={"name": 2.0})
    """

    model_config = ConfigDict(frozen=True)

    query: str
    fields: tuple[str, ...]
    weights: dict[str, float] | None = None
    mode: SearchFieldMode = SearchFieldMode.CONTAINS
    fuzzy: FuzzyMode = FuzzyMode.EXACT
    # Minimum trigram similarity (0-100) for FUZZY/TOKEN_SORT — pg_trgm's 0.3.
    threshold: int = 30
    min_length: int = 1
    max_results: int | None = None

    @field_validator("query")
    @classmethod
    def _check_query_length(cls, v: str) -> str:
        # Rule + limit live in the Rust core (shared with the TS package); the
        # ValueError it raises is wrapped by Pydantic into a ValidationError.
        _validate_search_query(v)
        return v


class FilterGroup(BaseModel):
    """Composite filter for nested AND/OR expressions.

    Use ``And()`` and ``Or()`` builder functions instead of
    constructing directly.

    Example::

        And(
            Or(FilterSpec(field="a", value=1), FilterSpec(field="b", value=2)),
            Or(FilterSpec(field="c", value=3), FilterSpec(field="d", value=4)),
        )
        # = (a=1 OR b=2) AND (c=3 OR d=4)
    """

    model_config = ConfigDict(frozen=True)

    logic: FilterLogic = FilterLogic.AND
    conditions: tuple[FilterSpec | FilterGroup, ...]

    @model_validator(mode="after")
    def _check_depth(self) -> FilterGroup:
        # Depth limit lives in the Rust core; we measure the tree here (it is a
        # Python object at construction) and let the core enforce the bound.
        _validate_filter_depth(_measure_depth(self))
        return self


def _measure_depth(group: FilterGroup) -> int:
    """Return the nesting depth of a FilterGroup tree."""
    max_child = 0
    for c in group.conditions:
        if isinstance(c, FilterGroup):
            max_child = max(max_child, _measure_depth(c))
    return 1 + max_child


def And(*conditions: FilterSpec | FilterGroup) -> FilterGroup:  # noqa: N802
    """Create an AND group of filter conditions."""
    return FilterGroup(logic=FilterLogic.AND, conditions=conditions)


def Or(*conditions: FilterSpec | FilterGroup) -> FilterGroup:  # noqa: N802
    """Create an OR group of filter conditions."""
    return FilterGroup(logic=FilterLogic.OR, conditions=conditions)


FilterInput = list[FilterSpec] | FilterGroup
"""Type alias for filter input accepted by engines and pipelines."""


__all__ = [
    "And",
    "FilterGroup",
    "FilterInput",
    "FilterOperator",
    "FilterSpec",
    "Or",
    "SearchSpec",
    "SortSpec",
]
