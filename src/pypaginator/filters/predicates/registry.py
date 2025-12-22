"""Registry of filter operator factories."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, TypeVar, cast

from ....exceptions import FilterValidationError

if TYPE_CHECKING:
    from collections.abc import Sequence

# Predicate Type Aliases
CandidateT = TypeVar("CandidateT", contravariant=True)
"""Contravariant type variable for filter predicate candidates."""

FilterPredicate = Callable[[CandidateT], bool]
"""Callable type for filter predicates.

A predicate accepts a candidate value and returns True if it matches.
"""

OperatorFactory = Callable[[object], FilterPredicate[CandidateT]]
"""Callable type for factories creating predicates from arguments.

A factory accepts an argument and returns a configured predicate.
"""


# Registry
CandidateT_inv = TypeVar("CandidateT_inv")
"""Invariant type variable for operator registry."""


class OperatorRegistry(Generic[CandidateT_inv]):
    """Mapping of operator names to predicate factories.

    Methods:
        register: Associate one or more names with a factory.
        build: Build a predicate from a registered name and argument.
        default: Create a registry pre-populated with standard operators.
    """

    def __init__(self) -> None:
        """Initialize an empty operator registry."""
        self._factories: dict[str, OperatorFactory[CandidateT_inv]] = {}

    def register(
        self, names: Sequence[str], factory: OperatorFactory[CandidateT_inv]
    ) -> None:
        """Register a factory for a list of operator names.

        Args:
            names: List of operator name aliases.
            factory: Factory function creating predicates.
        """
        for name in names:
            self._factories[name] = factory

    def build(self, name: str, argument: object) -> FilterPredicate[CandidateT_inv]:
        """Return a predicate by resolving name with argument.

        Args:
            name: Operator name to resolve.
            argument: Argument to pass to the operator factory.

        Returns:
            A predicate function for filtering.

        Raises:
            FilterValidationError: If name is not registered.
        """
        try:
            factory = self._factories[name]
        except KeyError as error:
            raise FilterValidationError(
                f"Unsupported filter operator '{name}'",
                details={"operator": name},
            ) from error
        return factory(argument)

    @classmethod
    def default(cls) -> OperatorRegistry[object]:
        """Create a registry pre-populated with standard operators.

        Returns:
            A new OperatorRegistry with default operators registered.
        """
        from .operators import register_default_operators

        registry = cast("OperatorRegistry[object]", cls())
        register_default_operators(registry)
        return registry


__all__ = ["OperatorRegistry", "FilterPredicate", "OperatorFactory"]

