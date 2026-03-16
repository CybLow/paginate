"""Field accessor for resolving dotted paths on dicts and objects.

Supports nested access like ``"user.profile.email"`` transparently
across both dict-like and attribute-based containers.

``compile_accessor()`` pre-splits the path ONCE and returns a fast
callable that can be applied N times without per-item overhead.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import NoReturn

from pypaginate.domain.exceptions import FilterError


_SENTINEL = object()


def compile_accessor(field_path: str) -> Callable[[object], object]:
    """Compile a field path into a fast accessor function.

    Called ONCE per field path. Returns a callable used N times.

    Args:
        field_path: Dot-separated path (e.g. ``"user.name"``).

    Returns:
        A callable that resolves the path on any item.
    """
    segments = field_path.split(".")

    if len(segments) == 1:
        return _single_accessor(segments[0], field_path)

    return _multi_accessor(tuple(segments), field_path)


def _single_accessor(
    key: str,
    field_path: str,
) -> Callable[[object], object]:
    """Build accessor for a single-segment path."""

    def _access(item: object) -> object:
        if isinstance(item, dict):
            if key in item:
                return item[key]
        else:
            value = getattr(item, key, _SENTINEL)
            if value is not _SENTINEL:
                return value
        return _raise_not_found(key, field_path, item)

    return _access


def _multi_accessor(
    segments: tuple[str, ...],
    field_path: str,
) -> Callable[[object], object]:
    """Build accessor for a multi-segment dotted path."""

    def _access(item: object) -> object:
        current = item
        for seg in segments:
            current = _resolve_segment(current, seg, field_path)
        return current

    return _access


def _resolve_segment(
    obj: object,
    segment: str,
    full_path: str,
) -> object:
    """Resolve a single path segment via dict or attribute access."""
    if isinstance(obj, dict):
        if segment in obj:
            return obj[segment]
    else:
        value = getattr(obj, segment, _SENTINEL)
        if value is not _SENTINEL:
            return value
    return _raise_not_found(segment, full_path, obj)


def _raise_not_found(
    segment: str,
    full_path: str,
    obj: object,
) -> NoReturn:
    """Raise a FilterError for an unresolved path segment."""
    msg = f"Cannot resolve '{segment}' in path '{full_path}'"
    raise FilterError(
        msg,
        field=full_path,
        details={"segment": segment, "type": type(obj).__name__},
    )


__all__ = ["compile_accessor"]
