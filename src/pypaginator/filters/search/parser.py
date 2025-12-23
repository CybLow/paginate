"""Tokenization helpers for textual search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Final

import pyparsing as _pyparsing


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

    from pyparsing import ParserElement, ParseResults

# Token type constants
_TOKEN_PHRASE: Final[str] = "phrase"
"""Constant for phrase token type."""

_TOKEN_TERM: Final[str] = "term"
"""Constant for term token type."""


def _mark_phrase(tokens: ParseResults) -> tuple[str, str]:
    """Mark a parsed token as a quoted phrase.

    Args:
        tokens: Pyparsing result sequence for the token.

    Returns:
        A ("phrase", value) tuple.
    """
    return _TOKEN_PHRASE, str(tokens[0])


def _mark_term(tokens: ParseResults) -> tuple[str, str]:
    """Mark a parsed token as a free term.

    Args:
        tokens: Pyparsing result sequence for the token.

    Returns:
        A ("term", value) tuple.
    """
    return _TOKEN_TERM, str(tokens[0])


def _build_parser() -> ParserElement:
    """Build and return the pyparsing grammar for tokenization.

    Returns:
        A configured pyparsing ParserElement.
    """
    _pyparsing.ParserElement.set_default_whitespace_chars(" \t\r\n")
    phrase = _pyparsing.QuotedString('"', escChar="\\").set_parse_action(_mark_phrase)
    term = _pyparsing.Regex(r'[^"\s]+').set_parse_action(_mark_term)
    return _pyparsing.ZeroOrMore(_pyparsing.MatchFirst((phrase, term)))


def _group_pyparsing_tokens(
    parsed: ParseResults,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Group parsed tokens into (phrases, terms) tuples.

    Args:
        parsed: Pyparsing result sequence.

    Returns:
        Two tuples: normalized phrases, normalized terms.
    """
    phrases: list[str] = []
    terms: list[str] = []
    for kind, value in parsed:
        (phrases if kind == _TOKEN_PHRASE else terms).append(value)
    return tuple(phrases), tuple(terms)


@dataclass(frozen=True)
class QueryTokens:
    """Normalized tokens extracted from a raw query string.

    Attributes:
        terms: Lowercased, normalized individual tokens.
        phrases: Lowercased, normalized quoted phrases.
        raw: Original unnormalized terms (for ID matching, etc.).
    """

    terms: tuple[str, ...]
    phrases: tuple[str, ...]
    raw: tuple[str, ...]

    def has_content(self) -> bool:
        """Check if tokens contain any searchable content.

        Returns:
            True if any terms, phrases, or raw tokens exist.
        """
        return bool(self.terms or self.phrases or self.raw)


class TokenParser:
    """Extract quoted phrases and free terms from a search query.

    Attributes:
        _GRAMMAR: Shared pyparsing grammar for tokenization.
    """

    _GRAMMAR: ClassVar[ParserElement | None] = None

    def parse(
        self,
        query: str,
        normalizer: Callable[[str], str],
        *,
        raw_transform: Callable[[str], str] | None = None,
    ) -> QueryTokens:
        """Parse and normalize a search query into tokens.

        Args:
            query: Input query string.
            normalizer: Callable used to normalize tokens and phrases.
            raw_transform: Optional transform applied to raw terms.

        Returns:
            A QueryTokens instance with normalized values.
        """
        chunks = self._tokenize(query)
        return self._build_tokens(chunks, normalizer, raw_transform)

    def _build_tokens(
        self,
        chunks: tuple[tuple[str, ...], tuple[str, ...]],
        normalizer: Callable[[str], str],
        raw_transform: Callable[[str], str] | None,
    ) -> QueryTokens:
        """Build normalized tokens from parsed chunks.

        Args:
            chunks: Tuple of (phrases, terms) from parsing.
            normalizer: Function to normalize text.
            raw_transform: Optional transform for raw terms.

        Returns:
            A QueryTokens instance.
        """
        phrases_raw, terms_raw = chunks
        terms = self._normalize_terms(terms_raw, normalizer)
        phrases = self._normalize_terms(phrases_raw, normalizer)
        raw = self._normalize_raw_terms(terms_raw, raw_transform)
        return QueryTokens(terms=terms, phrases=phrases, raw=raw)

    def _tokenize(self, query: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Tokenize a query with the configured grammar, if any content.

        Args:
            query: Query string to tokenize.

        Returns:
            Tuple of (phrases, terms).
        """
        if not query.strip():
            return (), ()
        return self._tokenize_with_grammar(query)

    def _tokenize_with_grammar(
        self, query: str
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Run the pyparsing grammar and group tokens by kind.

        Args:
            query: Query string to parse.

        Returns:
            Tuple of (phrases, terms).
        """
        grammar = self._ensure_grammar()
        try:
            parsed = grammar.parse_string(query, parseAll=True)
        except _pyparsing.ParseException:
            return (), ()
        return _group_pyparsing_tokens(parsed)

    @classmethod
    def _ensure_grammar(cls) -> ParserElement:
        """Return the shared grammar, building it lazily when required."""

        if cls._GRAMMAR is None:
            cls._GRAMMAR = _build_parser()
        return cls._GRAMMAR

    @staticmethod
    def _normalize(
        values: Sequence[str], normalizer: Callable[[str], str]
    ) -> Iterable[str]:
        """Normalize and filter out empty values.

        Args:
            values: Values to normalize.
            normalizer: Normalization function.

        Returns:
            Iterator of normalized non-empty values.
        """
        return (normalizer(value) for value in values if value.strip())

    @staticmethod
    def _normalize_raw(
        values: Sequence[str],
        raw_transform: Callable[[str], str] | None,
    ) -> Iterable[str]:
        """Optionally transform and filter raw values.

        Args:
            values: Raw values to process.
            raw_transform: Optional transformation function.

        Returns:
            Iterator of processed values.
        """
        for value in values:
            if not value.strip():
                continue
            yield raw_transform(value) if raw_transform else value.strip()

    def _normalize_terms(
        self, values: Sequence[str], normalizer: Callable[[str], str]
    ) -> tuple[str, ...]:
        """Normalize and return terms as a tuple.

        Args:
            values: Terms to normalize.
            normalizer: Normalization function.

        Returns:
            Tuple of normalized terms.
        """
        return tuple(self._normalize(values, normalizer))

    def _normalize_raw_terms(
        self, values: Sequence[str], raw_transform: Callable[[str], str] | None
    ) -> tuple[str, ...]:
        """Normalize raw terms using the optional transformer.

        Args:
            values: Raw terms to process.
            raw_transform: Optional transformation function.

        Returns:
            Tuple of processed raw terms.
        """
        return tuple(self._normalize_raw(values, raw_transform))


__all__ = ["QueryTokens", "TokenParser"]
