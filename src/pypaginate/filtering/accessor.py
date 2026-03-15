"""Field accessor for resolving dotted paths on dicts and objects.

Supports nested access like ``"user.profile.email"`` transparently
across both dict-like and attribute-based containers.
"""

from __future__ import annotations

from pypaginate.domain.exceptions import FilterError


_SENTINEL = object()


def get_value(item: object, field_path: str) -> object:
    """Resolve a dotted field path on an item.

    Args:
        item: The source dict or object.
        field_path: Dot-separated path (e.g. ``"user.name"``).

    Returns:
        The resolved value.

    Raises:
        FilterError: If any segment cannot be resolved.
    """
    current = item
    for segment in field_path.split("."):
        current = _resolve_segment(current, segment, field_path)
    return current


def _resolve_segment(
    obj: object,
    segment: str,
    full_path: str,
) -> object:
    """Resolve a single path segment via dict or attribute access.

    Args:
        obj: Current object in the traversal.
        segment: The key or attribute name.
        full_path: Full dotted path (for error messages).

    Returns:
        The resolved value for this segment.

    Raises:
        FilterError: If the segment cannot be resolved.
    """
    value = _try_dict_access(obj, segment)
    if value is not _SENTINEL:
        return value
    return _try_attr_access(obj, segment, full_path)


def _try_dict_access(obj: object, segment: str) -> object:
    """Attempt dict-style access, returning _SENTINEL on failure."""
    if not isinstance(obj, dict):
        return _SENTINEL
    if segment in obj:
        return obj[segment]
    return _SENTINEL


def _try_attr_access(
    obj: object,
    segment: str,
    full_path: str,
) -> object:
    """Attempt attribute access, raising FilterError on failure.

    Args:
        obj: Object to access.
        segment: Attribute name.
        full_path: Full dotted path (for error messages).

    Returns:
        The attribute value.

    Raises:
        FilterError: If the attribute does not exist.
    """
    value = getattr(obj, segment, _SENTINEL)
    if value is _SENTINEL:
        _raise_not_found(segment, full_path, obj)
    return value


def _raise_not_found(
    segment: str,
    full_path: str,
    obj: object,
) -> None:
    """Raise a FilterError for an unresolved path segment.

    Args:
        segment: The segment that failed.
        full_path: The full dotted path.
        obj: The object that was searched.

    Raises:
        FilterError: Always raised.
    """
    msg = f"Cannot resolve '{segment}' in path '{full_path}'"
    raise FilterError(
        msg,
        field=full_path,
        details={"segment": segment, "type": type(obj).__name__},
    )


__all__ = ["get_value"]
