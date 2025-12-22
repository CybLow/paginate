"""Simple operator factories: membership, nullity, and emptiness checks."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..operator_arguments import ensure_collection

if TYPE_CHECKING:
    from ..registry import FilterPredicate



# Membership Operators

@dataclass(frozen=True)
class MembershipFactory:
    """Factory handling membership and negated membership operators.

    Attributes:
        name: Operator label for error reporting context.
        invert: When ``True``, negate membership semantics.
    """

    name: str
    invert: bool = False

    def __call__(self, argument: object) -> FilterPredicate[object]:
        """Build a membership predicate from argument.

        Args:
            argument: Collection of allowed values.

        Returns:
            A predicate checking membership in the collection.
        """
        collection = tuple(ensure_collection(argument, self.name))

        def _predicate(candidate: object) -> bool:
            contains = candidate in collection
            return not contains if self.invert else contains

        return _predicate



# Nullity Operators

@dataclass(frozen=True)
class NullityFactory:
    """Factory for ``is_null`` / ``is_not_null`` operators."""

    expect_null: bool

    def __call__(
        self, argument: object
    ) -> FilterPredicate[object]:  # noqa: ARG002 - signature contract
        """Return a predicate checking nullness according to configuration.

        Args:
            argument: Configuration flag (True/False/None).

        Returns:
            A predicate testing nullness.
        """
        flag = True if argument is None else bool(argument)

        def _predicate(candidate: object) -> bool:
            if self.expect_null:
                return (candidate is None) if flag else (candidate is not None)
            return (candidate is not None) if flag else (candidate is None)

        return _predicate



# Emptiness Operators

def _emptiness(candidate: object) -> bool | None:
    """Return True for empty containers, False for non-empty, None otherwise.

    Args:
        candidate: Value to check for emptiness.

    Returns:
        True if empty, False if non-empty, None if not a container.
    """
    if candidate is None:
        return True
    if isinstance(candidate, Collection):
        return len(candidate) == 0
    return None


@dataclass(frozen=True)
class EmptyFactory:
    """Factory for ``empty`` and ``not_empty`` operators."""

    expect_empty: bool

    def __call__(
        self, argument: object
    ) -> FilterPredicate[object]:  # noqa: ARG002 - signature contract
        """Return a predicate testing emptiness according to configuration.

        Args:
            argument: Configuration flag (ignored, uses expect_empty).

        Returns:
            A predicate testing container emptiness.
        """
        def _predicate(candidate: object) -> bool:
            state = _emptiness(candidate)
            if state is None:
                return not self.expect_empty
            return state is self.expect_empty

        return _predicate


__all__ = ["MembershipFactory", "NullityFactory", "EmptyFactory"]
