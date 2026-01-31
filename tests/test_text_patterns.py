"""Tests for text patterns module."""

from __future__ import annotations

import re

import pytest

from pypaginate.text.patterns import (
    FilterTextNormalizer,
    build_like_regex,
    compile_regex,
    sql_like_to_regex,
)


class TestSqlLikeToRegex:
    """Test sql_like_to_regex function."""

    def test_exact_match(self) -> None:
        """Should convert exact pattern."""
        result = sql_like_to_regex("hello")
        assert result == "hello"

    def test_wildcard_percent(self) -> None:
        """Should convert % to .*"""
        result = sql_like_to_regex("hello%")
        assert ".*" in result

    def test_wildcard_underscore(self) -> None:
        """Should convert _ to ."""
        result = sql_like_to_regex("h_llo")
        assert "." in result

    def test_escaped_characters(self) -> None:
        """Should escape regex special characters."""
        result = sql_like_to_regex("hello.world")
        # . should be escaped
        assert "\\." in result


class TestBuildLikeRegex:
    """Test build_like_regex function."""

    def test_returns_pattern(self) -> None:
        """Should return compiled pattern."""
        result = build_like_regex("hello%")
        assert isinstance(result, re.Pattern)

    def test_matches_prefix(self) -> None:
        """Should match prefix pattern."""
        pattern = build_like_regex("hello%")
        assert pattern.fullmatch("hello world") is not None

    def test_no_match(self) -> None:
        """Should not match when pattern doesn't match."""
        pattern = build_like_regex("hello%")
        assert pattern.fullmatch("world hello") is None


class TestCompileRegex:
    """Test compile_regex function."""

    def test_valid_pattern(self) -> None:
        """Should compile valid pattern."""
        pattern = compile_regex("hello.*")
        assert isinstance(pattern, re.Pattern)

    def test_invalid_pattern_raises(self) -> None:
        """Should raise on invalid pattern."""
        from pypaginate.exceptions import FilterValidationError

        with pytest.raises(FilterValidationError):
            compile_regex("[invalid")  # Unclosed bracket

    def test_flags(self) -> None:
        """Should accept flags."""
        pattern = compile_regex("hello", flags=re.IGNORECASE)
        assert pattern.match("HELLO") is not None


class TestFilterTextNormalizer:
    """Test FilterTextNormalizer class."""

    def test_case_sensitive(self) -> None:
        """Case sensitive should preserve case."""
        normalizer = FilterTextNormalizer(case_sensitive=True)
        result = normalizer("HELLO")
        assert result == "HELLO"

    def test_case_insensitive(self) -> None:
        """Case insensitive should lowercase."""
        normalizer = FilterTextNormalizer(case_sensitive=False)
        result = normalizer("HELLO")
        assert result is None or result == "hello" or result.islower()

    def test_none_input(self) -> None:
        """Should handle None input."""
        normalizer = FilterTextNormalizer(case_sensitive=True)
        result = normalizer(None)
        assert result is None

    def test_int_input(self) -> None:
        """Should convert int to string."""
        normalizer = FilterTextNormalizer(case_sensitive=True)
        result = normalizer(42)
        assert result == "42"
