"""Pattern-based filtering operators."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pypaginate.exceptions import FilterValidationError

from ....text.api import (
    FilterTextNormalizer,
    build_like_regex,
    compile_regex,
    normalise_regex_argument,
)


if TYPE_CHECKING:
    from ..registry import FilterPredicate


@dataclass(frozen=True)
class LikeFactory:
    """Factory implementing SQL LIKE semantics in memory.

    Attributes:
        name: Operator label for error reporting context.
        case_sensitive: Whether comparisons should be case-sensitive.
    """

    name: str
    case_sensitive: bool

    def __call__(self, argument: object) -> FilterPredicate[object]:
        """Build a LIKE pattern matching predicate.

        Args:
            argument: SQL LIKE pattern with % and _ wildcards.

        Returns:
            A predicate applying regex-converted LIKE matching.

        Raises:
            FilterValidationError: If pattern is None.
        """
        normalizer = FilterTextNormalizer(case_sensitive=self.case_sensitive)
        pattern = normalizer(argument)
        if pattern is None:
            raise FilterValidationError(
                "Operator 'like' requires a non-null pattern",
                details={"operator": self.name},
            )
        regex = build_like_regex(pattern)
        return self._predicate(normalizer, regex)

    @staticmethod
    def _predicate(
        normalizer: FilterTextNormalizer, regex: re.Pattern[str]
    ) -> FilterPredicate[object]:
        """Return a predicate applying a compiled LIKE regex to candidates.

        Args:
            normalizer: Text normalizer for candidates.
            regex: Compiled regex pattern from LIKE conversion.

        Returns:
            A predicate function for LIKE matching.
        """

        def _apply(candidate: object) -> bool:
            text = normalizer(candidate)
            return bool(text and regex.fullmatch(text))

        return _apply


@dataclass(frozen=True)
class RegexFactory:
    """Factory compiling safe regular expressions.

    Attributes:
        name: Operator label for error reporting context.
        case_sensitive: Whether the regular expression is case-sensitive.
    """

    name: str
    case_sensitive: bool

    def __call__(self, argument: object) -> FilterPredicate[object]:
        """Build a regex matching predicate.

        Args:
            argument: Regular expression pattern string.

        Returns:
            A predicate applying the compiled regex.

        Raises:
            FilterValidationError: If pattern compilation fails.
        """
        normalizer = FilterTextNormalizer(case_sensitive=self.case_sensitive)
        pattern = normalise_regex_argument(
            argument,
            normalizer=normalizer,
            case_sensitive=self.case_sensitive,
        )
        flags = 0 if self.case_sensitive else re.IGNORECASE
        compiled = compile_regex(pattern, flags=flags)
        return self._predicate(normalizer, compiled)

    @staticmethod
    def _predicate(
        normalizer: FilterTextNormalizer, compiled: re.Pattern[str]
    ) -> FilterPredicate[object]:
        """Return a predicate applying the compiled regex to candidates.

        Args:
            normalizer: Text normalizer for candidates.
            compiled: Compiled regular expression.

        Returns:
            A predicate function for regex matching.
        """

        def _apply(candidate: object) -> bool:
            text = normalizer(candidate)
            return bool(text and compiled.search(text))

        return _apply


__all__ = ["LikeFactory", "RegexFactory"]
