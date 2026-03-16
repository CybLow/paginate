"""FastAPI integration — Annotated dependency types.

Usage::

    from pypaginate.adapters.fastapi import OffsetDep, CursorDep
    from pypaginate.adapters.fastapi import FilterDep, FilterField
    from pypaginate.adapters.fastapi import SortDep, SearchDep
"""

from __future__ import annotations

from pypaginate.adapters.fastapi.dependencies import CursorDep, OffsetDep
from pypaginate.adapters.fastapi.filters import FilterDep, FilterField
from pypaginate.adapters.fastapi.search import SearchDep
from pypaginate.adapters.fastapi.sorting import SortDep


__all__ = [
    "CursorDep",
    "FilterDep",
    "FilterField",
    "OffsetDep",
    "SearchDep",
    "SortDep",
]
