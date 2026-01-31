"""Pattern utilities for SQL LIKE and regex filtering."""

from __future__ import annotations

import re

from pypaginate.exceptions import FilterValidationError

from .pipelines import MemoryTextNormalizer


class FilterTextNormalizer:
    """Text normalizer for filter comparison operators.

    Provides case-sensitive or case-insensitive text matching for
    filter predicates.

    Attributes:
        _case_sensitive: Whether to preserve case during normalization.
        _memory_normalizer: Memory text normalizer instance.
    """

    def __init__(self, *, case_sensitive: bool) -> None:
        """Initialize the filter text normalizer.

        Args:
            case_sensitive: Whether to preserve case.
        """
        self._case_sensitive = case_sensitive
        self._memory_normalizer = MemoryTextNormalizer()

    def __call__(self, value: object) -> str | None:
        """Normalize value for filter comparison.

        Args:
            value: Value to normalize.

        Returns:
            Normalized string or None if value is None.
        """
        if value is None:
            return None
        text = str(value)
        if self._case_sensitive:
            return text
        return self._memory_normalizer.normalize_text(text)


def sql_like_to_regex(pattern: str) -> str:
    """Convert SQL LIKE pattern to equivalent regex.

    Handles SQL wildcards:
    - % becomes .*
    - _ becomes .
    - \\\\ escapes next character

    Args:
        pattern: SQL LIKE pattern string.

    Returns:
        Equivalent regex pattern string.
    """
    mapping = {"%": ".*", "_": "."}
    iterator = iter(pattern)
    regex: list[str] = []
    append = regex.append
    for char in iterator:
        if char == "\\":
            append(re.escape(next(iterator, "\\")))
            continue
        append(mapping.get(char, re.escape(char)))
    return "".join(regex)


def build_like_regex(pattern: str, *, escape: str | None = None) -> re.Pattern[str]:
    """Build compiled regex from SQL LIKE pattern.

    Args:
        pattern: SQL LIKE pattern.
        escape: Optional escape character.

    Returns:
        Compiled regular expression.
    """
    regex = sql_like_to_regex(pattern)
    if escape:
        escaped = re.escape(escape)
        regex = regex.replace(escaped, re.escape(escape))
    return re.compile(regex)


def compile_regex(pattern: str, *, flags: int = 0) -> re.Pattern[str]:
    """Compile regex pattern with validation.

    Args:
        pattern: Regular expression pattern.
        flags: Regex compilation flags.

    Returns:
        Compiled regular expression.

    Raises:
        FilterValidationError: If pattern is invalid.
    """
    try:
        return re.compile(pattern, flags=flags)
    except re.error as exc:  # pragma: no cover - defensive guard
        raise FilterValidationError(
            "Invalid regular expression pattern",
            details={"pattern": pattern, "error": str(exc)},
        ) from exc


def normalise_regex_argument(
    pattern: object,
    *,
    normalizer: FilterTextNormalizer,
    case_sensitive: bool,
) -> str:
    """Normalize regex pattern argument for filter operators.

    Args:
        pattern: Pattern to normalize.
        normalizer: Text normalizer to use.
        case_sensitive: Whether normalization is case-sensitive.

    Returns:
        Normalized pattern string.

    Raises:
        FilterValidationError: If pattern is not a string.
    """
    text = _ensure_string(pattern)
    if case_sensitive:
        return text
    normalized = normalizer(text)
    return normalized if normalized is not None else text


def _ensure_string(value: object) -> str:
    """Validate that value is a string.

    Args:
        value: Value to validate.

    Returns:
        The validated string.

    Raises:
        FilterValidationError: If value is not a string.
    """
    if isinstance(value, str):
        return value
    raise FilterValidationError(
        "Regex operators require string patterns",
        details={"pattern": value},
    )


__all__ = [
    "FilterTextNormalizer",
    "build_like_regex",
    "compile_regex",
    "normalise_regex_argument",
    "sql_like_to_regex",
]
