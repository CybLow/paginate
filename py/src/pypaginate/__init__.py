"""pypaginate — Universal pagination toolkit for Python.

Input type determines output type (Elysia-style inference)::

    from pypaginate import paginate, OffsetParams

    page = paginate(users, OffsetParams(page=1, limit=20))
    page.total  # int — auto-inferred as OffsetPage

    from pypaginate import CursorParams

    page = await paginate(query, CursorParams(after="abc"), backend=backend)
    page.next_cursor  # str | None — auto-inferred as CursorPage
"""

from __future__ import annotations

from pypaginate._dispatch import paginate
from pypaginate.dataset import Dataset
from pypaginate.domain.enums import (
    FilterLogic,
    FuzzyMode,
    NullsPosition,
    OverflowStrategy,
    SearchFieldMode,
    SortDirection,
)
from pypaginate.domain.exceptions import (
    ConfigurationError,
    FilterError,
    FilterValidationError,
    PaginationError,
    SearchError,
    SearchQueryError,
    SortError,
    ValidationError,
)
from pypaginate.domain.pages import CursorPage, OffsetPage
from pypaginate.domain.params import CursorParams, OffsetParams
from pypaginate.domain.specs import And, FilterGroup, FilterSpec, Or, SearchSpec, SortSpec


__version__ = "0.2.0"

__all__ = [
    "And",
    "ConfigurationError",
    "CursorPage",
    "CursorParams",
    "Dataset",
    "FilterError",
    "FilterGroup",
    "FilterLogic",
    "FilterSpec",
    "FilterValidationError",
    "FuzzyMode",
    "NullsPosition",
    "OffsetPage",
    "OffsetParams",
    "Or",
    "OverflowStrategy",
    "PaginationError",
    "SearchError",
    "SearchFieldMode",
    "SearchQueryError",
    "SearchSpec",
    "SortDirection",
    "SortError",
    "SortSpec",
    "ValidationError",
    "__version__",
    "paginate",
]
