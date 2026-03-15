"""Tests for TokenParser."""

from __future__ import annotations

import pytest

from pypaginate.search.parser import TokenParser


@pytest.fixture()
def parser() -> TokenParser:
    """Shared TokenParser instance."""
    return TokenParser()


class TestParseSimple:
    @pytest.mark.parametrize(
        ("query", "expected"),
        [
            ("hello", ["hello"]),
            ("hello world", ["hello", "world"]),
            ("  hello   world  ", ["hello", "world"]),
        ],
        ids=["single_word", "two_words", "extra_whitespace"],
    )
    def test_plain_text_tokenized(
        self,
        parser: TokenParser,
        query: str,
        expected: list[str],
    ) -> None:
        result = parser.parse(query)

        assert result == expected

    @pytest.mark.parametrize(
        "query",
        ["", "   ", "\t\n"],
        ids=["empty", "spaces", "whitespace_chars"],
    )
    def test_blank_input_returns_empty(
        self,
        parser: TokenParser,
        query: str,
    ) -> None:
        result = parser.parse(query)

        assert result == []


class TestParseQuoted:
    def test_quoted_phrase_kept_intact(self, parser: TokenParser) -> None:
        result = parser.parse('"john doe"')

        assert result == ["john doe"]

    def test_mixed_quoted_and_plain(self, parser: TokenParser) -> None:
        result = parser.parse('"john doe" admin')

        assert result == ["john doe", "admin"]

    def test_multiple_quoted_phrases(self, parser: TokenParser) -> None:
        result = parser.parse('"hello world" "foo bar"')

        assert result == ["hello world", "foo bar"]


class TestParseEdgeCases:
    def test_unclosed_quote_falls_back(self, parser: TokenParser) -> None:
        result = parser.parse('"hello world')

        assert len(result) >= 1
        assert "hello" in result[0] or "hello world" in " ".join(result)

    def test_single_char_token(self, parser: TokenParser) -> None:
        result = parser.parse("a")

        assert result == ["a"]

    def test_empty_quotes_returns_empty(self, parser: TokenParser) -> None:
        result = parser.parse('""')

        assert result == []

    def test_whitespace_only_quotes(self, parser: TokenParser) -> None:
        result = parser.parse('"  "')

        assert result == ["  "]


class TestParseSpecialCharacters:
    def test_special_characters_preserved(
        self,
        parser: TokenParser,
    ) -> None:
        result = parser.parse("hello@world.com")

        assert result == ["hello@world.com"]
