"""FastAPI integration — query-param dependencies for pypaginate.

from pypaginate.adapters.fastapi import (
    OffsetDep,
    CursorDep,
    SortDep,
    SearchDep,
    FilterDep,
    FilterField,
)
"""

from __future__ import annotations

from pypaginate.adapters.fastapi.dependencies import (
    CursorDep,
    OffsetDep,
    SearchDep,
    SortDep,
    cursor_params,
    offset_params,
    parse_search,
    parse_sort,
    search_params,
    sort_params,
)
from pypaginate.adapters.fastapi.filters import FilterDep, FilterField


__all__ = [
    "CursorDep",
    "FilterDep",
    "FilterField",
    "OffsetDep",
    "SearchDep",
    "SortDep",
    "cursor_params",
    "offset_params",
    "parse_search",
    "parse_sort",
    "search_params",
    "sort_params",
]
