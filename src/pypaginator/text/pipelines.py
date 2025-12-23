"""Reusable text normalization pipelines for search and filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from sqlalchemy.sql import func

from pypaginator.exceptions import SearchNormalizationError

from .utf8 import Utf8Normalizer, create_search_normalizer, transliterate_ascii


if TYPE_CHECKING:
    from collections.abc import Callable

    from ..types import SqlStringExpression


class TextPipeline(Protocol):
    """Protocol for callable text normalization pipelines.

    A text pipeline is any callable that accepts a string and returns
    a normalized string.
    """

    def __call__(self, value: str) -> str:
        """Normalize text input.

        Args:
            value: Text to normalize.

        Returns:
            Normalized text string.
        """
        ...


@dataclass(frozen=True, slots=True)
class Utf8TextPipeline:
    """Compose UTF-8 normalization, ASCII transliteration and whitespace folding.

    This pipeline is used by both memory and SQL search normalizers to provide
    consistent text processing across different storage backends.
    """

    collapse_whitespace: bool = True
    normalizer_factory: Callable[[], Utf8Normalizer] = field(
        default=create_search_normalizer, repr=False
    )
    _normalizer: Utf8Normalizer = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the frozen normalizer field.

        Uses object.__setattr__ to bypass frozen dataclass restrictions during
        initialization. This is a necessary compatibility shim for lazy field
        initialization in frozen dataclasses.
        """
        object.__setattr__(self, "_normalizer", self.normalizer_factory())

    def __call__(self, value: str) -> str:
        """Apply full normalization pipeline to input text.

        Args:
            value: Text to normalize.

        Returns:
            Normalized text string.
        """
        normalised = self._normalizer.normalise(value)
        transliterated = transliterate_ascii(normalised)
        if self.collapse_whitespace:
            return " ".join(transliterated.split())
        return transliterated


@dataclass(frozen=True, slots=True)
class SqlTextNormalizer:
    """Normalizer for SQL column expressions and text inputs.

    Provides consistent text normalization for SQL LIKE queries and
    column comparisons.
    """

    pipeline: TextPipeline = field(default_factory=Utf8TextPipeline, repr=False)

    def normalize_text(self, value: str) -> str:
        """Normalize text input for SQL comparison.

        Args:
            value: Text to normalize.

        Returns:
            Normalized text string.
        """
        return self.pipeline(value)

    @staticmethod
    def normalize_column(column: SqlStringExpression) -> SqlStringExpression:
        """Apply SQL LOWER function to column expression.

        Args:
            column: Column expression to normalize.

        Returns:
            Normalized column expression.

        Raises:
            SearchNormalizationError: If database doesn't support LOWER.
        """
        try:
            return func.lower(column)
        except AttributeError as error:  # pragma: no cover
            raise SearchNormalizationError(
                "Database engine does not support LOWER",
            ) from error


@dataclass(frozen=True, slots=True)
class MemoryTextNormalizer:
    """Normalizer for in-memory text search operations.

    Used for prefix matching and substring search in memory collections.
    """

    pipeline: TextPipeline = field(default_factory=Utf8TextPipeline, repr=False)

    def normalize_text(self, value: str) -> str:
        """Normalize text for in-memory comparison.

        Args:
            value: Text to normalize.

        Returns:
            Normalized text string.
        """
        return self.pipeline(value)


__all__ = [
    "MemoryTextNormalizer",
    "SqlTextNormalizer",
    "TextPipeline",
    "Utf8TextPipeline",
]
