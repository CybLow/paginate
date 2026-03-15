"""Filter operators for in-memory predicate evaluation.

Each operator implements the ``Operator`` protocol with a single
``evaluate`` method that compares a field value against a spec value.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from fnmatch import fnmatch
from typing import Any, Protocol, runtime_checkable

from pypaginate.domain.exceptions import FilterError, FilterValidationError


@runtime_checkable
class Operator(Protocol):
    """Protocol for filter operators."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        """Return True if the field value satisfies the operator condition.

        Args:
            field_value: The value extracted from the item.
            spec_value: The value from the filter specification.

        Returns:
            True when the condition is satisfied.
        """
        ...


class Eq:
    """Equality: field == value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return field_value == spec_value


class Ne:
    """Not-equal: field != value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return field_value != spec_value


class Gt:
    """Greater than: field > value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return bool(field_value > spec_value)  # type: ignore[operator]


class Gte:
    """Greater than or equal: field >= value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return bool(field_value >= spec_value)  # type: ignore[operator]


class Lt:
    """Less than: field < value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return bool(field_value < spec_value)  # type: ignore[operator]


class Lte:
    """Less than or equal: field <= value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return bool(field_value <= spec_value)  # type: ignore[operator]


class In:
    """Membership: field in value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return field_value in spec_value  # type: ignore[operator]


class NotIn:
    """Non-membership: field not in value."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return field_value not in spec_value  # type: ignore[operator]


class Contains:
    """Substring containment (case-sensitive)."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return str(spec_value) in str(field_value)


class StartsWith:
    """String prefix match (case-sensitive)."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return str(field_value).startswith(str(spec_value))


class EndsWith:
    """String suffix match (case-sensitive)."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        return str(field_value).endswith(str(spec_value))


class Like:
    """SQL-style LIKE with ``%`` and ``_`` wildcards (case-sensitive)."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        pattern = _like_to_glob(str(spec_value))
        return fnmatch(str(field_value), pattern)


class ILike:
    """SQL-style ILIKE (case-insensitive LIKE)."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        pattern = _like_to_glob(str(spec_value))
        return fnmatch(str(field_value).lower(), pattern.lower())


class Between:
    """Range check: low <= field <= high."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        low, high = _unpack_pair(spec_value)
        return bool(low <= field_value <= high)


class IsNull:
    """Null check: field is None."""

    def evaluate(self, field_value: object, _spec_value: object) -> bool:
        return field_value is None


class IsNotNull:
    """Non-null check: field is not None."""

    def evaluate(self, field_value: object, _spec_value: object) -> bool:
        return field_value is not None


class Regex:
    """Regular expression match."""

    def evaluate(self, field_value: object, spec_value: object) -> bool:
        pattern = str(spec_value)
        try:
            return bool(re.search(pattern, str(field_value)))
        except re.error as exc:
            raise FilterError(
                f"Invalid regex pattern: '{pattern}'",
                details={"pattern": pattern, "error": str(exc)},
            ) from exc


# -- helpers -----------------------------------------------------------------


def _like_to_glob(pattern: str) -> str:
    """Convert SQL LIKE pattern to fnmatch glob pattern."""
    return pattern.replace("%", "*").replace("_", "?")


def _unpack_pair(value: object) -> tuple[Any, Any]:
    """Unpack a two-element sequence for Between."""
    if not isinstance(value, Iterable):
        raise FilterValidationError(
            "Between operator requires a two-element sequence",
            details={"value": repr(value), "type": type(value).__name__},
        )
    seq = list(value)
    if len(seq) != 2:
        raise FilterValidationError(
            "Between operator requires exactly 2 elements",
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
