"""In-memory search backend delegating to text normalization.

Implements SearchBackend protocol for Python sequences.
Pre-normalizes the query and compiles field accessors ONCE.
Compiles a single match function to minimize per-item overhead.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode
from pypaginate.filtering.accessor import compile_accessor
from pypaginate.text.normalize import normalize_text


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import SearchSpec

Matcher = Callable[[object], bool]


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
            Filtered list of items matching the search.
        """
        items: Sequence[object] = query  # type: ignore[assignment]
        normalized_query = normalize_text(spec.query)
        if not normalized_query:
            return list(items)
        matcher = _compile_matcher(spec, normalized_query)
        return [item for item in items if matcher(item)]


def _compile_matcher(spec: SearchSpec, norm_query: str) -> Matcher:
    """Compile a search spec into a single match callable."""
    accessors = [compile_accessor(f) for f in spec.fields]
    is_fuzzy = spec.fuzzy is FuzzyMode.FUZZY
    threshold = spec.threshold
    mode = spec.mode

    if is_fuzzy:
        return _compile_fuzzy(accessors, norm_query, threshold)

    if len(accessors) == 1:
        return _compile_exact_single(accessors[0], norm_query, mode)

    return _compile_exact_multi(accessors, norm_query, mode)


def _compile_exact_single(
    accessor: Callable[[object], object],
    norm_query: str,
    mode: SearchFieldMode,
) -> Matcher:
    """Fast path: single field, exact matching."""
    if mode is SearchFieldMode.CONTAINS:

        def _match(item: object) -> bool:
            v = accessor(item)
            if v is None:
                return False
            return norm_query in normalize_text(v if isinstance(v, str) else str(v))

        return _match

    if mode is SearchFieldMode.PREFIX:

        def _match_prefix(item: object) -> bool:
            v = accessor(item)
            if v is None:
                return False
            return normalize_text(v if isinstance(v, str) else str(v)).startswith(norm_query)

        return _match_prefix

    def _match_exact(item: object) -> bool:
        v = accessor(item)
        if v is None:
            return False
        return normalize_text(v if isinstance(v, str) else str(v)) == norm_query

    return _match_exact


def _compile_exact_multi(
    accessors: list[Callable[[object], object]],
    norm_query: str,
    mode: SearchFieldMode,
) -> Matcher:
    """Multi-field exact matching (no genexpr)."""

    def _match(item: object) -> bool:
        for accessor in accessors:
            v = accessor(item)
            if v is None:
                continue
            nv = normalize_text(v if isinstance(v, str) else str(v))
            if _exact_matches(nv, norm_query, mode):
                return True
        return False

    return _match


def _compile_fuzzy(
    accessors: list[Callable[[object], object]],
    norm_query: str,
    threshold: int,
) -> Matcher:
    """Fuzzy matching across fields."""

    def _match(item: object) -> bool:
        for accessor in accessors:
            v = accessor(item)
            if v is None:
                continue
            nv = normalize_text(v if isinstance(v, str) else str(v))
            if _fuzzy_match(nv, norm_query, threshold):
                return True
        return False

    return _match


def _exact_matches(value: str, query: str, mode: SearchFieldMode) -> bool:
    """Inline exact match dispatch."""
    if mode is SearchFieldMode.CONTAINS:
        return query in value
    if mode is SearchFieldMode.PREFIX:
        return value.startswith(query)
    return value == query


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
