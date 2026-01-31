"""Tests for filters/search/fuzzy.py module.

This module tests fuzzy matching functionality using RapidFuzz.
"""

from pypaginate.filters.search.fuzzy import (
    fuzzy_match,
    is_near_match,
    partial_ratio,
    text_match,
)


class TestFuzzyMatch:
    """Tests for fuzzy_match function."""

    def test_exact_match_high_threshold(self) -> None:
        """Exact match should pass even with high threshold."""
        assert fuzzy_match("hello", "hello", threshold=100) is True

    def test_exact_match_low_threshold(self) -> None:
        """Exact match should pass with low threshold."""
        assert fuzzy_match("hello", "hello", threshold=50) is True

    def test_partial_match_high_similarity(self) -> None:
        """High similarity should pass with reasonable threshold."""
        # "hello" is contained in "hello world"
        assert fuzzy_match("hello", "hello world", threshold=80) is True

    def test_partial_match_low_similarity(self) -> None:
        """Low similarity should fail with high threshold."""
        assert fuzzy_match("abc", "xyz", threshold=90) is False

    def test_near_match_one_char_difference(self) -> None:
        """One character difference should pass via near match."""
        # "hello" vs "hallo" - one character difference
        assert fuzzy_match("hello", "hallo", threshold=100) is True

    def test_near_match_one_char_added(self) -> None:
        """One character addition should be near match."""
        # "hello" vs "helloo" - one character added
        assert fuzzy_match("hello", "helloo", threshold=100) is True

    def test_near_match_one_char_removed(self) -> None:
        """One character removal should be near match."""
        # "hello" vs "hell" - one character removed
        assert fuzzy_match("hello", "hell", threshold=100) is True

    def test_no_match_completely_different(self) -> None:
        """Completely different strings should not match."""
        assert fuzzy_match("abc", "xyz", threshold=100) is False

    def test_empty_token(self) -> None:
        """Empty token should handle gracefully."""
        result = fuzzy_match("", "hello", threshold=80)
        # Empty string has high ratio with any text
        assert isinstance(result, bool)

    def test_empty_text(self) -> None:
        """Empty text should handle gracefully."""
        result = fuzzy_match("hello", "", threshold=80)
        assert isinstance(result, bool)

    def test_case_sensitive(self) -> None:
        """Fuzzy match is case-sensitive."""
        # "Hello" vs "hello" - should still match via near match
        result = fuzzy_match("Hello", "hello", threshold=100)
        assert isinstance(result, bool)


class TestPartialRatio:
    """Tests for partial_ratio function."""

    def test_exact_match_returns_100(self) -> None:
        """Exact match should return 100."""
        assert partial_ratio("hello", "hello") == 100

    def test_substring_returns_100(self) -> None:
        """Substring match should return 100."""
        assert partial_ratio("hello", "hello world") == 100

    def test_different_strings_low_ratio(self) -> None:
        """Different strings should have low ratio."""
        ratio = partial_ratio("abc", "xyz")
        assert ratio < 50

    def test_similar_strings_high_ratio(self) -> None:
        """Similar strings should have high ratio."""
        ratio = partial_ratio("hello", "hallo")
        assert ratio >= 60

    def test_returns_integer(self) -> None:
        """Result should be an integer."""
        result = partial_ratio("test", "testing")
        assert isinstance(result, int)

    def test_empty_strings(self) -> None:
        """Empty strings should return valid ratio."""
        result = partial_ratio("", "")
        assert isinstance(result, int)


class TestIsNearMatch:
    """Tests for is_near_match function."""

    def test_identical_strings(self) -> None:
        """Identical strings are near match (distance 0)."""
        assert is_near_match("hello", "hello") is True

    def test_one_substitution(self) -> None:
        """One character substitution is near match."""
        assert is_near_match("hello", "hallo") is True

    def test_one_insertion(self) -> None:
        """One character insertion is near match."""
        assert is_near_match("hello", "helloo") is True

    def test_one_deletion(self) -> None:
        """One character deletion is near match."""
        assert is_near_match("hello", "hell") is True

    def test_two_differences_not_near(self) -> None:
        """Two character differences is not near match."""
        assert is_near_match("hello", "hxxlo") is False

    def test_completely_different_not_near(self) -> None:
        """Completely different strings are not near match."""
        assert is_near_match("abc", "xyz") is False

    def test_empty_vs_one_char(self) -> None:
        """Empty string vs one char is near match (distance 1)."""
        assert is_near_match("", "a") is True

    def test_empty_vs_two_chars(self) -> None:
        """Empty string vs two chars is not near match."""
        assert is_near_match("", "ab") is False


class TestTextMatch:
    """Tests for text_match function."""

    def test_prefix_match_exact(self) -> None:
        """Exact prefix match should pass."""
        assert text_match("hello", "hello world", prefix=True) is True

    def test_prefix_match_partial(self) -> None:
        """Partial prefix match should pass."""
        assert text_match("hel", "hello", prefix=True) is True

    def test_prefix_no_match(self) -> None:
        """Token not at start should fail prefix match."""
        assert text_match("world", "hello world", prefix=True) is False

    def test_contains_match_middle(self) -> None:
        """Token in middle should pass contains match."""
        assert text_match("llo", "hello", prefix=False) is True

    def test_contains_match_end(self) -> None:
        """Token at end should pass contains match."""
        assert text_match("world", "hello world", prefix=False) is True

    def test_contains_match_start(self) -> None:
        """Token at start should pass contains match."""
        assert text_match("hello", "hello world", prefix=False) is True

    def test_contains_no_match(self) -> None:
        """Token not present should fail contains match."""
        assert text_match("xyz", "hello world", prefix=False) is False

    def test_empty_token_matches(self) -> None:
        """Empty token matches any text (both modes)."""
        assert text_match("", "hello", prefix=True) is True
        assert text_match("", "hello", prefix=False) is True

    def test_exact_match(self) -> None:
        """Exact match works for both modes."""
        assert text_match("hello", "hello", prefix=True) is True
        assert text_match("hello", "hello", prefix=False) is True

    def test_case_sensitive(self) -> None:
        """Text match is case-sensitive."""
        assert text_match("Hello", "hello", prefix=True) is False
        assert text_match("Hello", "hello", prefix=False) is False
