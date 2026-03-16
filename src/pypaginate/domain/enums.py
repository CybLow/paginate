"""Essential enums replacing boolean parameters across pypaginate.

Each enum replaces primitive boolean flags with a self-documenting
type, following the Replace Type Code with Class refactoring.
"""

from __future__ import annotations

from enum import Enum, auto


class OverflowStrategy(Enum):
    """How to handle page numbers exceeding total pages."""

    CLAMP = auto()
    EMPTY = auto()


class SortDirection(Enum):
    """Sort direction for ordering."""

    ASC = auto()
    DESC = auto()


class NullsPosition(Enum):
    """Where to place NULL values in sorted results."""

    FIRST = auto()
    LAST = auto()


class FilterLogic(Enum):
    """Logical operator for combining filter conditions."""

    AND = auto()
    OR = auto()


class SearchFieldMode(Enum):
    """How to match search terms against fields."""

    PREFIX = auto()
    CONTAINS = auto()
    EXACT = auto()


class FuzzyMode(Enum):
    """Fuzzy matching strategy for search."""

    EXACT = auto()
    FUZZY = auto()
    TOKEN_SORT = auto()


__all__ = [
    "FilterLogic",
    "FuzzyMode",
    "NullsPosition",
    "OverflowStrategy",
    "SearchFieldMode",
    "SortDirection",
]
