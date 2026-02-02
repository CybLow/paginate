"""Validation helpers for SQL search pagination options."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TypedDict

from pypaginate.exceptions import SearchQueryError

from .conditions import SearchMode


DEFAULT_SEARCH_MODE: SearchMode = SearchMode.AND
"""Default search mode used when none is specified."""


class ContextOptions(TypedDict):
    """Keyword arguments passed to SqlConditionBuilder.context.

    Attributes:
        prefix: Whether to use prefix matching for search terms.
        id_fields: Tuple of field names to search for identifiers.
        id_token_regex: Compiled regex pattern to detect ID tokens.
    """

    prefix: bool
    id_fields: tuple[str, ...]
    id_token_regex: re.Pattern[str]


class SearchOptions(TypedDict, total=False):
    """User facing options supported by the SQL search service.

    Attributes:
        mode: Search mode (AND/OR).
        prefix: Whether to use prefix matching.
        id_fields: Sequence of field names for ID matching.
        id_token_regex: Compiled regex to detect identifier tokens.
    """

    mode: SearchMode
    prefix: bool
    id_fields: Sequence[str]
    id_token_regex: re.Pattern[str]


@dataclass(frozen=True)
class ResolvedOptions:
    """Internal representation consumed by the condition builder.

    Attributes:
        mode: Validated search mode.
        context: Context options for the condition builder.
    """

    mode: SearchMode
    context: ContextOptions


@dataclass(frozen=True)
class SearchOptionSet:
    """Validated tuple mirroring SearchOptions.

    Attributes:
        mode: Search mode (AND/OR).
        prefix: Whether to use prefix matching.
        id_fields: Tuple of field names for ID matching.
        id_token_regex: Compiled regex for ID token detection.
    """

    mode: SearchMode
    prefix: bool
    id_fields: tuple[str, ...]
    id_token_regex: re.Pattern[str]

    @classmethod
    def from_mapping(
        cls, options: Mapping[str, object], *, default_pattern: re.Pattern[str]
    ) -> SearchOptionSet:
        """Create a SearchOptionSet from a mapping of options.

        Args:
            options: User-provided options mapping.
            default_pattern: Default ID pattern if not provided.

        Returns:
            Validated SearchOptionSet instance.
        """
        mode = _coerce_mode_option(options.get("mode"))
        prefix = _coerce_bool_option(options.get("prefix"))
        id_fields = _coerce_field_option(options.get("id_fields"))
        pattern = _coerce_pattern_option(options.get("id_token_regex"), default_pattern)
        return cls(mode=mode, prefix=prefix, id_fields=id_fields, id_token_regex=pattern)


def resolve_options(
    options: Mapping[str, object], *, default_pattern: re.Pattern[str]
) -> ResolvedOptions:
    """Validate and normalize user-facing options to resolved values.

    Args:
        options: Mapping of supported options (mode, prefix, etc.).
        default_pattern: Default compiled regex for identifier tokens.

    Returns:
        Resolved options with a context suitable for the condition builder.
    """
    parsed = SearchOptionSet.from_mapping(options, default_pattern=default_pattern)
    return ResolvedOptions(mode=parsed.mode, context=_build_context(parsed))


def _build_context(parsed: SearchOptionSet) -> ContextOptions:
    """Construct ContextOptions from a parsed option set.

    Args:
        parsed: Validated search option set.

    Returns:
        ContextOptions for the condition builder.
    """
    return ContextOptions(
        prefix=parsed.prefix,
        id_fields=parsed.id_fields,
        id_token_regex=parsed.id_token_regex,
    )


_SUPPORTED_MODES: tuple[SearchMode, ...] = (
    SearchMode.AND,
    SearchMode.OR,
)
"""Tuple of supported search modes for SQL search."""


def _validate_supported_mode(mode: SearchMode) -> None:
    """Validate that mode is in the supported modes list.

    Args:
        mode: Search mode to validate.

    Raises:
        SearchQueryError: If mode is unsupported.
    """
    if mode not in _SUPPORTED_MODES:
        raise SearchQueryError(
            "Unsupported search mode",
            details={"mode": mode.value},
        )


def _parse_string_mode(value: str) -> SearchMode:
    """Parse string value into SearchMode enum.

    Args:
        value: String mode value.

    Returns:
        Parsed SearchMode.

    Raises:
        SearchQueryError: If value is invalid.
    """
    try:
        return SearchMode(value)
    except ValueError as error:
        raise SearchQueryError(
            "Unsupported search mode",
            details={"mode": value},
        ) from error


def _coerce_mode_option(value: object | None) -> SearchMode:
    """Coerce and validate search mode from various input types.

    Args:
        value: Mode value to coerce.

    Returns:
        Validated SearchMode.

    Raises:
        SearchQueryError: If value is invalid.
    """
    if value is None:
        return DEFAULT_SEARCH_MODE

    if isinstance(value, SearchMode):
        _validate_supported_mode(value)
        return value

    if isinstance(value, str):
        mode = _parse_string_mode(value)
        _validate_supported_mode(mode)
        return mode

    raise SearchQueryError("Unsupported search mode", details={"mode": value})


def _coerce_bool_option(value: object | None) -> bool:
    """Coerce prefix option to boolean.

    Args:
        value: Value to coerce.

    Returns:
        Boolean value.

    Raises:
        SearchQueryError: If value is not None or bool.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    raise SearchQueryError(
        "prefix must be a boolean when provided",
        details={"prefix": value},
    )


def _coerce_field_option(value: object | None) -> tuple[str, ...]:
    """Coerce id_fields option to tuple of strings.

    Args:
        value: Value to coerce.

    Returns:
        Tuple of field names.

    Raises:
        SearchQueryError: If value is invalid.
    """
    if value is None:
        return ()
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return tuple(_iter_string_values(value))
    raise SearchQueryError(
        "id_fields must be a sequence of strings when provided",
        details={"id_fields": value},
    )


def _iter_string_values(values: Sequence[object]) -> list[str]:
    """Extract string values from a sequence.

    Args:
        values: Sequence to process.

    Returns:
        List of string values.

    Raises:
        SearchQueryError: If non-string values found.
    """
    fields: list[str] = []
    for field in values:
        if not isinstance(field, str):
            raise SearchQueryError(
                "id_fields must contain only strings",
                details={"invalid_field": field},
            )
        fields.append(field)
    return fields


def _coerce_pattern_option(value: object | None, default: re.Pattern[str]) -> re.Pattern[str]:
    """Coerce id_token_regex option to compiled pattern.

    Args:
        value: Value to coerce.
        default: Default pattern if value is None.

    Returns:
        Compiled regex pattern.

    Raises:
        SearchQueryError: If value is invalid.
    """
    if value is None:
        return default
    if isinstance(value, re.Pattern):
        return value
    raise SearchQueryError(
        "id_token_regex must be a compiled regular expression when provided",
        details={"id_token_regex": value},
    )


__all__ = [
    "DEFAULT_SEARCH_MODE",
    "ContextOptions",
    "ResolvedOptions",
    "SearchOptionSet",
    "SearchOptions",
    "resolve_options",
]
