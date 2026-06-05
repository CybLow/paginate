"""Pipelines — compose filter, sort, search, then paginate.

Separate sync and async pipelines for type safety.
Each applies optional specs before delegating to its paginator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, cast

from pypaginate.domain.params import OffsetParams
from pypaginate.engine.paginator import AsyncPaginator, Paginator


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from pypaginate.domain.pages import OffsetPage
    from pypaginate.domain.protocols import FilterBackend, SearchBackend, SortBackend
    from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec

ItemT = TypeVar("ItemT")


def _apply_specs(
    query: object,
    filters: object,
    sorting: object,
    search: object | None,
    filter_backend: FilterBackend | None,
    sort_backend: SortBackend | None,
    search_backend: SearchBackend | None,
) -> object:
    """Apply filter, sort, and search specs to a query.

    Auto-converts FilterDep/SortDep/SearchDep via protocol detection.
    Accepts both raw spec lists and FastAPI dependency objects.
    """
    resolved_filters = _resolve_input(filters, "to_specs")
    resolved_sorting = _resolve_input(sorting, "to_specs")
    resolved_search = _resolve_search(search)

    if resolved_filters and filter_backend is not None:
        query = filter_backend.apply_filters(query, cast("Sequence[FilterSpec]", resolved_filters))
    if resolved_sorting and sort_backend is not None:
        query = sort_backend.apply_sorting(query, cast("Sequence[SortSpec]", resolved_sorting))
    if resolved_search is not None and search_backend is not None:
        query = search_backend.apply_search(query, cast("SearchSpec", resolved_search))
    return query


def _resolve_input(value: object, method: str) -> object:
    """Auto-convert objects with to_specs() to spec lists."""
    if hasattr(value, method):
        return cast("Callable[[], object]", getattr(value, method))()
    return value


def _resolve_search(value: object | None) -> object | None:
    """Auto-convert SearchDep to SearchSpec via to_spec()."""
    to_spec = getattr(value, "to_spec", None)
    if to_spec is not None:
        return cast("Callable[[], object]", to_spec)()
    return value


class SyncPipeline(Generic[ItemT]):
    """Sync: filter -> sort -> search -> paginate."""

    __slots__ = ("_filter", "_paginator", "_search", "_sort")

    def __init__(
        self,
        paginator: Paginator[ItemT],
        *,
        filter_backend: FilterBackend | None = None,
        sort_backend: SortBackend | None = None,
        search_backend: SearchBackend | None = None,
    ) -> None:
        self._paginator = paginator
        self._filter = filter_backend
        self._sort = sort_backend
        self._search = search_backend

    def execute(
        self,
        query: object,
        params: OffsetParams,
        *,
        filters: Sequence[FilterSpec] = (),
        sorting: Sequence[SortSpec] = (),
        search: SearchSpec | None = None,
    ) -> OffsetPage[ItemT]:
        """Apply specs then paginate synchronously.

        Args:
            query: Data source.
            params: Offset pagination parameters.
            filters: Filter specifications.
            sorting: Sort specifications.
            search: Search specification.

        Returns:
            Paginated result with filters/sorts applied.
        """
        modified = _apply_specs(
            query,
            filters,
            sorting,
            search,
            self._filter,
            self._sort,
            self._search,
        )
        return self._paginator.paginate(modified, params)


class AsyncPipeline(Generic[ItemT]):
    """Async: filter -> sort -> search -> paginate."""

    __slots__ = ("_filter", "_paginator", "_search", "_sort")

    def __init__(
        self,
        paginator: AsyncPaginator[ItemT],
        *,
        filter_backend: FilterBackend | None = None,
        sort_backend: SortBackend | None = None,
        search_backend: SearchBackend | None = None,
    ) -> None:
        self._paginator = paginator
        self._filter = filter_backend
        self._sort = sort_backend
        self._search = search_backend

    async def execute(
        self,
        query: object,
        params: OffsetParams,
        *,
        filters: Sequence[FilterSpec] = (),
        sorting: Sequence[SortSpec] = (),
        search: SearchSpec | None = None,
    ) -> OffsetPage[ItemT]:
        """Apply specs then paginate asynchronously.

        Args:
            query: Query object.
            params: Offset pagination parameters.
            filters: Filter specifications.
            sorting: Sort specifications.
            search: Search specification.

        Returns:
            Paginated result with filters/sorts applied.
        """
        modified = _apply_specs(
            query,
            filters,
            sorting,
            search,
            self._filter,
            self._sort,
            self._search,
        )
        return await self._paginator.paginate(modified, params)


__all__ = ["AsyncPipeline", "SyncPipeline"]
