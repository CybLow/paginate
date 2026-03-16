"""Filter operators for in-memory predicate evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol, runtime_checkable

from pypaginate.domain.exceptions import FilterError, FilterValidationError
from pypaginate.filtering.like import match_ilike, match_like
from pypaginate.filtering.regex import compile_pattern


@runtime_checkable
class Operator(Protocol):
    """Protocol for filter operators."""

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool: ...


class Eq:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return field_value == spec_value


class Ne:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return field_value != spec_value


class Gt:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return bool(field_value > spec_value)  # type: ignore[operator]


class Gte:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return bool(field_value >= spec_value)  # type: ignore[operator]


class Lt:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return bool(field_value < spec_value)  # type: ignore[operator]


class Lte:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return bool(field_value <= spec_value)  # type: ignore[operator]


class In:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return field_value in spec_value  # type: ignore[operator]


class NotIn:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return field_value not in spec_value  # type: ignore[operator]


class Contains:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return str(spec_value) in str(field_value)


class StartsWith:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return str(field_value).startswith(str(spec_value))


class EndsWith:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return str(field_value).endswith(str(spec_value))


class Like:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return match_like(str(field_value), str(spec_value))


class ILike:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return match_ilike(str(field_value), str(spec_value))


class Between:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        low, high = _unpack_pair(spec_value)
        return bool(low <= field_value <= high)


class IsNull:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, _spec_value: object) -> bool:
        return field_value is None


class IsNotNull:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, _spec_value: object) -> bool:
        return field_value is not None


class Regex:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        pattern = str(spec_value)
        try:
            compiled = compile_pattern(pattern)
            return bool(compiled.search(str(field_value)))
        except Exception as exc:
            raise FilterError(
                f"Invalid regex pattern: '{pattern}'",
                details={"pattern": pattern, "error": str(exc)},
            ) from exc


class Empty:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, _spec_value: object) -> bool:
        return field_value is None or field_value in ("", [])


class NotEmpty:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, _spec_value: object) -> bool:
        return field_value is not None and field_value not in ("", [])


class Exists:
    __slots__ = ()

    @staticmethod
    def evaluate(_field_value: object, _spec_value: object) -> bool:
        return True


def _unpack_pair(value: object) -> tuple[Any, Any]:
    """Unpack a two-element sequence for Between."""
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
    "Empty",
    "EndsWith",
    "Eq",
    "Exists",
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
    "NotEmpty",
    "NotIn",
    "Operator",
    "Regex",
    "StartsWith",
]
