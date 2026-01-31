"""Text comparison operator factories."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pypaginate.exceptions import FilterValidationError

from ....text.api import FilterTextNormalizer


if TYPE_CHECKING:
    from collections.abc import Callable

    from ..registry import FilterPredicate


@dataclass(frozen=True)
class TextFactory:
    """Factory applying text matchers with consistent normalisation.

    Attributes:
        name: Operator label for error messages.
        matcher: Callable implementing the string comparison.
        case_sensitive: Whether to preserve case during normalization.
    """

    name: str
    matcher: Callable[[str, str], bool]
    case_sensitive: bool

    def __call__(self, argument: object) -> FilterPredicate[object]:
        """Build a text matching predicate.

        Args:
            argument: Text pattern to match.

        Returns:
            A predicate applying the text matcher.

        Raises:
            FilterValidationError: If argument is None.
        """
        normalizer = FilterTextNormalizer(case_sensitive=self.case_sensitive)
        needle = self._normalize_argument(argument, normalizer)
        return self._predicate(normalizer, needle)

    def _normalize_argument(self, argument: object, normalizer: FilterTextNormalizer) -> str:
        """Normalize and validate the comparison needle argument.

        Args:
            argument: Pattern argument to normalize.
            normalizer: Text normalizer to use.

        Returns:
            Normalized pattern string.

        Raises:
            FilterValidationError: If argument normalizes to None.
        """
        if argument is None:
            raise self._null_error()
        needle = normalizer(argument)
        if needle is None:
            raise self._null_error()
        return needle

    def _predicate(self, normalizer: FilterTextNormalizer, needle: str) -> FilterPredicate[object]:
        """Return a predicate applying the configured matcher to candidates.

        Args:
            normalizer: Text normalizer for candidates.
            needle: Normalized pattern to match.

        Returns:
            A predicate function for text matching.
        """

        def _apply(candidate: object) -> bool:
            haystack = normalizer(candidate)
            return bool(haystack and self.matcher(haystack, needle))

        return _apply

    def _null_error(self) -> FilterValidationError:
        """Build error for null text pattern.

        Returns:
            A FilterValidationError instance.
        """
        return FilterValidationError(
            f"Operator '{self.name}' requires a non-null term",
            details={"operator": self.name},
        )


__all__ = ["TextFactory"]
