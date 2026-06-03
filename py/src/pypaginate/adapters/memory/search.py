"""In-memory search backend.

Implements the ``SearchBackend`` protocol for Python sequences. Non-fuzzy
match-filtering (exact / prefix / contains) delegates to the native ``_core``
engine (so it normalizes identically to the ranked ``SearchEngine`` and the
resident ``Dataset``); ``FuzzyMode.FUZZY`` uses a small adapter-level
similarity match (substring fast path + character-overlap score).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypaginate import _native
from pypaginate.domain.enums import FuzzyMode
from pypaginate.filtering.accessor import compile_accessor
from pypaginate.text.normalize import normalize_text


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from pypaginate.domain.specs import SearchSpec


class MemorySearchBackend:
    """Search backend for in-memory sequences."""

    __slots__ = ()

    @staticmethod
    def apply_search(
        query: object,
        spec: SearchSpec,
    ) -> object:
        """Apply a search spec to a sequence.

        Args:
            query: A Python sequence of items.
            spec: Search specification with query and fields.

        Returns:
            Filtered list of items matching the search (original order).
        """
        items: Sequence[object] = query  # type: ignore[assignment]
        if spec.fuzzy is FuzzyMode.FUZZY:
            return _fuzzy_filter(items, spec)
        return _native.match_filter(items, spec.query, spec.fields, spec.mode)


def _fuzzy_filter(items: Sequence[object], spec: SearchSpec) -> list[object]:
    """Adapter-level fuzzy match-filter (substring + char-overlap similarity)."""
    norm_query = normalize_text(spec.query)
    if not norm_query:
        return list(items)
    accessors = [compile_accessor(f) for f in spec.fields]
    return [item for item in items if _fuzzy_any(item, accessors, norm_query, spec.threshold)]


def _fuzzy_any(
    item: object,
    accessors: list[Callable[[object], object]],
    norm_query: str,
    threshold: int,
) -> bool:
    """True if any field's normalized value fuzzy-matches the query."""
    for accessor in accessors:
        value = accessor(item)
        if value is None:
            continue
        normalized = normalize_text(value if isinstance(value, str) else str(value))
        if _fuzzy_match(normalized, norm_query, threshold):
            return True
    return False


def _fuzzy_match(value: str, query: str, threshold: int) -> bool:
    """Fuzzy match with substring fast path."""
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
