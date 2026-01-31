"""Registration helpers for default filter operator factories."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Final

from .comparison import COMPARATORS, EqualityFactory, OrderingFactory
from .patterns import LikeFactory, RegexFactory
from .range import RangeFactory
from .simple import EmptyFactory, MembershipFactory, NullityFactory
from .text import TextFactory


if TYPE_CHECKING:  # pragma: no cover - import cycle guard
    from ..registry import OperatorRegistry

__all__ = [
    "EmptyFactory",
    "EqualityFactory",
    "LikeFactory",
    "MembershipFactory",
    "NullityFactory",
    "OrderingFactory",
    "RangeFactory",
    "RegexFactory",
    "TextFactory",
    "register_default_operators",
]


def register_default_operators(registry: OperatorRegistry[object]) -> None:
    """Populate the registry with the standard operator factories.

    Args:
        registry: Registry receiving default operator factory bindings.
    """
    _register_basic(registry)
    _register_ordering(registry)
    _register_membership(registry)
    _register_ranges(registry)
    _register_text(registry)
    _register_like(registry)
    _register_regex(registry)
    _register_nullity(registry)
    _register_empty(registry)


def _register_basic(registry: OperatorRegistry[object]) -> None:
    """Register equality and inequality operators.

    Args:
        registry: Registry to register operators in.
    """
    registry.register(["eq"], EqualityFactory())
    registry.register(["ne"], EqualityFactory(negate=True))


def _register_ordering(registry: OperatorRegistry[object]) -> None:
    """Register ordering operators based on the comparator map.

    Args:
        registry: Registry to register operators in.
    """
    for name, comparator in COMPARATORS.items():
        registry.register([name], OrderingFactory(name, comparator))


def _register_membership(registry: OperatorRegistry[object]) -> None:
    """Register in and negated membership operators.

    Args:
        registry: Registry to register operators in.
    """
    registry.register(["in"], MembershipFactory("in"))
    registry.register(["not_in", "notin"], MembershipFactory("not_in", invert=True))


def _register_ranges(registry: OperatorRegistry[object]) -> None:
    """Register inclusive range and generic range operators.

    Args:
        registry: Registry to register operators in.
    """
    registry.register(["between"], RangeFactory("between"))
    registry.register(["range"], RangeFactory("range"))


_TextMatcher = Callable[[str, str], bool]


def _contains(hay: str, ndl: str) -> bool:
    """Check if needle is contained in haystack.

    Args:
        hay: Haystack string to search in.
        ndl: Needle string to search for.

    Returns:
        True if needle is in haystack.
    """
    return ndl in hay


def _startswith(hay: str, ndl: str) -> bool:
    """Check if haystack starts with needle.

    Args:
        hay: Haystack string to check.
        ndl: Needle prefix to search for.

    Returns:
        True if haystack starts with needle.
    """
    return hay.startswith(ndl)


def _endswith(hay: str, ndl: str) -> bool:
    """Check if haystack ends with needle.

    Args:
        hay: Haystack string to check.
        ndl: Needle suffix to search for.

    Returns:
        True if haystack ends with needle.
    """
    return hay.endswith(ndl)


_TEXT_OPERATORS: Final[tuple[tuple[list[str], str, _TextMatcher, bool], ...]] = (
    (["contains"], "contains", _contains, True),
    (["icontains"], "icontains", _contains, False),
    (["startswith"], "startswith", _startswith, True),
    (["istartswith"], "istartswith", _startswith, False),
    (["endswith"], "endswith", _endswith, True),
    (["iendswith"], "iendswith", _endswith, False),
)


def _register_text(registry: OperatorRegistry[object]) -> None:
    """Register contains/starts/ends text operators (case-sensitive/insensitive).

    Args:
        registry: Registry to register operators in.
    """
    for names, label, matcher, case_sensitive in _TEXT_OPERATORS:
        registry.register(
            names,
            TextFactory(label, matcher, case_sensitive=case_sensitive),
        )


def _register_like(registry: OperatorRegistry[object]) -> None:
    """Register SQL LIKE and ILIKE operators.

    Args:
        registry: Registry to register operators in.
    """
    registry.register(["like"], LikeFactory("like", case_sensitive=True))
    registry.register(["ilike"], LikeFactory("ilike", case_sensitive=False))


def _register_regex(registry: OperatorRegistry[object]) -> None:
    """Register regex and case-insensitive regex operators.

    Args:
        registry: Registry to register operators in.
    """
    registry.register(["regex"], RegexFactory("regex", case_sensitive=True))
    registry.register(["iregex"], RegexFactory("iregex", case_sensitive=False))


def _register_nullity(registry: OperatorRegistry[object]) -> None:
    """Register nullity operators (is_null/is_not_null).

    Args:
        registry: Registry to register operators in.
    """
    registry.register(["is_null"], NullityFactory(expect_null=True))
    registry.register(["is_not_null"], NullityFactory(expect_null=False))


def _register_empty(registry: OperatorRegistry[object]) -> None:
    """Register emptiness operators (empty/not_empty).

    Args:
        registry: Registry to register operators in.
    """
    registry.register(["empty"], EmptyFactory(expect_empty=True))
    registry.register(["not_empty"], EmptyFactory(expect_empty=False))
