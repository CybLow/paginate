"""UTF-8 normalization and ASCII transliteration primitives."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal


if TYPE_CHECKING:
    from collections.abc import Callable


NormalizationForm = Literal["NFC", "NFD", "NFKC", "NFKD"]
"""Literal type for Unicode normalization forms."""


def _get_unidecode() -> Callable[[str], str]:
    """Lazily import unidecode function from text_unidecode library.

    Returns:
        The unidecode function.

    Raises:
        ImportError: If text_unidecode is not installed.
    """
    try:
        from text_unidecode import unidecode
    except ImportError as e:
        raise ImportError(
            "text_unidecode is required for text normalization. "
            "Install with: pip install pypaginator[text]"
        ) from e
    return unidecode  # type: ignore[no-any-return]


def normalize_utf8(
    value: str,
    *,
    lowercase: bool,
    casefold_output: bool,
    form: NormalizationForm,
) -> str:
    """Normalize a UTF-8 string with specified casing and form.

    Args:
        value: Input text to normalize.
        lowercase: Whether to lowercase the result (ignored if casefold_output).
        casefold_output: Whether to apply casefolding for aggressive matching.
        form: Unicode normalization form (e.g. "NFKC").

    Returns:
        The normalized string.
    """
    normalised = unicodedata.normalize(form, value)
    if casefold_output:
        return normalised.casefold()
    return normalised.lower() if lowercase else normalised


def transliterate_ascii(value: str) -> str:
    """Return ASCII transliteration using text-unidecode.

    Args:
        value: Input unicode text.

    Returns:
        ASCII-only transliteration of value.
    """
    return _get_unidecode()(value)


@dataclass(frozen=True)
class Utf8Normalizer:
    """UTF-8 text normalizer with configurable casing and normalization form."""

    lowercase: bool = False
    casefold_output: bool = False
    form: NormalizationForm = "NFC"

    def normalise(self, value: str) -> str:
        """Normalize the given UTF-8 string.

        Args:
            value: Input text to normalize.

        Returns:
            The normalized string according to the instance configuration.
        """
        return normalize_utf8(
            value,
            lowercase=self.lowercase,
            casefold_output=self.casefold_output,
            form=self.form,
        )


def create_search_normalizer() -> Utf8Normalizer:
    """Return the canonical search normalizer (lowercase + NFKC).

    Returns:
        A configured Utf8Normalizer instance.
    """
    return Utf8Normalizer(lowercase=True, casefold_output=False, form="NFKC")


__all__ = [
    "NormalizationForm",
    "Utf8Normalizer",
    "create_search_normalizer",
    "normalize_utf8",
    "transliterate_ascii",
]
