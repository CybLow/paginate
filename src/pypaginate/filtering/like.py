"""LIKE pattern utilities — classification and glob conversion.

Classifies SQL LIKE patterns for fast dispatch to string methods
when possible, falling back to fnmatch for complex patterns.
"""

from __future__ import annotations

from fnmatch import fnmatch


def classify_like(pattern: str) -> tuple[str, str]:
    """Classify a LIKE pattern for fast string-method dispatch.

    Args:
        pattern: SQL LIKE pattern with ``%`` and ``_`` wildcards.

    Returns:
        Tuple of (kind, inner_value) where kind is one of:
        ``"contains"``, ``"startswith"``, ``"endswith"``, ``"complex"``.
    """
    if "_" in pattern:
        return "complex", pattern
    starts = pattern.startswith("%")
    ends = pattern.endswith("%")
    inner = pattern.strip("%")
    if "%" in inner:
        return "complex", pattern
    if starts and ends:
        return "contains", inner
    if ends:
        return "startswith", inner
    if starts:
        return "endswith", inner
    return "complex", pattern


def like_to_glob(pattern: str) -> str:
    """Convert SQL LIKE pattern to fnmatch glob pattern."""
    return pattern.replace("%", "*").replace("_", "?")


def match_like(field_str: str, spec_value: str) -> bool:
    """Match a field value against a LIKE pattern."""
    kind, inner = classify_like(spec_value)
    if kind == "contains":
        return inner in field_str
    if kind == "startswith":
        return field_str.startswith(inner)
    if kind == "endswith":
        return field_str.endswith(inner)
    return fnmatch(field_str, like_to_glob(spec_value))


def match_ilike(field_str: str, spec_value: str) -> bool:
    """Match a field value against a case-insensitive LIKE pattern."""
    kind, inner = classify_like(spec_value)
    lower_field = field_str.lower()
    lower_inner = inner.lower()
    if kind == "contains":
        return lower_inner in lower_field
    if kind == "startswith":
        return lower_field.startswith(lower_inner)
    if kind == "endswith":
        return lower_field.endswith(lower_inner)
    glob = like_to_glob(spec_value).lower()
    return fnmatch(lower_field, glob)


__all__ = ["classify_like", "like_to_glob", "match_ilike", "match_like"]
