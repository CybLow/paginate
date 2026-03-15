"""SQLAlchemy search backend translating SearchSpec to ILIKE clauses.

Combines field conditions with OR (any field matches) and
token conditions with AND (all tokens must match).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.adapters.sqlalchemy.columns import resolve_column
from pypaginate.domain.enums import SearchFieldMode
from pypaginate.text.normalize import normalize_text


if TYPE_CHECKING:
    from sqlalchemy.sql import Select

    from pypaginate.domain.specs import SearchSpec


class SQLAlchemySearchBackend:
    """Translates SearchSpec to SQLAlchemy ILIKE clauses.

    Satisfies ``SearchBackend`` protocol. Tokenizes the query
    and matches each token against all specified fields.
    """

    def apply_search(
        self,
        query: object,
        spec: SearchSpec,
    ) -> object:
        """Apply a search spec to a SQLAlchemy Select.

        Args:
            query: A SQLAlchemy Select statement.
            spec: Search specification with query and fields.

        Returns:
            Modified Select with WHERE clauses for search.
        """
        stmt: Select[Any] = query  # type: ignore[assignment]
        normalized = normalize_text(spec.query)
        if not normalized:
            return stmt
        tokens = normalized.split()
        return _apply_token_conditions(stmt, tokens, spec)


def _apply_token_conditions(
    stmt: Select[Any],
    tokens: list[str],
    spec: SearchSpec,
) -> Select[Any]:
    """Apply AND-combined token conditions to the statement.

    Args:
        stmt: The Select statement.
        tokens: Normalized search tokens.
        spec: Search specification.

    Returns:
        Statement with all token conditions applied.
    """
    from sqlalchemy import and_

    conditions = [_token_condition(stmt, token, spec) for token in tokens]
    return stmt.where(and_(*conditions))


def _token_condition(
    stmt: Select[Any],
    token: str,
    spec: SearchSpec,
) -> Any:
    """Build an OR condition matching one token across all fields.

    Args:
        stmt: The Select statement for column resolution.
        token: A single normalized search token.
        spec: Search specification with fields and mode.

    Returns:
        OR-combined condition across all fields.
    """
    from sqlalchemy import or_

    field_conds = [_field_match(stmt, field, token, spec.mode) for field in spec.fields]
    return or_(*field_conds)


def _field_match(
    stmt: Select[Any],
    field: str,
    token: str,
    mode: SearchFieldMode,
) -> Any:
    """Build an ILIKE condition for one field and token.

    Args:
        stmt: The Select statement for column resolution.
        field: The field name to search.
        token: The search token.
        mode: The matching mode (PREFIX, CONTAINS, EXACT).

    Returns:
        A SQLAlchemy ILIKE expression.
    """
    column = resolve_column(stmt, field)
    pattern = _build_pattern(token, mode)
    return column.ilike(pattern)


def _build_pattern(token: str, mode: SearchFieldMode) -> str:
    """Build an ILIKE pattern string from token and mode.

    Args:
        token: The search token.
        mode: The matching mode.

    Returns:
        Pattern string with appropriate wildcards.
    """
    if mode is SearchFieldMode.PREFIX:
        return f"{token}%"
    if mode is SearchFieldMode.EXACT:
        return token
    return f"%{token}%"


__all__ = ["SQLAlchemySearchBackend"]
