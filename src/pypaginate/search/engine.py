"""In-memory search engine applying SearchSpec to sequences.

Pre-normalizes tokens and compiles field accessors ONCE.
Single-field fast path avoids list allocation per item.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode
from pypaginate.domain.exceptions import PaginationError
from pypaginate.domain.specs import SearchSpec
from pypaginate.filtering.accessor import compile_accessor
from pypaginate.search.matching import fuzzy_score, matches_field
from pypaginate.search.parser import TokenParser
from pypaginate.text.normalize import normalize_text


T = TypeVar("T")


class SearchEngine:
    """Stateless engine that searches sequences by SearchSpec."""

    __slots__ = ("_parser",)

    def __init__(self) -> None:
        self._parser = TokenParser()

    def apply(self, items: Sequence[T], spec: SearchSpec) -> list[T]:
        """Filter and rank items by search relevance.

        Args:
            items: Input sequence to search.
            spec: Search specification with query, fields, mode.

        Returns:
            Items matching the query, sorted by relevance.
        """
        tokens = self._parser.parse(spec.query)
        if not tokens:
            return list(items)
        norm_tokens = [normalize_text(t) for t in tokens]
        accessors = [compile_accessor(f) for f in spec.fields]
        is_fuzzy = spec.fuzzy is FuzzyMode.FUZZY
        mode = spec.mode
        threshold = spec.threshold

        if len(accessors) == 1:
            return _rank_single(items, norm_tokens, accessors[0], is_fuzzy, mode, threshold)
        return _rank_multi(items, norm_tokens, accessors, is_fuzzy, mode, threshold)


def _rank_single(
    items: Sequence[T],
    norm_tokens: list[str],
    accessor: Callable[[object], object],
    is_fuzzy: bool,
    mode: SearchFieldMode,
    threshold: int,
) -> list[T]:
    """Fast path: single field, no list alloc per item."""
    scored = []
    for item in items:
        s = _score_single(item, norm_tokens, accessor, is_fuzzy, mode, threshold)
        if s > 0:
            scored.append((s, item))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [item for _, item in scored]


def _score_single(
    item: object,
    norm_tokens: list[str],
    accessor: Callable[[object], object],
    is_fuzzy: bool,
    mode: SearchFieldMode,
    threshold: int,
) -> int:
    """Score single field: no list, no _extract, no _best."""
    try:
        value = accessor(item)
    except PaginationError:
        return 0
    if not isinstance(value, str):
        return 0
    nv = normalize_text(value)
    total = 0
    for nt in norm_tokens:
        if is_fuzzy:
            s = fuzzy_score(nv, nt, threshold)
            if s == 0:
                return 0
            total += s
        elif matches_field(nv, nt, mode):
            total += 100
        else:
            return 0
    return total


def _rank_multi(
    items: Sequence[T],
    norm_tokens: list[str],
    accessors: list[Callable[[object], object]],
    is_fuzzy: bool,
    mode: SearchFieldMode,
    threshold: int,
) -> list[T]:
    """Multi-field: extract+normalize once, match all tokens."""
    scored = []
    for item in items:
        s = _score_multi(item, norm_tokens, accessors, is_fuzzy, mode, threshold)
        if s > 0:
            scored.append((s, item))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [item for _, item in scored]


def _score_multi(
    item: object,
    norm_tokens: list[str],
    accessors: list[Callable[[object], object]],
    is_fuzzy: bool,
    mode: SearchFieldMode,
    threshold: int,
) -> int:
    """Score across multiple fields."""
    norm_values = _extract(item, accessors)
    if not norm_values:
        return 0
    total = 0
    for nt in norm_tokens:
        best = _best(norm_values, nt, is_fuzzy, mode, threshold)
        if best == 0:
            return 0
        total += best
    return total


def _extract(
    item: object,
    accessors: list[Callable[[object], object]],
) -> list[str]:
    """Extract and normalize field values ONCE per item."""
    result: list[str] = []
    for accessor in accessors:
        try:
            value = accessor(item)
        except PaginationError:
            continue
        if isinstance(value, str):
            result.append(normalize_text(value))
    return result


def _best(
    norm_values: list[str],
    norm_token: str,
    is_fuzzy: bool,
    mode: SearchFieldMode,
    threshold: int,
) -> int:
    """Best score across pre-normalized values."""
    best = 0
    if is_fuzzy:
        for nv in norm_values:
            best = max(best, fuzzy_score(nv, norm_token, threshold))
    else:
        for nv in norm_values:
            if matches_field(nv, norm_token, mode):
                return 100
    return best


__all__ = ["SearchEngine"]
