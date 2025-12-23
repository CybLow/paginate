"""Validation helpers for operator arguments."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import TypeGuard

from pypaginator.exceptions import FilterValidationError


def ensure_collection(argument: object, operator: str) -> Sequence[object]:
    """Ensure that ``argument`` is a non-mapping collection.

    Args:
        argument: Input value to validate.
        operator: Operator name for error reporting context.

    Returns:
        A sequence of objects materialized from ``argument``.

    Raises:
        FilterValidationError: If ``argument`` is ``None`` or a mapping.
    """
    if argument is None:
        raise _null_collection_error(operator)
    if isinstance(argument, Mapping):
        raise _mapping_collection_error(argument, operator)
    return _materialize_collection(argument)


def ensure_pair(argument: object, operator: str) -> tuple[object, object]:
    """Validate that ``argument`` is a two-element sequence.

    Args:
        argument: Input value to validate.
        operator: Operator name for error reporting context.

    Returns:
        The two elements of the sequence as a tuple.

    Raises:
        FilterValidationError: If the input is not a two-element sequence.
    """
    if not _is_pair_sequence(argument):
        raise _pair_error(argument, operator)
    sequence = tuple(argument)
    if len(sequence) != 2:
        raise _pair_error(argument, operator)
    return sequence[0], sequence[1]


def _null_collection_error(operator: str) -> FilterValidationError:
    """Build an error for null collections.

    Args:
        operator: Operator name for error context.

    Returns:
        FilterValidationError instance.
    """
    return FilterValidationError(
        f"Operator '{operator}' requires a non-null collection",
        details={"operator": operator},
    )


def _mapping_collection_error(
    argument: Mapping[object, object], operator: str
) -> FilterValidationError:
    """Build an error for mapping payloads where a collection is required.

    Args:
        argument: Invalid mapping argument.
        operator: Operator name for error context.

    Returns:
        FilterValidationError instance.
    """
    return FilterValidationError(
        f"Operator '{operator}' does not accept mapping payloads",
        details={"operator": operator, "payload": argument},
    )


def _pair_error(argument: object, operator: str) -> FilterValidationError:
    """Build an error describing an invalid pair argument.

    Args:
        argument: Invalid argument value.
        operator: Operator name for error context.

    Returns:
        FilterValidationError instance.
    """
    return FilterValidationError(
        f"Operator '{operator}' expects a pair of values",
        details={"operator": operator, "payload": argument},
    )


def _is_pair_sequence(argument: object) -> TypeGuard[Sequence[object]]:
    """Return ``True`` when ``argument`` is a non-string sequence.

    Args:
        argument: Value to check.

    Returns:
        True if argument is a sequence (not string/bytes).
    """
    return isinstance(argument, Sequence) and not isinstance(argument, (str, bytes))


def _materialize_collection(argument: object) -> Sequence[object]:
    """Convert an arbitrary value into a sequence suitable for membership tests.

    Args:
        argument: Value to convert.

    Returns:
        A sequence representation of the argument.
    """
    if isinstance(argument, Sequence) and not isinstance(argument, (str, bytes)):
        return argument
    if isinstance(argument, Iterable) and not isinstance(argument, (str, bytes)):
        return tuple(argument)
    return (argument,)


__all__ = ["ensure_collection", "ensure_pair"]
