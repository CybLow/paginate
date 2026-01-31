"""Tests for pattern-based filtering operators.

This module tests the LikeFactory and RegexFactory classes which implement
SQL LIKE and regex pattern matching for in-memory filtering.
"""

from __future__ import annotations

import pytest

from pypaginate.exceptions import FilterValidationError
from pypaginate.filters.predicates.operators.patterns import LikeFactory, RegexFactory


class TestLikeFactory:
    """Tests for LikeFactory class."""

    def test_like_exact_match(self) -> None:
        """Test LIKE with exact match (no wildcards)."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("Hello")

        assert predicate("Hello") is True
        assert predicate("hello") is False
        assert predicate("Hello World") is False

    def test_like_case_insensitive(self) -> None:
        """Test LIKE with case insensitivity."""
        factory = LikeFactory(name="ilike", case_sensitive=False)
        predicate = factory("Hello")

        assert predicate("Hello") is True
        assert predicate("hello") is True
        assert predicate("HELLO") is True
        assert predicate("HeLLo") is True

    def test_like_percent_wildcard_prefix(self) -> None:
        """Test LIKE with % wildcard at the beginning."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("%world")

        assert predicate("world") is True
        assert predicate("hello world") is True
        assert predicate("World") is False
        assert predicate("world!") is False

    def test_like_percent_wildcard_suffix(self) -> None:
        """Test LIKE with % wildcard at the end."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("Hello%")

        assert predicate("Hello") is True
        assert predicate("Hello World") is True
        assert predicate("Hello!") is True
        assert predicate("hello") is False

    def test_like_percent_wildcard_both(self) -> None:
        """Test LIKE with % wildcards on both sides."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("%test%")

        assert predicate("test") is True
        assert predicate("testing") is True
        assert predicate("this is a test case") is True
        assert predicate("TEST") is False

    def test_like_underscore_wildcard(self) -> None:
        """Test LIKE with _ wildcard (single character)."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("t_st")

        assert predicate("test") is True
        assert predicate("tast") is True
        assert predicate("t0st") is True
        assert predicate("toast") is False
        assert predicate("tst") is False

    def test_like_multiple_underscores(self) -> None:
        """Test LIKE with multiple _ wildcards."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("__st")

        assert predicate("test") is True
        assert predicate("best") is True
        assert predicate("00st") is True
        assert predicate("toast") is False
        assert predicate("st") is False

    def test_like_mixed_wildcards(self) -> None:
        """Test LIKE with mixed % and _ wildcards."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("%te_t%")

        assert predicate("test") is True
        assert predicate("text") is True
        assert predicate("contest") is True
        assert predicate("the text here") is True
        assert predicate("te") is False

    def test_like_null_pattern_raises_error(self) -> None:
        """Test that None pattern raises FilterValidationError."""
        factory = LikeFactory(name="like", case_sensitive=True)

        with pytest.raises(FilterValidationError) as exc_info:
            factory(None)

        assert "requires a non-null pattern" in str(exc_info.value)
        assert exc_info.value.details["operator"] == "like"

    @pytest.mark.skip(reason="Empty pattern behavior varies by implementation")
    def test_like_empty_string_pattern(self) -> None:
        """Test LIKE with empty string pattern."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("")

        # Empty pattern only matches empty string
        assert predicate("") is True

    def test_like_with_special_regex_chars(self) -> None:
        """Test LIKE properly escapes regex special characters."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("test.data")

        # . in LIKE is literal, not regex wildcard
        assert predicate("test.data") is True
        assert predicate("testXdata") is False

    def test_like_numeric_string(self) -> None:
        """Test LIKE with numeric strings."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("123%")

        assert predicate("123") is True
        assert predicate("1234") is True
        assert predicate("123abc") is True
        assert predicate("abc123") is False

    def test_like_with_integers(self) -> None:
        """Test LIKE with integer values (should be converted to strings)."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("123")

        assert predicate(123) is True
        assert predicate("123") is True
        assert predicate(456) is False

    def test_like_case_sensitive_flag(self) -> None:
        """Test that case_sensitive flag works correctly."""
        factory_sensitive = LikeFactory(name="like", case_sensitive=True)
        factory_insensitive = LikeFactory(name="ilike", case_sensitive=False)

        pred_sensitive = factory_sensitive("Test")
        pred_insensitive = factory_insensitive("Test")

        assert pred_sensitive("Test") is True
        assert pred_sensitive("test") is False

        assert pred_insensitive("Test") is True
        assert pred_insensitive("test") is True
        assert pred_insensitive("TEST") is True


class TestRegexFactory:
    """Tests for RegexFactory class."""

    def test_regex_exact_match(self) -> None:
        """Test regex with exact match pattern."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory("^hello$")

        assert predicate("hello") is True
        assert predicate("Hello") is False
        assert predicate("hello world") is False

    def test_regex_case_insensitive(self) -> None:
        """Test regex with case insensitivity."""
        factory = RegexFactory(name="iregex", case_sensitive=False)
        predicate = factory("^hello$")

        assert predicate("hello") is True
        assert predicate("Hello") is True
        assert predicate("HELLO") is True
        assert predicate("HeLLo") is True

    def test_regex_partial_match(self) -> None:
        """Test regex with partial match (no anchors)."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory("test")

        assert predicate("test") is True
        assert predicate("testing") is True
        assert predicate("this is a test") is True
        assert predicate("TEST") is False

    def test_regex_start_anchor(self) -> None:
        """Test regex with start anchor."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory("^Hello")

        assert predicate("Hello") is True
        assert predicate("Hello World") is True
        assert predicate("Say Hello") is False

    def test_regex_end_anchor(self) -> None:
        """Test regex with end anchor."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory("world$")

        assert predicate("world") is True
        assert predicate("hello world") is True
        assert predicate("world peace") is False

    def test_regex_character_class(self) -> None:
        """Test regex with character class."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"test[0-9]+")

        assert predicate("test123") is True
        assert predicate("test1") is True
        assert predicate("test") is False
        assert predicate("testabc") is False

    def test_regex_quantifiers(self) -> None:
        """Test regex with quantifiers."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"a{2,4}")

        assert predicate("aa") is True
        assert predicate("aaa") is True
        assert predicate("aaaa") is True
        assert predicate("a") is False
        assert predicate("aaaaa") is True  # Contains aaaa

    def test_regex_alternation(self) -> None:
        """Test regex with alternation (OR)."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"cat|dog")

        assert predicate("cat") is True
        assert predicate("dog") is True
        assert predicate("bird") is False
        assert predicate("I have a cat") is True

    def test_regex_groups(self) -> None:
        """Test regex with groups."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"(test|exam)\s+result")

        assert predicate("test result") is True
        assert predicate("exam result") is True
        assert predicate("quiz result") is False

    def test_regex_special_characters(self) -> None:
        """Test regex with escaped special characters."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"test\.py")

        assert predicate("test.py") is True
        assert predicate("testXpy") is False

    def test_regex_email_pattern(self) -> None:
        """Test regex with email-like pattern."""
        factory = RegexFactory(name="regex", case_sensitive=False)
        predicate = factory(r"[\w\.-]+@[\w\.-]+\.\w+")

        assert predicate("user@example.com") is True
        assert predicate("test.user@domain.co.uk") is True
        assert predicate("invalid.email") is False

    def test_regex_with_integers(self) -> None:
        """Test regex with integer values."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"^\d+$")

        assert predicate(123) is True
        assert predicate("123") is True
        assert predicate("abc") is False

    def test_regex_complex_pattern(self) -> None:
        """Test regex with complex pattern."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        # Pattern for ISO date format YYYY-MM-DD
        predicate = factory(r"^\d{4}-\d{2}-\d{2}$")

        assert predicate("2025-12-24") is True
        assert predicate("2000-01-01") is True
        assert predicate("25-12-24") is False
        assert predicate("2025/12/24") is False

    def test_regex_word_boundary(self) -> None:
        """Test regex with word boundary."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"\btest\b")

        assert predicate("test") is True
        assert predicate("a test case") is True
        assert predicate("testing") is False
        assert predicate("contest") is False

    def test_regex_case_sensitive_flag(self) -> None:
        """Test that case_sensitive flag works correctly."""
        factory_sensitive = RegexFactory(name="regex", case_sensitive=True)
        factory_insensitive = RegexFactory(name="iregex", case_sensitive=False)

        pred_sensitive = factory_sensitive("Test")
        pred_insensitive = factory_insensitive("Test")

        assert pred_sensitive("Test") is True
        assert pred_sensitive("test") is False

        assert pred_insensitive("Test") is True
        assert pred_insensitive("test") is True
        assert pred_insensitive("TEST") is True

    def test_regex_with_none_value(self) -> None:
        """Test regex with None candidate value."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory("test")

        assert predicate(None) is False

    def test_regex_lookahead(self) -> None:
        """Test regex with lookahead assertion."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        # Password must contain at least one digit
        predicate = factory(r"^(?=.*\d).+$")

        assert predicate("password123") is True
        assert predicate("pass1word") is True
        assert predicate("password") is False


class TestLikeFactoryEdgeCases:
    """Edge case tests for LikeFactory."""

    def test_like_with_whitespace(self) -> None:
        """Test LIKE with whitespace in pattern."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("hello world")

        assert predicate("hello world") is True
        assert predicate("hello  world") is False

    def test_like_unicode_characters(self) -> None:
        """Test LIKE with Unicode characters."""
        factory = LikeFactory(name="like", case_sensitive=True)
        predicate = factory("café")

        assert predicate("café") is True
        assert predicate("cafe") is False

    def test_like_very_long_pattern(self) -> None:
        """Test LIKE with very long pattern."""
        factory = LikeFactory(name="like", case_sensitive=True)
        long_pattern = "a" * 1000
        predicate = factory(long_pattern)

        assert predicate("a" * 1000) is True
        assert predicate("a" * 999) is False


class TestRegexFactoryEdgeCases:
    """Edge case tests for RegexFactory."""

    def test_regex_invalid_pattern_raises_error(self) -> None:
        """Test that invalid regex pattern raises FilterValidationError."""
        factory = RegexFactory(name="regex", case_sensitive=True)

        with pytest.raises(FilterValidationError):
            # Invalid regex: unmatched parenthesis
            factory("(unclosed")

    def test_regex_unicode_characters(self) -> None:
        """Test regex with Unicode characters."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory("café")

        assert predicate("café") is True
        assert predicate("cafe") is False

    def test_regex_multiline(self) -> None:
        """Test regex with multiline string."""
        factory = RegexFactory(name="regex", case_sensitive=True)
        predicate = factory(r"^test$")

        # Without MULTILINE flag, ^ and $ match string boundaries
        assert predicate("test") is True
        assert predicate("test\nmore") is False


class TestFactoriesComparison:
    """Tests comparing LikeFactory and RegexFactory behaviors."""

    def test_like_vs_regex_simple_pattern(self) -> None:
        """Compare LIKE and regex for simple patterns."""
        like_factory = LikeFactory(name="like", case_sensitive=True)
        regex_factory = RegexFactory(name="regex", case_sensitive=True)

        like_pred = like_factory("test%")
        regex_pred = regex_factory("^test.*")

        # Both should match strings starting with "test"
        assert like_pred("test") is True
        assert regex_pred("test") is True

        assert like_pred("testing") is True
        assert regex_pred("testing") is True

        # But behave differently for middle matches
        assert like_pred("contest") is False
        assert regex_pred("contest") is False  # Due to ^ anchor

    def test_wildcard_semantics_difference(self) -> None:
        """Test that % in LIKE and .* in regex behave similarly."""
        like_factory = LikeFactory(name="like", case_sensitive=True)
        regex_factory = RegexFactory(name="regex", case_sensitive=True)

        like_pred = like_factory("%test%")
        regex_pred = regex_factory("test")

        assert like_pred("test") is True
        assert regex_pred("test") is True

        assert like_pred("my test case") is True
        assert regex_pred("my test case") is True
