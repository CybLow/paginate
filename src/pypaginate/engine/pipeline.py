"""Pipelines — compose filter, sort, search, then paginate.

Separate sync and async pipelines for type safety.
Each applies optional specs before delegating to its paginator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from pypaginate.domain.models import OffsetPage, OffsetParams
from pypaginate.engine.paginator import AsyncPaginator, Paginator


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.protocols import FilterBackend, SearchBackend, SortBackend
    from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec

ItemT = TypeVar("ItemT")


def _apply_specs(
    query: object,
    filters: Sequence[FilterSpec],
    sorting: Sequence[SortSpec],
    search: SearchSpec | None,
    filter_backend: FilterBackend | None,
    sort_backend: SortBackend | None,
    search_backend: SearchBackend | None,
) -> object:
    """Apply filter, sort, and search specs to a query.

    Args:
        query: Data source or query object.
        filters: Filter specifications.
        sorting: Sort specifications.
        search: Search specification.
        filter_backend: Optional filter backend.
        sort_backend: Optional sort backend.
        search_backend: Optional search backend.

    Returns:
        Modified query with all specs applied.
    """
    if filters and filter_backend is not None:
        query = filter_backend.apply_filters(query, filters)
    if sorting and sort_backend is not None:
        query = sort_backend.apply_sorting(query, sorting)
    if search is not None and search_backend is not None:
        query = search_backend.apply_search(query, search)
    return query


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
