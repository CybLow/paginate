"""FastAPI pagination dependencies.

Provides ``Annotated`` type aliases for clean dependency injection::

    from pypaginate.adapters.fastapi import OffsetDep, CursorDep


    @app.get("/users")
    async def get_users(params: OffsetDep) -> OffsetPage[User]:
        return paginate(users, params)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pypaginate.domain.models import CursorParams, OffsetParams


if TYPE_CHECKING:
    pass

try:
    from fastapi import Depends, Query
except ImportError as _err:  # pragma: no cover
    _msg = "FastAPI is required: pip install pypaginate[fastapi]"  # pragma: no cover
    raise ImportError(_msg) from _err  # pragma: no cover


def _get_offset_params(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
) -> OffsetParams:
    """Resolve offset pagination params from query string."""
    return OffsetParams(page=page, limit=limit)


def _get_cursor_params(
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    after: str | None = Query(None, description="Cursor for next page"),
    before: str | None = Query(None, description="Cursor for previous page"),
) -> CursorParams:
    """Resolve cursor pagination params from query string."""
    return CursorParams(limit=limit, after=after, before=before)


OffsetDep = Annotated[OffsetParams, Depends(_get_offset_params)]
"""Annotated type for offset pagination dependency.

Usage::

    @app.get("/users")
    async def get_users(params: OffsetDep) -> OffsetPage[User]:
        return paginate(users, params)
"""

CursorDep = Annotated[CursorParams, Depends(_get_cursor_params)]
"""Annotated type for cursor pagination dependency.

Usage::

    @app.get("/users/scroll")
    async def scroll(params: CursorDep) -> CursorPage[User]:
        return await paginate(query, params, backend=backend)
"""

__all__ = ["CursorDep", "OffsetDep"]
