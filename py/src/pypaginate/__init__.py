"""pypaginate — fast, typed pagination over a Rust core.

Filter, sort, search, and offset-paginate in-memory; DB pagination is provided by
the optional adapters. The Rust core owns all computation *and* the type shapes
(generated from its JSON Schema); this package is the thin, typed Python face,
byte-for-byte compatible with the TS package (`@cyblow/paginate`).

    from pypaginate import paginate, OffsetParams

    page = paginate(users, OffsetParams(page=1, limit=20))
    page.total  # int
"""

from __future__ import annotations

from pypaginate import _core
from pypaginate.dataset import Dataset
from pypaginate.errors import (
    ConfigurationError,
    FilterError,
    FilterValidationError,
    InvalidCursorError,
    PaginateError,
    PaginationError,
    SearchError,
    SearchQueryError,
    SortError,
    ValidationError,
)
from pypaginate.pages import CursorPage, OffsetPage
from pypaginate.paginate import paginate
from pypaginate.params import MAX_LIMIT, CursorParams, OffsetParams
from pypaginate.query import filter, search, sort  # noqa: A004 (public API name)
from pypaginate.specs import (
    And,
    FilterGroup,
    FilterNode,
    FilterOperator,
    FilterSpec,
    FuzzyMode,
    NullsPosition,
    Or,
    SearchFieldMode,
    SearchSpec,
    SortDirection,
    SortSpec,
    search_spec,
)


__version__: str = _core.__version__

__all__ = [
    "MAX_LIMIT",
    "And",
    "ConfigurationError",
    "CursorPage",
    "CursorParams",
    "Dataset",
    "FilterError",
    "FilterGroup",
    "FilterNode",
    "FilterOperator",
    "FilterSpec",
    "FilterValidationError",
    "FuzzyMode",
    "InvalidCursorError",
    "NullsPosition",
    "OffsetPage",
    "OffsetParams",
    "Or",
    "PaginateError",
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
    "filter",
    "paginate",
    "search",
    "search_spec",
    "sort",
]
