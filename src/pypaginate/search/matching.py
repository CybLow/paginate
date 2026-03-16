"""Matching utilities for search operations.

All functions expect pre-normalized strings. Callers must
normalize via ``normalize_text()`` before calling.

Provides exact, prefix, and contains matching plus optional
fuzzy matching via rapidfuzz (graceful fallback if unavailable).
"""

from __future__ import annotations

from typing import Any

from pypaginate.domain.enums import SearchFieldMode


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
    """Check if a normalized value matches a normalized token.

    Args:
        norm_value: Pre-normalized field value.
        norm_token: Pre-normalized search token.
        mode: Matching strategy (EXACT, PREFIX, CONTAINS).

    Returns:
        True if the match succeeds.
    """
    if mode is SearchFieldMode.EXACT:
        return norm_value == norm_token
    if mode is SearchFieldMode.PREFIX:
        return norm_value.startswith(norm_token)
    return norm_token in norm_value


def fuzzy_score(
    norm_value: str,
    norm_token: str,
    threshold: int,
) -> int:
    """Compute fuzzy match score on pre-normalized strings.

    Uses rapidfuzz if available; falls back to simple containment
    check returning 100 (match) or 0 (no match).

    Args:
        norm_value: Pre-normalized field value.
        norm_token: Pre-normalized search token.
        threshold: Minimum score (0-100) to consider a match.

    Returns:
        Score from 0 to 100 (0 means no match above threshold).
    """
    score = _compute_score(norm_value, norm_token)
    return score if score >= threshold else 0


def _compute_score(norm_value: str, norm_token: str) -> int:
    """Compute fuzzy similarity score."""
    if _HAS_RAPIDFUZZ and _fuzz is not None:
        return int(_fuzz.partial_ratio(norm_token, norm_value))
    return 100 if norm_token in norm_value else 0


__all__ = ["fuzzy_score", "matches_field"]
