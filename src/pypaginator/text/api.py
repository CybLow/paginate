"""Public text normalization API.

This module aggregates UTF-8 primitives, reusable normalization pipelines,
and pattern utilities into a single import surface for consumers.
"""

from __future__ import annotations

from .patterns import (
    FilterTextNormalizer,
    build_like_regex,
    compile_regex,
    normalise_regex_argument,
    sql_like_to_regex,
)
from .pipelines import (
    MemoryTextNormalizer,
    SqlTextNormalizer,
    TextPipeline,
    Utf8TextPipeline,
)
from .utf8 import (
    UNIDECODE,
    NormalizationForm,
    Utf8Normalizer,
    create_search_normalizer,
    normalize_utf8,
    transliterate_ascii,
)

__all__ = [
    # UTF-8 primitives
    "Utf8Normalizer",
    "normalize_utf8",
    "transliterate_ascii",
    "create_search_normalizer",
    "UNIDECODE",
    "NormalizationForm",
    # Pipelines
    "TextPipeline",
    "Utf8TextPipeline",
    "SqlTextNormalizer",
    "MemoryTextNormalizer",
    # Pattern utilities
    "FilterTextNormalizer",
    "sql_like_to_regex",
    "build_like_regex",
    "compile_regex",
    "normalise_regex_argument",
]

