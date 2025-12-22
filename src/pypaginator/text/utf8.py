"""UTF-8 normalization and ASCII transliteration primitives."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from importlib import import_module
from typing import Callable, Final, Literal, cast

_UNIDECODE_MODULE = import_module("text_unidecode")
UNIDECODE: Final[Callable[[str], str]] = cast(
    "Callable[[str], str]", getattr(_UNIDECODE_MODULE, "unidecode")
)
"""Concrete reference to the unidecode function from text_unidecode library."""

NormalizationForm = Literal["NFC", "NFD", "NFKC", "NFKD"]
"""Literal type for Unicode normalization forms."""


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
    return UNIDECODE(value)


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
    "Utf8Normalizer",
    "normalize_utf8",
    "transliterate_ascii",
    "create_search_normalizer",
    "UNIDECODE",
    "NormalizationForm",
]
