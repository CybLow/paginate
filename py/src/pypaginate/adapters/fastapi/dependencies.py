"""FastAPI pagination dependencies — parse query params into pypaginate specs.

These are plain FastAPI dependency callables (and ready-made ``Annotated``
aliases) that turn the request query string into the package's flat dataclasses::

    from pypaginate.adapters.fastapi import OffsetDep, SortDep, SearchDep


    @app.get("/users")
    def list_users(params: OffsetDep, sort: SortDep, search: SearchDep): ...

Invalid page/limit/cursor combinations are reported as HTTP 422 responses.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, TypeVar

from pypaginate.errors import PaginateError
from pypaginate.params import MAX_LIMIT, CursorParams, OffsetParams
from pypaginate.specs import SearchSpec, SortSpec


try:
    from fastapi import Depends, HTTPException, Query
except ImportError as _err:  # pragma: no cover
    _msg = "FastAPI is required: pip install pypaginate[fastapi]"
    raise ImportError(_msg) from _err


_T = TypeVar("_T")


def _checked(build: Callable[[], _T]) -> _T:
    """Build a value, re-raising pypaginate validation errors as HTTP 422."""
    try:
        return build()
    except PaginateError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def offset_params(
    page: Annotated[int, Query(ge=1, description="1-based page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT, description="Page size")] = 20,
) -> OffsetParams:
    """Resolve offset params (``?page=&limit=``) from the request query."""
    return _checked(lambda: OffsetParams(page=page, limit=limit))


def cursor_params(
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT, description="Page size")] = 20,
    after: Annotated[str | None, Query(description="Cursor to page forward")] = None,
    before: Annotated[str | None, Query(description="Cursor to page backward")] = None,
) -> CursorParams:
    """Resolve cursor params (``?limit=&after=&before=``) from the request query."""
    return _checked(lambda: CursorParams(limit=limit, after=after, before=before))


def _sort_key(part: str) -> SortSpec:
    """Parse one sort token; a leading ``-`` means descending."""
    if part.startswith("-"):
        return SortSpec(field=part[1:], direction="desc")
    return SortSpec(field=part.lstrip("+"))


def parse_sort(value: str | None) -> list[SortSpec]:
    """Parse a ``name,-age`` sort string into an ordered ``SortSpec`` list."""
    if not value:
        return []
    return [_sort_key(part) for part in map(str.strip, value.split(",")) if part]


def sort_params(
    sort: Annotated[
        str | None,
        Query(description="Comma-separated sort keys; '-' prefix = descending"),
    ] = None,
) -> list[SortSpec]:
    """Resolve sort keys (``?sort=name,-age``) into a ``SortSpec`` list."""
    return parse_sort(sort)


def parse_search(query: str | None, fields_csv: str) -> SearchSpec | None:
    """Parse a query plus comma-separated fields into a ``SearchSpec`` (or ``None``)."""
    if not query:
        return None
    fields = [field for field in map(str.strip, fields_csv.split(",")) if field]
    if not fields:
        return None
    return SearchSpec(query=query, fields=fields)


def search_params(
    q: Annotated[str | None, Query(description="Free-text search query")] = None,
    search_fields: Annotated[str, Query(description="Comma-separated search fields")] = "",
) -> SearchSpec | None:
    """Resolve search params (``?q=&search_fields=``) into a ``SearchSpec``."""
    return parse_search(q, search_fields)


OffsetDep = Annotated[OffsetParams, Depends(offset_params)]
CursorDep = Annotated[CursorParams, Depends(cursor_params)]
SortDep = Annotated[list[SortSpec], Depends(sort_params)]
SearchDep = Annotated[SearchSpec | None, Depends(search_params)]


__all__ = [
    "CursorDep",
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
