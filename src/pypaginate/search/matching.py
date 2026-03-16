"""Matching utilities for search operations.

All functions expect pre-normalized strings. Callers must
normalize via ``normalize_text()`` before calling.

Provides exact, prefix, and contains matching plus optional
fuzzy matching via rapidfuzz (graceful fallback if unavailable).
"""

from __future__ import annotations

from typing import Any

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode


_fuzz: Any = None

try:
    from rapidfuzz import fuzz as _fuzz

    _HAS_RAPIDFUZZ = True
except ImportError:  # pragma: no cover
    _HAS_RAPIDFUZZ = False  # pragma: no cover


def matches_field(
    norm_value: str,
    norm_token: str,
    mode: SearchFieldMode,
) -> bool:
    """Check if a normalized value matches a normalized token."""
    if mode is SearchFieldMode.EXACT:
        return norm_value == norm_token
    if mode is SearchFieldMode.PREFIX:
        return norm_value.startswith(norm_token)
    return norm_token in norm_value


def fuzzy_score(
    norm_value: str,
    norm_token: str,
    threshold: int,
    fuzzy_mode: FuzzyMode = FuzzyMode.FUZZY,
) -> int:
    """Compute fuzzy match score on pre-normalized strings.

    Args:
        norm_value: Pre-normalized field value.
        norm_token: Pre-normalized search token.
        threshold: Minimum score (0-100) to consider a match.
        fuzzy_mode: Algorithm to use (FUZZY or TOKEN_SORT).

    Returns:
        Score from 0 to 100 (0 means no match above threshold).
    """
    if fuzzy_mode is FuzzyMode.TOKEN_SORT:
        score = _compute_token_sort(norm_value, norm_token)
    else:
        score = _compute_partial(norm_value, norm_token)
    return score if score >= threshold else 0


def _compute_partial(norm_value: str, norm_token: str) -> int:
    """Fuzzy score via partial_ratio (substring matching)."""
    if _HAS_RAPIDFUZZ and _fuzz is not None:
        return int(_fuzz.partial_ratio(norm_token, norm_value))
    return 100 if norm_token in norm_value else 0


def _compute_token_sort(norm_value: str, norm_token: str) -> int:
    """Fuzzy score via token_sort_ratio (word-order agnostic)."""
    if _HAS_RAPIDFUZZ and _fuzz is not None:
        return int(_fuzz.token_sort_ratio(norm_token, norm_value))
    return 100 if norm_token in norm_value else 0


__all__ = ["fuzzy_score", "matches_field"]
