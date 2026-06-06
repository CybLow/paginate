"""Essential enums replacing boolean parameters across pypaginate.

Each enum replaces primitive boolean flags with a self-documenting type
(Replace Type Code with Class). Each member's **value is its canonical wire
token** — the exact string the Rust core's ``from_token`` parsers accept — so the
bridge to the native engine is just ``member.value`` (no mapping table) and the
tokens have a single home, shared with the TS package and pinned by the parity
fixture.
"""

from __future__ import annotations

from enum import Enum


class OverflowStrategy(Enum):
    """How to handle page numbers exceeding total pages."""

    CLAMP = "clamp"
    EMPTY = "empty"


class SortDirection(Enum):
    """Sort direction for ordering."""

    ASC = "asc"
    DESC = "desc"


class NullsPosition(Enum):
    """Where to place NULL values in sorted results."""

    FIRST = "first"
    LAST = "last"


class FilterLogic(Enum):
    """Logical operator for combining filter conditions."""

    AND = "and"
    OR = "or"


class SearchFieldMode(Enum):
    """How to match search terms against fields."""

    PREFIX = "prefix"
    CONTAINS = "contains"
    EXACT = "exact"


class FuzzyMode(Enum):
    """Fuzzy matching strategy for search."""

    EXACT = "exact"
    FUZZY = "fuzzy"
    TOKEN_SORT = "token_sort"


__all__ = [
    "FilterLogic",
    "FuzzyMode",
    "NullsPosition",
    "OverflowStrategy",
    "SearchFieldMode",
    "SortDirection",
]
