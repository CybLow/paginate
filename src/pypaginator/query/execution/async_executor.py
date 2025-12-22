"""Internal helpers for the asynchronous pagination facade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeAlias, TypeGuard, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ...core.context import PaginationContext
from ...core.pages import PageParams
from ...database.types import CountStatement, SelectStatement
from ...engines.sql import SqlPaginator

if TYPE_CHECKING:
    from ...core.snapshots import PaginationSnapshot

T = TypeVar("T")
"""Generic type variable for item types."""

ParamsT = TypeVar("ParamsT", bound=PageParams)
"""Type variable for pagination parameter types."""

Session: TypeAlias = AsyncSession
"""Type alias for async SQLAlchemy session."""

CountQueryInput: TypeAlias = SelectStatement | CountStatement
"""Type alias for count query inputs (select or count statement)."""


@dataclass(frozen=True)
class Execution(Generic[ParamsT]):
    """Execution plan shared by the public async pagination helpers.

    Attributes:
        params: Effective pagination parameters.
        clamp: Whether to clamp requested parameters to bounds.
        unique: Whether to deduplicate rows before pagination.
        scalars: Whether to materialize scalar values (vs ORM entities).
        count_query: Optional explicit count statement.
    """

    params: ParamsT
    clamp: bool
    unique: bool
    scalars: bool
    count_query: CountStatement | None


def _is_count_statement(value: CountQueryInput) -> TypeGuard[CountStatement]:
    """Return True when value is a typed count statement.

    Args:
        value: Input value to check.

    Returns:
        True if value is a CountStatement, False otherwise.
    """
    return isinstance(value, Select)


def normalize_count_query(count_query: CountQueryInput | None) -> CountStatement | None:
    """Normalize an optional count query to a typed statement when possible.

    Args:
        count_query: Optional count query input to normalize.

    Returns:
        A typed CountStatement or None if input is None.
    """
    if count_query is None:
        return None
    if _is_count_statement(count_query):
        return count_query
    # Here we accept a general select and return the concrete count statement
    # by trusting the caller to provide a proper Select over (int,).
    return count_query  # type: ignore[return-value]


def create_execution(
    params: ParamsT,
    *,
    count_query: CountQueryInput | None,
    clamp: bool,
    unique: bool,
    scalars: bool,
) -> Execution[ParamsT]:
    """Create an Execution plan for snapshot gathering.

    Args:
        params: Pagination parameters.
        count_query: Optional explicit count statement.
        clamp: Whether to clamp requested parameters to bounds.
        unique: Whether to deduplicate rows before pagination.
        scalars: Whether to materialize scalar values.

    Returns:
        An Execution plan ready for use.
    """
    normalized = normalize_count_query(count_query)
    return Execution(params, clamp, unique, scalars, normalized)


async def gather_snapshot(
    session: Session,
    query: SelectStatement,
    execution: Execution[ParamsT],
) -> PaginationSnapshot[T, ParamsT]:
    """Execute pagination and return a snapshot according to execution plan.

    Args:
        session: Async SQLAlchemy session for query execution.
        query: SELECT statement to paginate.
        execution: Execution plan with pagination parameters.

    Returns:
        A PaginationSnapshot with materialized items and metadata.
    """

    context: PaginationContext[ParamsT] = PaginationContext(
        params=execution.params,
        clamp=execution.clamp,
        unique=execution.unique,
        count_query=execution.count_query,
    )
    args = (query, context)
    paginator: SqlPaginator[T] = SqlPaginator(session, clamp=execution.clamp)
    return await paginator.paginate(*args, scalars=execution.scalars)


__all__ = [
    "Session",
    "CountQueryInput",
    "Execution",
    "create_execution",
    "normalize_count_query",
    "gather_snapshot",
]
