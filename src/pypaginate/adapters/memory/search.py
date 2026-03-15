"""In-memory search backend delegating to text normalization.

Implements SearchBackend protocol for Python sequences.
Supports exact and contains matching with optional fuzzy comparison.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode
from pypaginate.filtering.accessor import get_value
from pypaginate.text.normalize import normalize_text


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import SearchSpec


class MemorySearchBackend:
    """Search backend for in-memory sequences.

    Satisfies ``SearchBackend`` protocol by matching search terms
    against item fields using text normalization.
    """

    def apply_search(
        self,
        query: object,
        spec: SearchSpec,
    ) -> object:
        """Apply a search spec to a sequence.

        Args:
            query: A Python sequence of items.
            spec: Search specification with query and fields.

        Returns:
            Filtered list of items matching the search.
        """
        items: Sequence[object] = query  # type: ignore[assignment]
        normalized_query = normalize_text(spec.query)
        if not normalized_query:
            return list(items)
        return [item for item in items if _matches(item, spec, normalized_query)]


def _matches(item: object, spec: SearchSpec, normalized_query: str) -> bool:
    """Check if any field on an item matches the search query.

    Args:
        item: The item to check.
        spec: Search specification.
        normalized_query: Pre-normalized query string.

    Returns:
        True if any field matches.
    """
    return any(_field_matches(item, field, spec, normalized_query) for field in spec.fields)


def _field_matches(
    item: object,
    field: str,
    spec: SearchSpec,
    normalized_query: str,
) -> bool:
    """Check if a single field matches the search query."""
    raw_value = get_value(item, field)
    if raw_value is None:
        return False
    normalized_value = normalize_text(str(raw_value))
    if spec.fuzzy is FuzzyMode.FUZZY:
        return _fuzzy_match(normalized_value, normalized_query, spec.threshold)
    return _exact_match(normalized_value, normalized_query, spec.mode)


def _exact_match(value: str, query: str, mode: SearchFieldMode) -> bool:
    """Match using exact string comparison."""
    if mode is SearchFieldMode.EXACT:
        return value == query
    if mode is SearchFieldMode.PREFIX:
        return value.startswith(query)
    return query in value


def _fuzzy_match(value: str, query: str, threshold: int) -> bool:
    """Match using simple substring ratio as fuzzy fallback."""
    if query in value:
        return True
    return _similarity(value, query) >= threshold


def _similarity(value: str, query: str) -> int:
    """Compute a simple similarity score (0-100)."""
    if not value or not query:
        return 0
    shorter, longer = sorted([value, query], key=len)
    if shorter in longer:
        return 100
    matches = sum(c in longer for c in shorter)
    return int(matches / len(shorter) * 100)


__all__ = ["MemorySearchBackend"]
