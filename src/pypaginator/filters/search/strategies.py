"""Composable strategies for SQL pagination search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from .helpers import (
    collect_clauses,
    column_attributes,
    match_columns,
    matching_ids,
    phrase_clause_factory,
    term_clause_factory,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    import re
    from collections.abc import Sequence

    from ...text.api import SqlTextNormalizer
    from ...types import SqlClause
    from .parser import QueryTokens


@dataclass(frozen=True)
class ConditionContext:
    """Immutable context provided to each condition strategy."""

    model_class: type
    fields: Sequence[str]
    tokens: QueryTokens
    prefix: bool
    id_fields: Sequence[str]
    id_pattern: re.Pattern[str]


class ConditionStrategy(Protocol):
    """Strategy interface producing SQL clauses from the context."""

    def collect(self, context: ConditionContext) -> list[SqlClause]: ...


class IdConditionStrategy:
    """Collect identifiers matching the configured ID pattern."""

    @staticmethod
    def collect(context: ConditionContext) -> list[SqlClause]:
        """Return ID matching clauses for the configured columns.

        Args:
            context: Context providing tokens and id_fields.

        Returns:
            A list containing a single clause, or an empty list when none.
        """
        tokens = matching_ids(context)
        if not tokens:
            return []
        columns = column_attributes(context.model_class, context.id_fields)
        condition = match_columns(columns, tokens)
        return [condition] if condition is not None else []


class PhraseConditionStrategy:
    """Create LIKE clauses for quoted phrases."""

    def __init__(self, normalizer: SqlTextNormalizer) -> None:
        """Initialize the phrase condition strategy.

        Args:
            normalizer: SQL text normalizer.
        """
        self._normalizer = normalizer

    def collect(self, context: ConditionContext) -> list[SqlClause]:
        """Return LIKE clauses for quoted phrases in the query.

        Args:
            context: Condition context with phrase tokens.

        Returns:
            List of LIKE clauses for phrases.
        """
        builder = phrase_clause_factory(self._normalizer)
        return collect_clauses(context, context.tokens.phrases, builder)


class TermConditionStrategy:
    """Create LIKE clauses for individual tokens."""

    def __init__(self, normalizer: SqlTextNormalizer) -> None:
        """Initialize the term condition strategy.

        Args:
            normalizer: SQL text normalizer.
        """
        self._normalizer = normalizer

    def collect(self, context: ConditionContext) -> list[SqlClause]:
        """Return LIKE clauses for individual terms, skipping ID tokens.

        Args:
            context: Condition context with term tokens.

        Returns:
            List of LIKE clauses for terms.
        """
        builder = term_clause_factory(self._normalizer, matching_ids(context))
        return collect_clauses(context, context.tokens.terms, builder)


__all__ = [
    "ConditionContext",
    "ConditionStrategy",
    "IdConditionStrategy",
    "PhraseConditionStrategy",
    "TermConditionStrategy",
]
