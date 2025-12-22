"""Fuzzy matching helpers shared by the in-memory search engine."""

from __future__ import annotations

from math import isfinite

from rapidfuzz import fuzz as rapidfuzz_fuzz
from rapidfuzz.distance import Levenshtein as RapidfuzzLevenshtein


def fuzzy_match(token: str, text: str, threshold: int) -> bool:
    """Return True when text matches token within fuzzy bounds.

    Args:
        token: Search token to match.
        text: Text to search in.
        threshold: RapidFuzz threshold percentage (0-100).

    Returns:
        True if fuzzy match succeeds.
    """

    if partial_ratio(token, text) >= threshold:
        return True
    return is_near_match(token, text)


def partial_ratio(token: str, text: str) -> int:
    """Compute the RapidFuzz partial ratio or raise if unavailable.

    Args:
        token: Search token.
        text: Text to compare.

    Returns:
        Partial ratio score (0-100).
    """

    return int(rapidfuzz_fuzz.partial_ratio(token, text))


def is_near_match(token: str, text: str) -> bool:
    """Return True when token and text are within one mutation.

    Args:
        token: Search token.
        text: Text to compare.

    Returns:
        True if Levenshtein distance <= 1.
    """

    distance = RapidfuzzLevenshtein.distance(token, text, score_cutoff=1)
    if isinstance(distance, int | float) and isfinite(distance):
        return distance <= 1
    return False


def text_match(token: str, text: str, prefix: bool) -> bool:
    """Return True when text satisfies the prefix/contains policy.

    Args:
        token: Search token.
        text: Text to search in.
        prefix: Whether to use prefix matching (vs contains).

    Returns:
        True if match succeeds.
    """

    return text.startswith(token) if prefix else token in text


__all__ = ["fuzzy_match", "partial_ratio", "is_near_match", "text_match"]
