"""Type stubs for the native ``paginate_core`` extension module.

Hand-maintained to mirror the PyO3 bindings (`crates/pyo3/src`). Shipped in the
wheel alongside `py.typed` so consumers and type checkers get full typing.
"""

from collections.abc import Sequence
from typing import Any

__version__: str

# Validation limits (DoS mitigation) — the single source of truth for every
# binding, mirrored by the TS package.
MAX_LIMIT: int
MAX_QUERY_LEN: int
MAX_FILTER_DEPTH: int

# -- typed exceptions --------------------------------------------------------

class PaginateError(ValueError):
    """Base error raised by the native engine (subclasses ``ValueError``)."""

class InvalidCursorError(PaginateError):
    """A cursor string was malformed, truncated, or tampered with."""

class FilterError(PaginateError):
    """A filter operator could not be applied."""

class SortError(PaginateError):
    """A sort could not be completed (e.g. incomparable values)."""

class SearchError(PaginateError):
    """A search query was invalid."""

# -- cursor codec ------------------------------------------------------------

def encode_cursor(values: Sequence[Any]) -> str: ...
def decode_cursor(cursor: str) -> tuple[Any, ...]: ...

# -- text --------------------------------------------------------------------

def normalize_text(value: str) -> str: ...

# -- pagination math ---------------------------------------------------------

def offset(page: int, limit: int) -> int: ...
def max_pages(total: int, limit: int) -> int: ...
def offset_meta(page: int, limit: int, total: int) -> tuple[int, int, bool, bool]: ...
def clamp_page(page: int, limit: int, total: int) -> int: ...

# -- input validation (raises ValueError on failure) -------------------------

def validate_offset(page: int, limit: int) -> None: ...
def validate_cursor(limit: int, has_after: bool, has_before: bool) -> None: ...
def validate_search_query(query: str) -> None: ...
def validate_filter_depth(depth: int) -> None: ...

# -- keyset (cursor) predicate -----------------------------------------------

def keyset_terms(ascending: Sequence[bool]) -> list[list[tuple[int, str]]]: ...

# -- one-shot in-memory engines (return indices into ``items``) --------------

def filter_indices(items: Sequence[Any], specs: Sequence[Any]) -> list[int]: ...
def filter_group_indices(items: Sequence[Any], group: Any) -> list[int]: ...
def sort_indices(items: Sequence[Any], specs: Sequence[Any]) -> list[int]: ...
def search_indices(
    items: Sequence[Any],
    query: str,
    fields: Sequence[str],
    mode: str = ...,
    fuzzy: str = ...,
    threshold: int = ...,
    min_length: int = ...,
    max_results: int | None = ...,
    weights: dict[str, float] | None = ...,
) -> list[int]: ...
def match_indices(
    items: Sequence[Any],
    query: str,
    fields: Sequence[str],
    mode: str = ...,
    fuzzy: str = ...,
    threshold: int = ...,
) -> list[int]: ...

# -- resident dataset --------------------------------------------------------

class Dataset:
    """An in-memory dataset held in Rust, queried by index (marshalled once)."""

    def __init__(self, items: Sequence[Any]) -> None: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def filter(self, specs: Sequence[Any]) -> list[int]: ...
    def sort(self, specs: Sequence[Any]) -> list[int]: ...
    def search(
        self,
        query: str,
        fields: Sequence[str],
        mode: str = ...,
        fuzzy: str = ...,
        threshold: int = ...,
        min_length: int = ...,
        max_results: int | None = ...,
    ) -> list[int]: ...
    def page(
        self,
        page: int,
        limit: int,
        filters: Sequence[Any] | None = ...,
        sorts: Sequence[Any] | None = ...,
        search: tuple[str, Sequence[str], str, str, int] | None = ...,
    ) -> dict[str, Any]: ...
