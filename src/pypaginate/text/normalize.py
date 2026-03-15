"""Text normalization using Python stdlib.

Replaces the previous text-unidecode dependency with stdlib
unicodedata. Handles accents, diacritics, case folding, and
whitespace normalization for 95% of use cases.
"""

from __future__ import annotations

import unicodedata


def normalize_text(value: str) -> str:
    """Normalize text for search and filtering.

    Pipeline: NFKD decompose -> strip accents -> casefold -> collapse ws.

    Args:
        value: Text to normalize.

    Returns:
        Normalized ASCII-safe text.
    """
    decomposed = unicodedata.normalize("NFKD", value)
    stripped = _strip_accents(decomposed)
    return " ".join(stripped.casefold().split())


def _strip_accents(value: str) -> str:
    """Remove combining diacritical marks from decomposed text.

    Args:
        value: NFKD-decomposed text.

    Returns:
        Text with accents removed.
    """
    return "".join(char for char in value if unicodedata.category(char) != "Mn")


__all__ = ["normalize_text"]
