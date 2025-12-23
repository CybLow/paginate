"""Adapters binding runtime pagination models to typed protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

from .pages import PageParams


if TYPE_CHECKING:
    from ..database.types import CountStatement

ParamsT = TypeVar("ParamsT", bound=PageParams)
"""Type variable for pagination parameter types bounded by PageParams."""


@dataclass(frozen=True)
class PaginationContext(Generic[ParamsT]):
    """Immutable parameters that drive SQL pagination execution.

    Attributes:
        params: Effective page parameters.
        clamp: Whether to clamp requested parameters to bounds.
        unique: Whether to deduplicate rows during pagination.
        count_query: Optional explicit count statement.
    """

    params: ParamsT
    clamp: bool
    unique: bool
    count_query: CountStatement | None = None


def clamp_page_params(total: int, params: ParamsT) -> ParamsT:
    """Clamp requested pagination parameters within the available range.

    Args:
        total: Total number of rows available.
        params: Requested page parameters.

    Returns:
        Potentially adjusted parameters constrained to valid bounds.
    """
    limit = max(1, params.limit)
    if total <= 0:
        return params.model_copy(update={"page": 1, "limit": limit})  # type: ignore[return-value]
    pages = max(1, (total + limit - 1) // limit)
    safe_page = min(max(params.page, 1), pages)
    if safe_page == params.page and limit == params.limit:
        return params
    return params.model_copy(update={"page": safe_page, "limit": limit})  # type: ignore[return-value]


__all__ = ["PaginationContext", "clamp_page_params"]
