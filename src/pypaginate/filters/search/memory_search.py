"""In-memory search engine for text queries."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, TypeVar

from pypaginate.exceptions import SearchQueryError

from ..predicates.field_accessor import FieldAccessor
from .conditions import SearchMode
from .fuzzy import fuzzy_match, text_match


if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from ...text.api import MemoryTextNormalizer
    from .parser import QueryTokens, TokenParser

T = TypeVar("T")

# Constants
DEFAULT_FUZZY_THRESHOLD = 75
DEFAULT_SEARCH_MODE = SearchMode.AND


# ============================================================================
# Helpers Section
# ============================================================================

TextConverter = Callable[[object], str]


@dataclass(frozen=True)
class MatchOptions:
    """Runtime options describing how to match tokens against values."""

    prefix: bool
    fuzzy: bool
    threshold: int


def _decode_bytes(value: object) -> str:
    """Decode bytes-like objects to UTF-8 strings.

    Args:
        value: Value to decode.

    Returns:
        Decoded UTF-8 string.

    Raises:
        TypeError: If value is not bytes-like.
    """
    if not isinstance(value, bytes | bytearray | memoryview):
        raise TypeError
    return bytes(value).decode("utf-8", errors="ignore")


_SAFE_TEXT_CONVERTERS: tuple[TextConverter, ...] = (
    _decode_bytes,
    lambda candidate: "" if candidate is None else str(candidate),
    repr,
)


def safe_text(value: object) -> str:
    """Return a safe string representation for arbitrary values.

    Args:
        value: Arbitrary Python object.

    Returns:
        A best-effort string conversion, resilient to common errors.
    """
    for convert in _SAFE_TEXT_CONVERTERS:
        try:
            return convert(value)
        except (AttributeError, TypeError, UnicodeError, ValueError):
            continue
    return ""


def token_values(tokens: QueryTokens) -> tuple[str, ...]:
    """Flatten phrases and terms into a deterministic tuple.

    Args:
        tokens: Token container with phrases and terms.

    Returns:
        Tuple concatenating phrases followed by terms.
    """
    return *tokens.phrases, *tokens.terms


def select_flags(flags: tuple[bool, ...], mode: SearchMode) -> bool:
    """Aggregate match flags according to the requested mode.

    Args:
        flags: Per-token match results.
        mode: Aggregation strategy (AND/OR/FUZZY).

    Returns:
        Aggregated boolean outcome according to mode.

    Raises:
        SearchQueryError: If mode is unsupported.
    """
    if not flags:
        return True
    if mode is SearchMode.FUZZY:
        return any(flags)
    if mode is SearchMode.AND:
        return all(flags)
    if mode is SearchMode.OR:
        return any(flags)
    raise SearchQueryError(
        "Unsupported search mode for in-memory search",
        details={"mode": mode.value},
    )


def match_value(
    normalizer: MemoryTextNormalizer,
    value: object,
    token: str,
    options: MatchOptions,
) -> bool:
    """Return True when a single value matches token under options.

    Args:
        normalizer: Text normalizer for value.
        value: Value to check.
        token: Search token.
        options: Match configuration.

    Returns:
        True if value matches token.
    """
    text = normalizer.normalize_text(safe_text(value))
    if options.fuzzy:
        return fuzzy_match(token, text, options.threshold)
    return text_match(token, text, options.prefix)


def _any_field_matches(
    normalizer: MemoryTextNormalizer,
    item: object,
    field_accessors: Sequence[FieldAccessor],
    token: str,
    options: MatchOptions,
) -> bool:
    """Return True when any accessor resolves a value matching token.

    Args:
        normalizer: Text normalizer.
        item: Item to search in.
        field_accessors: Field accessors to evaluate.
        token: Search token.
        options: Match configuration.

    Returns:
        True if any field matches.
    """
    return any(
        match_value(normalizer, accessor.resolve(item), token, options)
        for accessor in field_accessors
    )


def match_flags(
    normalizer: MemoryTextNormalizer,
    item: object,
    *,
    field_accessors: Sequence[FieldAccessor],
    tokens: tuple[str, ...],
    options: MatchOptions,
) -> tuple[bool, ...]:
    """Return per-token match flags for an item across field_accessors.

    Args:
        normalizer: Text normalizer.
        item: Item to search.
        field_accessors: Fields to search in.
        tokens: Search tokens to match.
        options: Match configuration.

    Returns:
        Tuple of boolean flags, one per token.
    """
    return tuple(
        _any_field_matches(normalizer, item, field_accessors, token, options) for token in tokens
    )


def accessors(fields: Sequence[str]) -> tuple[FieldAccessor, ...]:
    """Return typed accessors for each requested field.

    Args:
        fields: Field paths to create accessors for.

    Returns:
        Tuple of FieldAccessor instances.
    """
    return tuple(FieldAccessor.from_string(field) for field in fields)


# ============================================================================
# Options Section
# ============================================================================


@dataclass(frozen=True)
class MemorySearchOptions:
    """Value object bridging service configuration and match options."""

    mode: SearchMode = DEFAULT_SEARCH_MODE
    prefix: bool = False
    fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD

    def to_match(self) -> MatchOptions:
        """Convert to low-level match options used by the engine.

        Returns:
            A MatchOptions instance derived from this configuration.
        """
        return MatchOptions(
            prefix=self.prefix,
            fuzzy=self.mode is SearchMode.FUZZY,
            threshold=self.fuzzy_threshold,
        )


# ============================================================================
# Engine Classes
# ============================================================================


class MemorySearchEngine:
    """Filter Python objects using SQL-compatible normalisation rules."""

    def __init__(self, normalizer: MemoryTextNormalizer) -> None:
        """Initialize the search engine with a text normalizer.

        Args:
            normalizer: Text normalizer for consistent comparisons.
        """
        self._normalizer = normalizer

    @property
    def normalizer(self) -> MemoryTextNormalizer:
        """Get the configured text normalizer.

        Returns:
            The MemoryTextNormalizer instance.
        """
        return self._normalizer

    def filter(
        self,
        items: Iterable[T],
        fields: Sequence[str],
        tokens: QueryTokens,
        *,
        mode: SearchMode,
        prefix: bool,
        fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD,
    ) -> list[T]:
        """Return items that match tokenized criteria across selected fields.

        Args:
            items: Iterable of items to filter.
            fields: Dot paths to resolve within each item.
            tokens: Parsed query tokens.
            mode: Aggregation mode (AND/OR/FUZZY).
            prefix: Whether to use prefix matching for non-fuzzy mode.
            fuzzy_threshold: RapidFuzz threshold for fuzzy mode.

        Returns:
            A list of items matching the criteria.
        """
        config = MemorySearchOptions(mode, prefix, fuzzy_threshold)
        selector = self._selector(fields, tokens, config)
        return [item for item in items if selector(item)]

    def _selector(
        self,
        fields: Sequence[str],
        tokens: QueryTokens,
        options: MemorySearchOptions,
    ) -> Callable[[object], bool]:
        """Return a predicate that aggregates match flags according to mode.

        Args:
            fields: Field paths to search.
            tokens: Query tokens.
            options: Search configuration.

        Returns:
            A predicate function for filtering items.
        """
        matcher = self._matcher(fields, tokens, options)
        return lambda item: select_flags(matcher(item), options.mode)

    def _matcher(
        self,
        fields: Sequence[str],
        tokens: QueryTokens,
        options: MemorySearchOptions,
    ) -> Callable[[object], tuple[bool, ...]]:
        """Return a callable producing boolean flags per token for an item.

        Args:
            fields: Field paths to search.
            tokens: Query tokens.
            options: Search configuration.

        Returns:
            A function producing match flags.
        """
        match_options = options.to_match()
        return partial(
            match_flags,
            self._normalizer,
            field_accessors=accessors(fields),
            tokens=token_values(tokens),
            options=match_options,
        )


class MemorySearchService:
    """Facade orchestrating token parsing and in-memory filtering."""

    def __init__(self, parser: TokenParser, engine: MemorySearchEngine) -> None:
        """Initialize the search service.

        Args:
            parser: Token parser instance.
            engine: In-memory search engine.
        """
        self._parser = parser
        self._engine = engine

    def search(
        self,
        items: Iterable[T],
        fields: Sequence[str],
        term: str,
        *,
        mode: SearchMode = DEFAULT_SEARCH_MODE,
        prefix: bool = False,
        fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD,
    ) -> list[T]:
        """Filter items according to a search term and options.

        Args:
            items: Iterable of items to filter.
            fields: Dot paths evaluated for each item.
            term: Raw search query string.
            mode: Aggregation mode (AND/OR/FUZZY).
            prefix: Whether to enable prefix matching.
            fuzzy_threshold: RapidFuzz threshold for fuzzy mode.

        Returns:
            A list of matching items.
        """
        tokens = self._prepare(fields, term)
        if tokens is None:
            return list(items)
        config = MemorySearchOptions(mode, prefix, fuzzy_threshold)
        return self._filter(items, fields, tokens, config)

    def _parse(self, term: str) -> QueryTokens:
        """Parse and normalize the raw search term into tokens.

        Args:
            term: Raw search query string.

        Returns:
            Parsed and normalized QueryTokens.
        """
        normalise = self._engine.normalizer.normalize_text
        return self._parser.parse(term, normalise, raw_transform=str.strip)

    @staticmethod
    def _has_terms(tokens: QueryTokens) -> bool:
        """Return True when tokens contain any content.

        Args:
            tokens: QueryTokens to check.

        Returns:
            True if tokens have content.
        """
        return tokens.has_content()

    def _prepare(self, fields: Sequence[str], term: str) -> QueryTokens | None:
        """Parse the query and return tokens only when criteria exist.

        Args:
            fields: Fields to search.
            term: Search query string.

        Returns:
            QueryTokens if valid criteria exist, None otherwise.
        """
        if not fields:
            return None
        tokens = self._parse(term)
        return tokens if self._has_terms(tokens) else None

    def _filter(
        self,
        items: Iterable[T],
        fields: Sequence[str],
        tokens: QueryTokens,
        options: MemorySearchOptions,
    ) -> list[T]:
        """Delegate filtering to the underlying engine with prepared options.

        Args:
            items: Items to filter.
            fields: Fields to search.
            tokens: Query tokens.
            options: Search configuration.

        Returns:
            Filtered list of items.
        """
        return self._engine.filter(
            items,
            fields,
            tokens,
            mode=options.mode,
            prefix=options.prefix,
            fuzzy_threshold=options.fuzzy_threshold,
        )


__all__ = [
    "DEFAULT_FUZZY_THRESHOLD",
    "DEFAULT_SEARCH_MODE",
    "MemorySearchEngine",
    "MemorySearchService",
]
