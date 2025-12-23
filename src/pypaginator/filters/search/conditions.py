"""Builders composing SQLAlchemy expressions for search tokens."""

from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

from pypaginator.exceptions import SearchQueryError

from .strategies import (
    ConditionContext,
    ConditionStrategy,
    IdConditionStrategy,
    PhraseConditionStrategy,
    TermConditionStrategy,
)


if TYPE_CHECKING:  # pragma: no cover - typing only
    import re
    from collections.abc import Sequence

    from ...text.api import SqlTextNormalizer
    from ...types import SqlClause
    from .parser import QueryTokens


# Import SearchMode from the centralized location
from enum import Enum


class SearchMode(Enum):
    """Aggregation mode for search conditions."""

    AND = "and"
    OR = "or"
    FUZZY = "fuzzy"


class SqlConditionBuilder:
    """Compose SQLAlchemy expressions for search tokens via strategies."""

    def __init__(self, normalizer: SqlTextNormalizer) -> None:
        self._strategies: tuple[ConditionStrategy, ...] = (
            IdConditionStrategy(),
            PhraseConditionStrategy(normalizer),
            TermConditionStrategy(normalizer),
        )

    def build(
        self,
        model_class: type,
        fields: Sequence[str],
        tokens: QueryTokens,
        *,
        mode: SearchMode,
        prefix: bool,
        id_fields: Sequence[str],
        id_token_regex: re.Pattern[str],
    ) -> list[SqlClause]:
        """Build SQL clauses for the provided tokens and options.

        Args:
            model_class: ORM model class providing searchable attributes.
            fields: Field names targeted for LIKE comparisons.
            tokens: Normalized tokens extracted from the search term.
            mode: Aggregation mode for combining sub-clauses.
            prefix: Whether LIKE patterns use prefix semantics.
            id_fields: Field names acting as identifiers.
            id_token_regex: Pattern used to detect identifier tokens.

        Returns:
            A list of SQLAlchemy boolean expressions.
        """
        context = self.context(
            model_class,
            fields,
            tokens,
            prefix,
            id_fields,
            id_token_regex,
        )
        return self.build_from_context(context, mode=mode)

    def build_from_context(self, context: ConditionContext, *, mode: SearchMode) -> list[SqlClause]:
        """Build SQL clauses from an existing :class:`ConditionContext`."""
        return _combine(self._gather(context), mode)

    def _gather(self, context: ConditionContext) -> list[SqlClause]:
        """Gather raw clauses from all registered strategies."""
        return list(chain.from_iterable(strategy.collect(context) for strategy in self._strategies))

    @staticmethod
    def context(
        model_class: type,
        fields: Sequence[str],
        tokens: QueryTokens,
        prefix: bool,
        id_fields: Sequence[str],
        id_token_regex: re.Pattern[str],
    ) -> ConditionContext:
        """Create a :class:`ConditionContext` from inputs."""
        return ConditionContext(model_class, fields, tokens, prefix, id_fields, id_token_regex)


def _combine(expressions: list[SqlClause], mode: SearchMode) -> list[SqlClause]:
    """Combine SQL expressions according to the search mode.

    Args:
        expressions: List of SQL boolean expressions.
        mode: Search mode (AND/OR).

    Returns:
        List containing a single combined expression.

    Raises:
        SearchQueryError: If mode is unsupported.
    """
    from sqlalchemy.sql import and_, or_

    if not expressions:
        return []
    if mode is SearchMode.AND:
        return [and_(*expressions)]  # type: ignore[arg-type]
    if mode is SearchMode.OR:
        return [or_(*expressions)]  # type: ignore[arg-type]
    raise SearchQueryError(
        "Unsupported search mode for SQL search",
        details={"mode": mode.value},
    )


__all__ = [
    "ConditionContext",
    "ConditionStrategy",
    "IdConditionStrategy",
    "PhraseConditionStrategy",
    "SearchMode",
    "SqlConditionBuilder",
    "TermConditionStrategy",
]
