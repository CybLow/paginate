"""SQL-backed search engine for text queries."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Unpack

from .conditions import ConditionContext, SqlConditionBuilder
from .options import ContextOptions, ResolvedOptions, SearchOptions, resolve_options


if TYPE_CHECKING:  # pragma: no cover - typing only
    from collections.abc import Sequence

    from ...text.api import SqlTextNormalizer
    from ...types import SqlClause, SqlStringExpression
    from .parser import QueryTokens, TokenParser


class SqlSearchService:
    """Facade orchestrating token parsing and SQL condition building."""

    DEFAULT_ID_PATTERN = re.compile(r"^[A-Za-z0-9:_\-]{6,}$")

    def __init__(
        self,
        parser: TokenParser,
        normalizer: SqlTextNormalizer,
        builder: SqlConditionBuilder,
        *,
        id_pattern: re.Pattern[str] | None = None,
    ) -> None:
        """Initialize the SQL search service.

        Args:
            parser: Token parser instance.
            normalizer: SQL text normalizer.
            builder: SQL condition builder.
            id_pattern: Optional regex for identifier tokens.
        """
        self._parser = parser
        self._normalizer = normalizer
        self._builder = builder
        self._id_pattern = id_pattern or self.DEFAULT_ID_PATTERN

    def normalize_text(self, value: str) -> str:
        """Normalize free text using the configured SQL text normalizer.

        Args:
            value: Text to normalize.

        Returns:
            Normalized text string.
        """
        return self._normalizer.normalize_text(value)

    def normalize_column(self, column: SqlStringExpression) -> SqlStringExpression:
        """Normalize a column expression for consistent LIKE comparisons.

        Args:
            column: Column expression to normalize.

        Returns:
            Normalized column expression.
        """
        return self._normalizer.normalize_column(column)

    def parse_tokens(self, term: str) -> QueryTokens:
        """Parse a raw search term into normalized tokens.

        Args:
            term: Raw search query string.

        Returns:
            Parsed QueryTokens instance.
        """
        return self._parser.parse(term, self._normalizer.normalize_text, raw_transform=str.strip)

    @staticmethod
    def has_criteria(fields: Sequence[str], tokens: QueryTokens) -> bool:
        """Check if search criteria exist.

        Args:
            fields: Field list to search.
            tokens: Parsed query tokens.

        Returns:
            True if both fields and tokens contain content.
        """
        return bool(fields) and tokens.has_content()

    def create_conditions(
        self,
        model_class: type,
        search_fields: Sequence[str],
        search_term: str,
        **options: Unpack[SearchOptions],
    ) -> list[SqlClause]:
        """Create SQLAlchemy boolean expressions for the given search term.

        Args:
            model_class: ORM model class providing column attributes.
            search_fields: Field names to target for LIKE expressions.
            search_term: Raw search query string.
            **options: User-facing options resolved via options module.

        Returns:
            A list of SQLAlchemy boolean expressions ready to combine.
        """
        resolved = resolve_options(options, default_pattern=self._id_pattern)
        context = self._context_from_term(model_class, search_fields, search_term, resolved)
        if context is None:
            return []
        return self._builder.build_from_context(context, mode=resolved.mode)

    def _build_context(
        self,
        model_class: type,
        fields: Sequence[str],
        tokens: QueryTokens,
        *,
        options: ContextOptions,
    ) -> ConditionContext:
        """Build a ConditionContext consumed by strategies.

        Args:
            model_class: ORM model class.
            fields: Field names to search.
            tokens: Parsed query tokens.
            options: Context options.

        Returns:
            A ConditionContext instance.
        """
        return self._builder.context(model_class, fields, tokens, **options)

    def _context_from_term(
        self,
        model_class: type,
        fields: Sequence[str],
        term: str,
        options: ResolvedOptions,
    ) -> ConditionContext | None:
        """Parse term and prepare context when criteria exist.

        Args:
            model_class: ORM model class.
            fields: Field names to search.
            term: Raw search query.
            options: Resolved options.

        Returns:
            ConditionContext if criteria exist, None otherwise.
        """
        tokens = self.parse_tokens(term)
        if not self.has_criteria(fields, tokens):
            return None
        return self._build_context(model_class, fields, tokens, options=options.context)


__all__ = ["SqlConditionBuilder", "SqlSearchService"]


if TYPE_CHECKING:  # pragma: no cover - static analyzers only
    _CONTRACT_REFERENCE = SqlSearchService.create_conditions
