"""Matching utilities for search operations.

Provides exact, prefix, and contains matching plus optional
fuzzy matching via rapidfuzz (graceful fallback if unavailable).
"""

from __future__ import annotations

import types

from pypaginate.domain.enums import SearchFieldMode
from pypaginate.text.normalize import normalize_text


_fuzz: types.ModuleType | None

try:
    from rapidfuzz import fuzz as _fuzz

    _HAS_RAPIDFUZZ = True
except ImportError:  # pragma: no cover
    _fuzz = None  # pragma: no cover
    _HAS_RAPIDFUZZ = False  # pragma: no cover


def matches_field(value: str, token: str, mode: SearchFieldMode) -> bool:
    """Check if a field value matches a token using the given mode.

    Both value and token are normalized before comparison.

    Args:
        value: The field value to check.
        token: The search token to match against.
        mode: Matching strategy (EXACT, PREFIX, CONTAINS).

    Returns:
        True if the value matches the token.
    """
    norm_value = normalize_text(value)
    norm_token = normalize_text(token)
    return _match_normalized(norm_value, norm_token, mode)


def fuzzy_score(value: str, token: str, threshold: int) -> int:
    """Compute a fuzzy match score between value and token.

    Uses rapidfuzz if available; falls back to simple containment
    check returning 100 (match) or 0 (no match).

    Args:
        value: The field value to score.
        token: The search token to score against.
        threshold: Minimum score (0-100) to consider a match.

    Returns:
        Score from 0 to 100 (0 means no match above threshold).
    """
    norm_value = normalize_text(value)
    norm_token = normalize_text(token)
    score = _compute_score(norm_value, norm_token)
    return score if score >= threshold else 0


def _match_normalized(
    norm_value: str,
    norm_token: str,
    mode: SearchFieldMode,
) -> bool:
    """Perform matching on already-normalized strings.

    Args:
        norm_value: Normalized field value.
        norm_token: Normalized search token.
        mode: Matching strategy.

    Returns:
        True if the match succeeds.
    """
    if mode is SearchFieldMode.EXACT:
        return norm_value == norm_token
    if mode is SearchFieldMode.PREFIX:
        return norm_value.startswith(norm_token)
    return norm_token in norm_value


def _compute_score(norm_value: str, norm_token: str) -> int:
    """Compute fuzzy similarity score.

    Args:
        norm_value: Normalized field value.
        norm_token: Normalized search token.

    Returns:
        Integer score from 0 to 100.
    """
    if _HAS_RAPIDFUZZ and _fuzz is not None:
        return int(_fuzz.partial_ratio(norm_token, norm_value))
    return 100 if norm_token in norm_value else 0


__all__ = ["fuzzy_score", "matches_field"]
