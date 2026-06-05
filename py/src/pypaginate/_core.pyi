"""Type stubs for the native ``paginate_core`` extension module.

Hand-maintained to mirror the PyO3 bindings (`crates/py/src`). Shipped in the
wheel alongside `py.typed` so consumers and mypy get full typing.
"""

from collections.abc import Sequence
from typing import Any

__version__: str

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
    def match_filter(
        self,
        query: str,
        fields: Sequence[str],
        mode: str = ...,
        fuzzy: str = ...,
        threshold: int = ...,
    ) -> list[int]: ...
    def page(
        self,
        page: int,
        limit: int,
        filters: Sequence[Any] | None = ...,
        sorts: Sequence[Any] | None = ...,
    ) -> dict[str, Any]: ...
