"""Tests for text pipelines module."""

from __future__ import annotations

import pytest

from pypaginator.text.pipelines import (
    MemoryTextNormalizer,
    SqlTextNormalizer,
    Utf8TextPipeline,
)


class TestUtf8TextPipeline:
    """Test Utf8TextPipeline class."""

    def test_creation(self) -> None:
        """Should create pipeline."""
        pipeline = Utf8TextPipeline()
        assert pipeline is not None

    def test_call_basic(self) -> None:
        """Should normalize basic text."""
        pipeline = Utf8TextPipeline()
        result = pipeline("Hello World")
        assert result is not None
        assert isinstance(result, str)

    def test_lowercase(self) -> None:
        """Should lowercase text."""
        pipeline = Utf8TextPipeline()
        result = pipeline("HELLO")
        assert result == "hello"

    def test_collapse_whitespace(self) -> None:
        """Should collapse whitespace by default."""
        pipeline = Utf8TextPipeline(collapse_whitespace=True)
        result = pipeline("hello  world")
        assert "  " not in result

    def test_preserve_whitespace(self) -> None:
        """Should preserve whitespace when disabled."""
        pipeline = Utf8TextPipeline(collapse_whitespace=False)
        result = pipeline("hello  world")
        # Whitespace should be preserved
        assert result is not None


class TestSqlTextNormalizer:
    """Test SqlTextNormalizer class."""

    def test_creation(self) -> None:
        """Should create normalizer."""
        normalizer = SqlTextNormalizer()
        assert normalizer is not None

    def test_normalize_text(self) -> None:
        """Should normalize text."""
        normalizer = SqlTextNormalizer()
        result = normalizer.normalize_text("HELLO")
        assert result == "hello"

    def test_normalize_text_whitespace(self) -> None:
        """Should handle whitespace."""
        normalizer = SqlTextNormalizer()
        result = normalizer.normalize_text("hello  world")
        assert "  " not in result


class TestMemoryTextNormalizerPipeline:
    """Test MemoryTextNormalizer with pipeline."""

    def test_creation(self) -> None:
        """Should create normalizer."""
        normalizer = MemoryTextNormalizer()
        assert normalizer is not None

    def test_normalize_text(self) -> None:
        """Should normalize text."""
        normalizer = MemoryTextNormalizer()
        result = normalizer.normalize_text("HELLO")
        assert result == "hello"

    def test_normalize_unicode(self) -> None:
        """Should handle unicode."""
        normalizer = MemoryTextNormalizer()
        result = normalizer.normalize_text("café")
        assert result is not None
        assert isinstance(result, str)

    def test_normalize_empty(self) -> None:
        """Should handle empty string."""
        normalizer = MemoryTextNormalizer()
        result = normalizer.normalize_text("")
        assert result == ""

    def test_custom_pipeline(self) -> None:
        """Should accept custom pipeline."""
        custom_pipeline = Utf8TextPipeline()
        normalizer = MemoryTextNormalizer(pipeline=custom_pipeline)
        result = normalizer.normalize_text("TEST")
        assert result == "test"
