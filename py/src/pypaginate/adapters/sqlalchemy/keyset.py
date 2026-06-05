"""Keyset pagination WHERE clause builder.

Constructs the lexicographic comparison needed for cursor/keyset
pagination directly from SQLAlchemy column expressions.
No external dependencies -- pure SQLAlchemy 2.0 API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, or_
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.operators import desc_op

from pypaginate._core import keyset_terms
from pypaginate.domain.exceptions import ConfigurationError


if TYPE_CHECKING:
    from sqlalchemy.sql import Select
    from sqlalchemy.sql.elements import ColumnElement


class OrderColumn:
    """Parsed ORDER BY column with direction metadata."""

    __slots__ = ("element", "is_ascending")

    def __init__(
        self,
        element: ColumnElement[Any],
        *,
        is_ascending: bool,
    ) -> None:
        self.element = element
        self.is_ascending = is_ascending

    @property
    def reversed(self) -> OrderColumn:
        """Return a copy with flipped direction."""
        return OrderColumn(self.element, is_ascending=not self.is_ascending)

    @property
    def order_clause(self) -> Any:
        """Return the SQLAlchemy asc/desc expression for ORDER BY."""
        if self.is_ascending:
            return self.element.asc()
        return self.element.desc()


def extract_order_columns(query: Select[Any]) -> list[OrderColumn]:
    """Extract ORDER BY columns from a Select statement.

    Unwraps ``UnaryExpression`` (asc/desc wrappers) to get the bare
    column element and its sort direction.  Bare columns (no explicit
    direction) default to ascending.

    Args:
        query: A SQLAlchemy Select with an ORDER BY clause.

    Returns:
        Ordered list of ``OrderColumn`` objects.

    Raises:
        ConfigurationError: If the query has no ORDER BY clause.
    """
    clauses = query._order_by_clauses
    if not clauses:
        msg = "Query has no ORDER BY clause for keyset pagination"
        raise ConfigurationError(msg)
    return [_parse_clause(clause) for clause in clauses]


def build_keyset_condition(
    columns: list[OrderColumn],
    cursor_values: tuple[Any, ...],
) -> Any:
    """Build the WHERE clause for keyset pagination.

    For ``ORDER BY (a ASC, b DESC)`` with cursor ``(v1, v2)``::

        WHERE (a > v1) OR (a = v1 AND b < v2)

    Uses the conjunction-at-top-level form for optimizer friendliness.

    Args:
        columns: Parsed ORDER BY columns.
        cursor_values: Tuple of values matching each column.

    Returns:
        A SQLAlchemy boolean expression.

    Raises:
        ConfigurationError: If columns/values count mismatch.
    """
    _validate_inputs(columns, cursor_values)
    # The core owns the lexicographic *structure* (OR-of-AND terms); this adapter
    # only renders each `column OP value` and combines with SQLAlchemy and_/or_.
    ascending = [col.is_ascending for col in columns]
    terms = keyset_terms(ascending)
    return or_(*(_render_term(columns, cursor_values, term) for term in terms))


# -- Private helpers ---------------------------------------------------------


def _render_term(
    columns: list[OrderColumn],
    values: tuple[Any, ...],
    term: list[tuple[int, str]],
) -> Any:
    """AND the comparisons of one keyset term into a SQLAlchemy expression."""
    return and_(*(_render_compare(columns[i].element, op, values[i]) for i, op in term))


def _render_compare(col: ColumnElement[Any], op: str, value: Any) -> Any:
    """Render a single `column OP value` comparison (`gt` / `lt` / `eq`)."""
    if op == "gt":
        return col > value
    if op == "lt":
        return col < value
    return col == value


def _parse_clause(clause: Any) -> OrderColumn:
    """Parse a single ORDER BY clause into an OrderColumn.

    Args:
        clause: A ``UnaryExpression`` (asc/desc) or bare column.

    Returns:
        An ``OrderColumn`` with element and direction.
    """
    if isinstance(clause, UnaryExpression) and hasattr(clause, "modifier"):
        is_ascending = clause.modifier is not desc_op
        return OrderColumn(clause.element, is_ascending=is_ascending)
    return OrderColumn(clause, is_ascending=True)


def _validate_inputs(
    columns: list[OrderColumn],
    cursor_values: tuple[Any, ...],
) -> None:
    """Validate that column count matches cursor value count.

    Args:
        columns: Parsed ORDER BY columns.
        cursor_values: Cursor values to match.

    Raises:
        ConfigurationError: On count mismatch or empty inputs.
    """
    if not columns:
        msg = "No ORDER BY columns for keyset condition"
        raise ConfigurationError(msg)
    if len(columns) != len(cursor_values):
        msg = (
            f"Column count ({len(columns)}) does not match "
            f"cursor value count ({len(cursor_values)})"
        )
        raise ConfigurationError(msg)


__all__ = [
    "OrderColumn",
    "build_keyset_condition",
    "extract_order_columns",
]
