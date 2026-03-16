"""Auto-detect dispatch for the universal paginate() function.

Input type determines output type (Elysia-style inference):
    OffsetParams → OffsetPage
    CursorParams → CursorPage

Detection happens exactly once here. Internally, sync and async
code paths are separate with no scattered conditionals.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Sequence
from typing import Any, TypeVar, overload

from pypaginate.domain.enums import OverflowStrategy
from pypaginate.domain.models import (
    CursorPage,
    CursorParams,
    OffsetPage,
    OffsetParams,
)
from pypaginate.domain.protocols import (
    CursorBackend,
    PaginationBackend,
    SyncPaginationBackend,
)
from pypaginate.engine.paginator import AsyncPaginator, Paginator


ItemT = TypeVar("ItemT")


# ── Overloads: input type → output type ──────────────────


@overload
def paginate(
    source: Sequence[ItemT],
    params: OffsetParams,
    *,
    overflow: OverflowStrategy = ...,
) -> OffsetPage[ItemT]: ...


@overload
def paginate(
    source: object,
    params: OffsetParams,
    *,
    backend: SyncPaginationBackend[ItemT],
    overflow: OverflowStrategy = ...,
) -> OffsetPage[ItemT]: ...


@overload
def paginate(
    source: object,
    params: OffsetParams,
    *,
    backend: PaginationBackend[ItemT],
    overflow: OverflowStrategy = ...,
) -> Awaitable[OffsetPage[ItemT]]: ...


@overload
def paginate(
    source: object,
    params: CursorParams,
    *,
    backend: CursorBackend[ItemT],
) -> Awaitable[CursorPage[ItemT]]: ...


# ── Implementation ───────────────────────────────────────


def paginate(
    source: object,
    params: OffsetParams | CursorParams,
    *,
    backend: object | None = None,
    overflow: OverflowStrategy = OverflowStrategy.EMPTY,
) -> Any:
    """Universal pagination entry point.

    The return type is automatically inferred from the params type:
    - ``OffsetParams`` → ``OffsetPage``
    - ``CursorParams`` → ``CursorPage``

    Args:
        source: Data source (Sequence for in-memory, or query).
        params: OffsetParams or CursorParams.
        backend: Optional backend. Auto-detected from source if None.
        overflow: How to handle out-of-range pages (offset only).

    Returns:
        OffsetPage for sync, Awaitable[OffsetPage|CursorPage] for async.

    Raises:
        TypeError: If source is not a Sequence and no backend given.
        TypeError: If cursor params used with a sync backend.
    """
    if (
        backend is None
        and isinstance(params, OffsetParams)
        and isinstance(source, Sequence)
        and not isinstance(source, (str, bytes))
    ):
        return _fast_memory_offset(source, params, overflow)

    resolved = _resolve_backend(source, backend)

    if isinstance(params, CursorParams):
        if not _has_async_methods(resolved):
            msg = (
                "Cursor pagination requires an async CursorBackend. "
                "Use an async backend or switch to OffsetParams."
            )
            raise TypeError(msg)
        return _cursor_paginate(resolved, source, params)

    if _has_async_methods(resolved):
        paginator: AsyncPaginator[Any] = AsyncPaginator(resolved, overflow=overflow)  # type: ignore[arg-type]
        return paginator.paginate(source, params)

    return _sync_offset(resolved, source, params, overflow)


# ── Internal paths (clean, no branching) ─────────────────


def _fast_memory_offset(
    source: Sequence[Any],
    params: OffsetParams,
    overflow: OverflowStrategy,
) -> Any:
    """Fast path for in-memory offset pagination (no backend alloc)."""
    total = len(source)
    effective = params.clamp(total) if overflow is OverflowStrategy.CLAMP else params
    if total <= 0 or effective.offset >= total:
        return OffsetPage.create([], total, effective)
    items = list(source[effective.offset : effective.offset + effective.limit])
    return OffsetPage.create(items, total, effective)


def _sync_offset(
    backend: Any,
    source: object,
    params: OffsetParams,
    overflow: OverflowStrategy,
) -> Any:
    """Execute sync offset pagination."""
    paginator: Paginator[Any] = Paginator(backend, overflow=overflow)
    return paginator.paginate(source, params)


async def _cursor_paginate(
    backend: Any,
    source: object,
    params: CursorParams,
) -> Any:
    """Execute async cursor pagination."""
    from pypaginate.engine.cursor import AsyncCursorPaginator

    paginator: AsyncCursorPaginator[Any] = AsyncCursorPaginator(backend)
    return await paginator.paginate(source, params)


# ── Detection helpers ────────────────────────────────────


def _resolve_backend(source: object, backend: object | None) -> object:
    """Resolve backend from source type or explicit argument."""
    if backend is not None:
        return backend
    if isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
        from pypaginate.adapters.memory.backend import MemoryBackend

        return MemoryBackend()
    msg = (
        f"Cannot auto-detect backend for {type(source).__name__}. "
        "Pass backend=YourBackend(...) explicitly."
    )
    raise TypeError(msg)


_ASYNC_CACHE: dict[type, bool] = {}


def _has_async_methods(backend: object) -> bool:
    """Check if a backend has async methods (cached per class)."""
    cls = type(backend)
    cached = _ASYNC_CACHE.get(cls)
    if cached is not None:
        return cached
    result = _detect_async(backend)
    _ASYNC_CACHE[cls] = result
    return result


def _detect_async(backend: object) -> bool:
    """Introspect backend for async methods."""
    for attr in ("count", "fetch", "fetch_page"):
        method = getattr(backend, attr, None)
        if method is not None:
            return inspect.iscoroutinefunction(method)
    return False


__all__ = ["paginate"]
