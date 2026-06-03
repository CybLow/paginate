"""Backend detection helpers for the dispatch layer.

Resolves backend instances from source types and caches
async introspection results per backend class.
"""

from __future__ import annotations

import inspect
from collections.abc import Sequence


_ASYNC_CACHE: dict[type, bool] = {}


def resolve_backend(source: object, backend: object | None) -> object:
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


def has_async_methods(backend: object) -> bool:
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


__all__ = ["has_async_methods", "resolve_backend"]
