"""Equality and ordering operator factories."""

from __future__ import annotations

from dataclasses import dataclass
from operator import eq, ge, gt, le, lt, ne
from typing import TYPE_CHECKING, cast

from .....exceptions import FilterValidationError

if TYPE_CHECKING:
    from collections.abc import Callable

    from ....types import SupportsTotalOrdering
    from ..registry import FilterPredicate


@dataclass(frozen=True)
class EqualityFactory:
    """Factory producing equality and inequality predicates.

    Attributes:
        negate: When ``True``, produce a ``!=`` predicate instead of ``==``.
    """

    negate: bool = False

    def __call__(self, reference: object) -> FilterPredicate[object]:
        """Build a predicate comparing candidates to reference.

        Args:
            reference: Value to compare against.

        Returns:
            A predicate function for equality/inequality checks.
        """
        comparator: Callable[[object, object], bool] = ne if self.negate else eq
        return lambda candidate: bool(comparator(candidate, reference))


@dataclass(frozen=True)
class OrderingFactory:
    """Factory producing numeric ordering predicates with validation.

    Attributes:
        name: Operator name used for error reporting.
        comparator: Callable implementing the ordering relation.
    """

    name: str
    comparator: Callable[[SupportsTotalOrdering, SupportsTotalOrdering], bool]

    def __call__(self, reference: object) -> FilterPredicate[object]:
        """Build a predicate for ordering comparisons.

        Args:
            reference: Value to compare against.

        Returns:
            A predicate function for ordering checks.

        Raises:
            FilterValidationError: If reference is None.
        """
        if reference is None:
            raise _null_reference_error(self.name)
        return self._predicate(cast("SupportsTotalOrdering", reference))

    def _predicate(self, anchor: SupportsTotalOrdering) -> FilterPredicate[object]:
        """Create the ordering predicate with the anchor value.

        Args:
            anchor: Validated anchor value for comparisons.

        Returns:
            A predicate function applying the comparator.
        """
        comparator = self.comparator
        return _create_ordering_predicate(comparator, anchor)


def _create_ordering_predicate(
    comparator: Callable[[SupportsTotalOrdering, SupportsTotalOrdering], bool],
    anchor: SupportsTotalOrdering,
) -> FilterPredicate[object]:
    """Return a predicate comparing candidates against an anchor value.

    Args:
        comparator: Ordering comparison function.
        anchor: Value to compare against.

    Returns:
        A predicate function for ordering checks.
    """
    return lambda candidate: _compare_ordering(comparator, candidate, anchor)


def _compare_ordering(
    comparator: Callable[[SupportsTotalOrdering, SupportsTotalOrdering], bool],
    candidate: object,
    anchor: SupportsTotalOrdering,
) -> bool:
    """Safely evaluate the ordering relation, guarding None and TypeError.

    Args:
        comparator: Ordering comparison function.
        candidate: Value to check.
        anchor: Value to compare against.

    Returns:
        True if the comparison holds, False otherwise.
    """
    if candidate is None:
        return False
    try:
        return comparator(cast("SupportsTotalOrdering", candidate), anchor)
    except TypeError:
        return False


def _null_reference_error(operator: str) -> FilterValidationError:
    """Build an error for missing reference in ordering comparisons.

    Args:
        operator: Operator name for error context.

    Returns:
        A FilterValidationError instance.
    """
    return FilterValidationError(
        f"Operator '{operator}' requires a non-null reference",
        details={"operator": operator},
    )


COMPARATORS: dict[
    str, Callable[[SupportsTotalOrdering, SupportsTotalOrdering], bool]
] = {
    "gt": gt,
    "gte": ge,
    "lt": lt,
    "lte": le,
}


__all__ = ["EqualityFactory", "OrderingFactory", "COMPARATORS"]
