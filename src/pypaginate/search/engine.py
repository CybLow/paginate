"""In-memory search engine applying SearchSpec to sequences.

Tokenizes the query, scores each item against all search fields,
and returns items sorted by relevance (best matches first).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode
from pypaginate.domain.specs import SearchSpec
from pypaginate.filtering.accessor import get_value
from pypaginate.search.matching import fuzzy_score, matches_field
from pypaginate.search.parser import TokenParser


T = TypeVar("T")


class SearchEngine:
    """Stateless engine that searches sequences by SearchSpec.

    Tokenizes the query, matches tokens against specified fields,
    and returns results sorted by relevance score.
    """

    def __init__(self) -> None:
        self._parser = TokenParser()

    def apply(self, items: Sequence[T], spec: SearchSpec) -> list[T]:
        """Filter and rank items by search relevance.

        Args:
            items: Input sequence to search.
            spec: Search specification with query, fields, mode.

        Returns:
            Items matching the query, sorted by relevance.

        Raises:
            SearchError: If the search operation fails.
        """
        tokens = self._parser.parse(spec.query)
        if not tokens:
            return list(items)
        return self._rank_items(items, tokens, spec)

    @staticmethod
    def _rank_items(
        items: Sequence[T],
        tokens: list[str],
        spec: SearchSpec,
    ) -> list[T]:
        """Score and rank items by search relevance.

        Args:
            items: Source items to search.
            tokens: Parsed search tokens.
            spec: Search specification.

        Returns:
            Matched items sorted by descending relevance.
        """
        scored = []
        for item in items:
            score = _score_item(item, tokens, spec)
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored]


def _score_item(item: object, tokens: list[str], spec: SearchSpec) -> int:
    """Compute total relevance score for an item across all tokens.

    Args:
        item: Item to score.
        tokens: Search tokens to match.
        spec: Search specification.

    Returns:
        Sum of per-token best scores (0 if no match).
    """
    total = 0
    for token in tokens:
        best = _best_field_score(item, token, spec)
        if best == 0:
            return 0
        total += best
    return total


def _best_field_score(
    item: object,
    token: str,
    spec: SearchSpec,
) -> int:
    """Find the best match score for a token across all fields.

    Args:
        item: Item to search.
        token: Single search token.
        spec: Search specification.

    Returns:
        Best score across all fields (0 if no match).
    """
    best = 0
    for field in spec.fields:
        score = _field_score(item, field, token, spec)
        best = max(best, score)
    return best


def _field_score(
    item: object,
    field: str,
    token: str,
    spec: SearchSpec,
) -> int:
    """Score a single field against a token.

    Args:
        item: Item to extract field from.
        field: Dotted field path.
        token: Search token.
        spec: Search specification.

    Returns:
        Match score (0-100), or 0 if field is missing/non-string.
    """
    try:
        value = get_value(item, field)
    except Exception:
        return 0
    if not isinstance(value, str):
        return 0
    return _evaluate_match(value, token, spec.mode, spec.fuzzy, spec.threshold)


def _evaluate_match(
    value: str,
    token: str,
    mode: SearchFieldMode,
    fuzzy: FuzzyMode,
    threshold: int,
) -> int:
    """Evaluate a match between a string value and a token.

    Args:
        value: Field string value.
        token: Search token.
        mode: Match mode (EXACT, PREFIX, CONTAINS).
        fuzzy: Fuzzy mode (EXACT or FUZZY).
        threshold: Fuzzy match threshold.

    Returns:
        Score from 0 to 100.
    """
    if fuzzy is FuzzyMode.FUZZY:
        return fuzzy_score(value, token, threshold)
    return 100 if matches_field(value, token, mode) else 0


__all__ = ["SearchEngine"]
