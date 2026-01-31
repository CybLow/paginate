"""Range-based operator factories."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from ..operator_arguments import ensure_pair


if TYPE_CHECKING:
    from ....types import SupportsTotalOrdering
    from ..registry import FilterPredicate


def _within_bounds(candidate: object, lower: object, upper: object) -> bool:
    """Return True when candidate is within inclusive bounds.

    Args:
        candidate: Value to check.
        lower: Lower bound (inclusive).
        upper: Upper bound (inclusive).

    Returns:
        True if lower <= candidate <= upper, False otherwise.
    """
    if None in (candidate, lower, upper):
        return False
    try:
        low = cast("SupportsTotalOrdering", lower)
        high = cast("SupportsTotalOrdering", upper)
        value = cast("SupportsTotalOrdering", candidate)
        return bool(low <= value <= high)
    except TypeError:
        return False


@dataclass(frozen=True)
class RangeFactory:
    """Factory for between/range operators."""

    name: str

    def __call__(self, argument: object) -> FilterPredicate[object]:
        """Build a predicate checking if values fall within provided bounds.

        Args:
            argument: Two-element sequence [lower, upper].

        Returns:
            A predicate testing range membership.

        Raises:
            FilterValidationError: If argument is not a valid pair.
        """
        lower, upper = ensure_pair(argument, self.name)

        def _predicate(candidate: object) -> bool:
            return _within_bounds(candidate, lower, upper)

        return _predicate


__all__ = ["RangeFactory"]
