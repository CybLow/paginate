"""Public asynchronous pagination API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict, TypeVar, Unpack

from ..core.pages import Page, PageParams
from .execution.async_executor import (
    CountQueryInput,
    Execution,
    Session,
    create_execution,
    gather_snapshot,
)


if TYPE_CHECKING:
    from collections.abc import Callable

    from ..core.snapshots import PaginationSnapshot
    from ..database.types import SelectStatement

T = TypeVar("T")
"""Generic type variable for items."""

ResultT = TypeVar("ResultT", covariant=True)
"""Covariant type variable for result types."""


@dataclass(frozen=True)
class CollectOptions:
    """Internal options governing snapshot collection.

    Attributes:
        count_query: Optional explicit count statement.
        unique: Whether to deduplicate rows before counting/materializing.
        clamp: Whether to clamp requested parameters to bounds.
        scalars: Whether to select scalar results (ORM entities otherwise).
    """

    count_query: CountQueryInput | None
    unique: bool
    clamp: bool
    scalars: bool


class _CollectKwargs(TypedDict, total=False):
    """Public keyword arguments accepted by pagination helpers.

    Attributes:
        count_query: Optional explicit count statement.
        unique: Whether to deduplicate rows.
        clamp: Whether to clamp page parameters to bounds.
    """

    count_query: CountQueryInput | None
    unique: bool
    clamp: bool


def _entities(
    snapshot: PaginationSnapshot[T, PageParams],
) -> tuple[list[T], int]:
    """Return ORM entities alongside the total number of rows.

    Args:
        snapshot: Pagination snapshot containing items and metadata.

    Returns:
        Tuple of (items, total) where items are ORM entities.
    """
    return snapshot.items, snapshot.total


def _rows(snapshot: PaginationSnapshot[T, PageParams]) -> tuple[list[T], int]:
    """Return raw rows with their total count.

    Args:
        snapshot: Pagination snapshot containing items and metadata.

    Returns:
        Tuple of (items, total) where items are raw rows.
    """
    return snapshot.items, snapshot.total


def _entities_page(
    snapshot: PaginationSnapshot[T, PageParams],
) -> Page[T]:
    """Wrap paginate_entities result into a Page object.

    Args:
        snapshot: Pagination snapshot containing items and metadata.

    Returns:
        A Page object with items, total, and pagination parameters.
    """
    return Page.create(snapshot.items, snapshot.total, snapshot.params)


def _rows_page(snapshot: PaginationSnapshot[T, PageParams]) -> Page[T]:
    """Return a Page built from raw row results.

    Args:
        snapshot: Pagination snapshot containing items and metadata.

    Returns:
        A Page object with raw rows, total, and pagination parameters.
    """
    return Page.create(snapshot.items, snapshot.total, snapshot.params)


async def _collect(
    session: Session,
    query: SelectStatement,
    params: PageParams,
    builder: Callable[[PaginationSnapshot[T, PageParams]], ResultT],
    options: CollectOptions,
) -> ResultT:
    """Collect a snapshot and build the desired result type.

    Args:
        session: Async session used for execution.
        query: Statement to paginate.
        params: Page parameters controlling page and limit.
        builder: Callback mapping snapshot -> desired return type.
        options: Internal collection options.

    Returns:
        The result produced by builder.
    """
    snapshot: PaginationSnapshot[T, PageParams] = await gather_snapshot(
        session, query, _make_execution(params, options)
    )
    return builder(snapshot)


def _make_execution(params: PageParams, options: CollectOptions) -> Execution[PageParams]:
    """Create an execution plan for snapshot gathering.

    Args:
        params: Page parameters for pagination.
        options: Collection options controlling behavior.

    Returns:
        An Execution plan ready for snapshot gathering.
    """
    return create_execution(
        params,
        count_query=options.count_query,
        clamp=options.clamp,
        unique=options.unique,
        scalars=options.scalars,
    )


def _make_options(kwargs: _CollectKwargs, scalars: bool) -> CollectOptions:
    """Normalize public kwargs into a CollectOptions instance.

    Args:
        kwargs: Public keyword arguments from pagination functions.
        scalars: Whether to select scalar results.

    Returns:
        A CollectOptions instance with normalized values.
    """
    return CollectOptions(
        kwargs.get("count_query"),
        kwargs.get("unique", False),
        kwargs.get("clamp", False),
        scalars,
    )


async def paginate_entities(
    session: Session,
    query: SelectStatement,
    params: PageParams,
    **kwargs: Unpack[_CollectKwargs],
) -> tuple[list[T], int]:
    """Paginate a statement and return ORM entities with total count.

    Args:
        session: Async execution session.
        query: Statement selecting ORM entities.
        params: Page parameters (page number and limit).
        **kwargs: Optional unique/clamp/count_query options.

    Returns:
        Tuple (items, total) where items are ORM entities.

    Example:
        >>> items, total = await paginate_entities(
        ...     session, select(User), PageParams(page=1, limit=20)
        ... )
    """
    options = _make_options(kwargs, True)
    return await _collect(session, query, params, _entities, options)


async def paginate_entities_to_page(
    session: Session,
    query: SelectStatement,
    params: PageParams,
    **kwargs: Unpack[_CollectKwargs],
) -> Page[T]:
    """Paginate entities and wrap the result into a Page.

    Args:
        session: Async execution session.
        query: Statement selecting ORM entities.
        params: Page parameters (page number and limit).
        **kwargs: Optional unique/clamp/count_query options.

    Returns:
        A Page object containing items, total, and pagination metadata.

    Example:
        >>> page = await paginate_entities_to_page(
        ...     session, select(User), PageParams(page=1, limit=20)
        ... )
    """
    options = _make_options(kwargs, True)
    return await _collect(session, query, params, _entities_page, options)


async def paginate_rows(
    session: Session,
    query: SelectStatement,
    params: PageParams,
    **kwargs: Unpack[_CollectKwargs],
) -> tuple[list[T], int]:
    """Paginate a statement and return raw rows with total count.

    Args:
        session: Async execution session.
        query: Statement selecting raw rows.
        params: Page parameters (page number and limit).
        **kwargs: Optional unique/clamp/count_query options.

    Returns:
        Tuple (items, total) where items are raw row tuples.

    Example:
        >>> rows, total = await paginate_rows(
        ...     session, select(User.id, User.name), PageParams(page=1, limit=20)
        ... )
    """
    options = _make_options(kwargs, False)
    return await _collect(session, query, params, _rows, options)


async def paginate_rows_to_page(
    session: Session,
    query: SelectStatement,
    params: PageParams,
    **kwargs: Unpack[_CollectKwargs],
) -> Page[T]:
    """Paginate raw rows and wrap the result into a Page.

    Args:
        session: Async execution session.
        query: Statement selecting raw rows.
        params: Page parameters (page number and limit).
        **kwargs: Optional unique/clamp/count_query options.

    Returns:
        A Page object containing raw rows, total, and pagination metadata.

    Example:
        >>> page = await paginate_rows_to_page(
        ...     session, select(User.id, User.name), PageParams(page=1, limit=20)
        ... )
    """
    options = _make_options(kwargs, False)
    return await _collect(session, query, params, _rows_page, options)


__all__ = [
    "paginate_entities",
    "paginate_entities_to_page",
    "paginate_rows",
    "paginate_rows_to_page",
]
