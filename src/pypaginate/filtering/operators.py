"""Filter operators for in-memory predicate evaluation."""

from __future__ import annotations

import re
from collections.abc import Iterable
from fnmatch import fnmatch
from typing import Any, Protocol, runtime_checkable

from pypaginate.domain.exceptions import FilterError, FilterValidationError


@runtime_checkable
class Operator(Protocol):
    """Protocol for filter operators."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Return True if field_value satisfies the condition."""
        ...


class Eq:
    """Equality operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field == value."""
        return field_value == spec_value


class Ne:
    """Not-equal operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field != value."""
        return field_value != spec_value


class Gt:
    """Greater-than operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field > value."""
        return bool(field_value > spec_value)  # type: ignore[operator]


class Gte:
    """Greater-than-or-equal operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field >= value."""
        return bool(field_value >= spec_value)  # type: ignore[operator]


class Lt:
    """Less-than operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field < value."""
        return bool(field_value < spec_value)  # type: ignore[operator]


class Lte:
    """Less-than-or-equal operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field <= value."""
        return bool(field_value <= spec_value)  # type: ignore[operator]


class In:
    """Membership operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field in value."""
        return field_value in spec_value  # type: ignore[operator]


class NotIn:
    """Non-membership operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field not in value."""
        return field_value not in spec_value  # type: ignore[operator]


class Contains:
    """Substring containment operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check spec_value is substring of field_value."""
        return str(spec_value) in str(field_value)


class StartsWith:
    """String prefix operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field starts with value."""
        return str(field_value).startswith(str(spec_value))


class EndsWith:
    """String suffix operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field ends with value."""
        return str(field_value).endswith(str(spec_value))


class Like:
    """SQL-style LIKE with % and _ wildcards."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field matches LIKE pattern (case-sensitive)."""
        pattern = _like_to_glob(str(spec_value))
        return fnmatch(str(field_value), pattern)


class ILike:
    """Case-insensitive LIKE operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field matches LIKE pattern (case-insensitive)."""
        pattern = _like_to_glob(str(spec_value))
        return fnmatch(str(field_value).lower(), pattern.lower())


class Between:
    """Range check operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check low <= field <= high."""
        low, high = _unpack_pair(spec_value)
        return bool(low <= field_value <= high)


class IsNull:
    """Null check operator."""

    @staticmethod
    def evaluate(field_value: object, _spec_value: object) -> bool:
        """Check field is None."""
        return field_value is None


class IsNotNull:
    """Non-null check operator."""

    @staticmethod
    def evaluate(field_value: object, _spec_value: object) -> bool:
        """Check field is not None."""
        return field_value is not None


class Regex:
    """Regular expression operator."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        """Check field matches regex pattern."""
        pattern = str(spec_value)
        try:
            return bool(re.search(pattern, str(field_value)))
        except re.error as exc:
            raise FilterError(
                f"Invalid regex pattern: '{pattern}'",
                details={"pattern": pattern, "error": str(exc)},
            ) from exc


def _like_to_glob(pattern: str) -> str:
    """Convert SQL LIKE pattern to fnmatch glob pattern."""
    return pattern.replace("%", "*").replace("_", "?")


def _unpack_pair(value: object) -> tuple[Any, Any]:
    """Unpack a two-element sequence for Between operator."""
    if not isinstance(value, Iterable):
        raise FilterValidationError(
            "Between requires a two-element sequence",
            details={"value": repr(value), "type": type(value).__name__},
        )
    seq = list(value)
    if len(seq) != 2:
        raise FilterValidationError(
            "Between requires exactly 2 elements",
            details={"value": repr(value), "length": len(seq)},
        )
    return seq[0], seq[1]


__all__ = [
    "Between",
    "Contains",
    "EndsWith",
    "Eq",
    "Gt",
    "Gte",
    "ILike",
    "In",
    "IsNotNull",
    "IsNull",
    "Like",
    "Lt",
    "Lte",
    "Ne",
    "NotIn",
    "Operator",
    "Regex",
    "StartsWith",
]
