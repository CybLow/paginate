"""SQLAlchemy pagination orchestrator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from pypaginator.exceptions import PaginationConfigurationError
from ..core.context import PaginationContext, clamp_page_params
from ..core.pages import PageParams
from ..core.snapshots import (
    KeysetPaginationSnapshot,
    PaginationSnapshot,
    extract_keyset_markers,
    markers_from_paging,
    materialize_keyset_page,
)
from ..query.builders.count_builder import build_count_statement, fetch_count

if TYPE_CHECKING:  # pragma: no cover - typing only
    from collections.abc import Awaitable, Callable

    from sqlalchemy.ext.asyncio import AsyncSession

    from ..core.pages import KeysetPageParams
    from ..database.types import CountStatement, Result, ResultSequence, SelectStatement

ItemT = TypeVar("ItemT")
"""Type variable for item types in pagination results."""

ParamsT = TypeVar("ParamsT", bound=PageParams)
"""Type variable for pagination parameter types bounded by PageParams."""


class SqlPaginator(Generic[ItemT]):
    """Transform a SQLAlchemy statement into a paginated payload.

    The paginator supports both offset-based and keyset-based strategies and
    provides helpers to materialize results, compute counts, and clamp
    parameters.

    Attributes:
        _session: Async SQLAlchemy session used for execution.
        _clamp: When ``True``, clamp parameters to the computed total.
    """

    def __init__(self, session: AsyncSession, *, clamp: bool) -> None:
        """Initialize the paginator.

        Args:
            session: Async SQLAlchemy session.
            clamp: Whether to clamp requested page parameters to bounds.
        """
        self._session = session
        self._clamp = clamp

    async def paginate(
        self,
        query: SelectStatement,
        context: PaginationContext[ParamsT],
        *,
        scalars: bool,
    ) -> PaginationSnapshot[ItemT, ParamsT]:
        """Paginate a statement using the offset strategy.

        Args:
            query: Statement to paginate.
            context: Execution context carrying parameters and options.
            scalars: Whether to select scalar results (ORM entities otherwise).

        Returns:
            A PaginationSnapshot with materialized items and metadata.
        """
        return await self._paginate_offset(query, context, scalars=scalars)

    async def _prepare(
        self,
        query: SelectStatement,
        context: PaginationContext[ParamsT],
    ) -> tuple[int, ParamsT]:
        """Compute total rows and effective (possibly clamped) parameters.

        Args:
            query: Statement to paginate.
            context: Pagination context.

        Returns:
            Tuple of (total_count, effective_params).
        """
        total = await self._count_total(
            query, context.count_query, unique=context.unique
        )
        effective = self._clamp_params(context.params, total)
        return total, effective

    def _clamp_params(self, params: ParamsT, total: int) -> ParamsT:
        """Clamp parameters to bounds when clamping is enabled.

        Args:
            params: Original parameters.
            total: Total row count.

        Returns:
            Clamped or original parameters.
        """
        return clamp_page_params(total, params) if self._clamp else params

    async def _fetch_page(
        self,
        query: SelectStatement,
        params: PageParams,
        *,
        scalars: bool,
        unique: bool,
    ) -> list[ItemT]:
        """Execute the limited statement and materialize the page payload.

        Args:
            query: Statement to execute.
            params: Page parameters.
            scalars: Whether to select scalars.
            unique: Whether to deduplicate.

        Returns:
            List of materialized items.
        """
        statement = self._apply_limits(query, params)
        result = await self._session.execute(statement)
        return self._materialize(result, scalars=scalars, unique=unique)  # type: ignore[arg-type]

    @staticmethod
    def _apply_limits(
        query: SelectStatement, params: PageParams
    ) -> SelectStatement:
        """Apply offset/limit to the base statement from parameters.

        Args:
            query: Base statement.
            params: Page parameters.

        Returns:
            Limited statement.
        """
        return query.offset(params.offset).limit(params.limit)

    @staticmethod
    def _is_empty(total: int, params: PageParams) -> bool:
        """Return True if no rows should be fetched for the page.

        Args:
            total: Total row count.
            params: Page parameters.

        Returns:
            True if page is empty.
        """
        return total <= 0 or params.offset >= total

    @staticmethod
    def _select_sequence(
        result: ResultSequence[ItemT],  # type: ignore[type-var]
        *,
        unique: bool,
    ) -> ResultSequence[ItemT]:
        """Optionally remove duplicates prior to materialization.

        Args:
            result: Result sequence.
            unique: Whether to deduplicate.

        Returns:
            Unique or original result sequence.
        """
        return result.unique() if unique else result

    def _materialize(
        self,
        result: Result[ItemT],
        *,
        scalars: bool,
        unique: bool,
    ) -> list[ItemT]:
        """Materialize the selected results into a list of items.

        Args:
            result: Query result.
            scalars: Whether to select scalars.
            unique: Whether to deduplicate.

        Returns:
            List of materialized items.
        """
        sequence = result.scalars() if scalars else result
        selected = self._select_sequence(sequence, unique=unique)
        return list(selected.all())  # type: ignore[arg-type]

    async def _count_total(
        self,
        query: SelectStatement,
        count_query: CountStatement | None,
        *,
        unique: bool,
    ) -> int:
        """Compute the total number of rows for the given query.

        Args:
            query: Statement to count.
            count_query: Optional explicit count statement.
            unique: Whether to count unique rows.

        Returns:
            Total row count.
        """
        stmt = build_count_statement(query, count_query, unique=unique)
        return await fetch_count(self._session, stmt)

    # fmt: off
    async def paginate_keyset(self, query: SelectStatement, params: KeysetPageParams, *, unique: bool, scalars: bool = True) -> KeysetPaginationSnapshot[ItemT]:
# fmt: on
        """Paginate a statement using the keyset strategy.

        Args:
            query: Statement to paginate.
            params: Keyset-specific parameters (limit and bookmarks).
            unique: Whether to deduplicate rows before pagination.
            scalars: Whether to coerce rows to scalars when possible.

        Returns:
            A KeysetPaginationSnapshot with items and markers.
        """
        from ..engines.keyset import select_keyset_page

        page: object = await select_keyset_page(self._session, query, params, unique=unique)
        items: list[ItemT] = materialize_keyset_page(page, scalars=scalars)  # type: ignore[arg-type]
        markers = markers_from_paging(page.paging)  # type: ignore[attr-defined]
        return KeysetPaginationSnapshot(items, params, *markers)

# fmt: off
    async def _paginate_offset(self, query: SelectStatement, context: PaginationContext[ParamsT], *, scalars: bool) -> PaginationSnapshot[ItemT, ParamsT]:
# fmt: on
        """Internal offset-based pagination pipeline.

        Args:
            query: Statement to paginate.
            context: Pagination context.
            scalars: Whether to select scalars.

        Returns:
            PaginationSnapshot with results.
        """
        total, effective = await self._prepare(query, context)
        if self._is_empty(total, effective):
            return PaginationSnapshot([], total, effective)
        is_unique = context.unique
        payload = await self._fetch_page(
            query, effective, scalars=scalars, unique=is_unique
        )
        return PaginationSnapshot(payload, total, effective)


def get_pagination_strategy(
    name: str,
) -> Callable[..., Awaitable[object]]:
    """Return the paginator method associated with name.

    Args:
        name: Strategy identifier ("offset" or "keyset").

    Returns:
        The bound coroutine function implementing the strategy.

    Raises:
        PaginationConfigurationError: When name is unknown.
    """
    try:
        return _STRATEGIES[name]
    except KeyError as exc:
        raise PaginationConfigurationError(
            "Unknown pagination strategy", details={"strategy": name}
        ) from exc


_STRATEGIES: dict[str, Callable[..., Awaitable[object]]] = {
    "offset": SqlPaginator.paginate,
    "keyset": SqlPaginator.paginate_keyset,
}
"""Mapping of strategy names to their corresponding paginator methods."""


__all__ = [
    "SqlPaginator",
    "PaginationSnapshot",
    "KeysetPaginationSnapshot",
    "get_pagination_strategy",
    "extract_keyset_markers",
]
