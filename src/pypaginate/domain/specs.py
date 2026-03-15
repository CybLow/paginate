"""User-facing specification objects for filtering, sorting, and search.

Specs are immutable Pydantic models that users construct to describe
what they want. Engines consume specs to execute the operations.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

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
    """

    model_config = ConfigDict(frozen=True)

    query: str
    fields: tuple[str, ...]
    mode: SearchFieldMode = SearchFieldMode.CONTAINS
    fuzzy: FuzzyMode = FuzzyMode.EXACT
    threshold: int = 75


__all__ = ["FilterOperator", "FilterSpec", "SearchSpec", "SortSpec"]
