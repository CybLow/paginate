"""Keyset (cursor) WHERE-clause builder.

Renders the lexicographic comparison for keyset pagination directly from a
query's ORDER BY columns. The core owns the *structure* of the predicate
(OR-of-AND terms via :func:`keyset_terms`); this adapter only renders each
``column OP value`` comparison and combines them with SQLAlchemy ``and_``/``or_``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import and_, or_
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.operators import desc_op

from pypaginate._core import keyset_terms
from pypaginate.errors import ConfigurationError


if TYPE_CHECKING:
    from sqlalchemy.sql import Select
    from sqlalchemy.sql.elements import ColumnElement


class OrderColumn:
    """A parsed ORDER BY column with its sort direction."""

    __slots__ = ("element", "is_ascending")

    def __init__(self, element: ColumnElement[Any], *, is_ascending: bool) -> None:
        self.element = element
        self.is_ascending = is_ascending

    @property
    def reversed(self) -> OrderColumn:
        """Return a copy with the sort direction flipped."""
        return OrderColumn(self.element, is_ascending=not self.is_ascending)

    @property
    def order_clause(self) -> Any:
        """Return the ``.asc()`` / ``.desc()`` expression for ORDER BY."""
        return self.element.asc() if self.is_ascending else self.element.desc()


def extract_order_columns(query: Select[Any]) -> list[OrderColumn]:
    """Parse a Select's ORDER BY clause into ``OrderColumn`` objects.

    Unwraps ``asc()`` / ``desc()`` wrappers; bare columns default to ascending.

    Args:
        query: A SQLAlchemy Select carrying an ORDER BY clause.

    Returns:
        The ordered list of parsed ORDER BY columns.

    Raises:
        ConfigurationError: If the query has no ORDER BY clause.
    """
    clauses = cast("Any", query)._order_by_clauses
    if not clauses:
        msg = "query has no ORDER BY clause for keyset pagination"
        raise ConfigurationError(msg)
    return [_parse_clause(clause) for clause in clauses]


def build_keyset_condition(columns: list[OrderColumn], values: tuple[Any, ...]) -> Any:
    """Build the keyset WHERE expression for ``columns`` past ``values``.

    For ``ORDER BY (a ASC, b DESC)`` with cursor ``(v1, v2)`` this renders
    ``(a > v1) OR (a = v1 AND b < v2)``.

    Args:
        columns: The parsed (direction-aware) ORDER BY columns.
        values: The cursor values, one per column.

    Returns:
        A SQLAlchemy boolean expression.

    Raises:
        ConfigurationError: If the column / value counts disagree or are empty.
    """
    _validate(columns, values)
    terms = keyset_terms([col.is_ascending for col in columns])
    return or_(*(_render_term(columns, values, term) for term in terms))


def _render_term(
    columns: list[OrderColumn], values: tuple[Any, ...], term: list[tuple[int, str]]
) -> Any:
    """AND one keyset term's ``column OP value`` comparisons together."""
    return and_(*(_compare(columns[i].element, op, values[i]) for i, op in term))


def _compare(column: ColumnElement[Any], op: str, value: Any) -> Any:
    """Render a single ``column OP value`` comparison (``gt`` / ``lt`` / ``eq``)."""
    if op == "gt":
        return column > value
    if op == "lt":
        return column < value
    return column == value


def _parse_clause(clause: Any) -> OrderColumn:
    """Parse one ORDER BY clause into an ``OrderColumn``."""
    if isinstance(clause, UnaryExpression) and hasattr(clause, "modifier"):
        return OrderColumn(clause.element, is_ascending=clause.modifier is not desc_op)
    return OrderColumn(clause, is_ascending=True)


def _validate(columns: list[OrderColumn], values: tuple[Any, ...]) -> None:
    """Validate that the column and cursor-value counts match and are non-empty."""
    if not columns:
        msg = "no ORDER BY columns for keyset condition"
        raise ConfigurationError(msg)
    if len(columns) != len(values):
        msg = f"column count ({len(columns)}) does not match cursor value count ({len(values)})"
        raise ConfigurationError(msg)


__all__ = ["OrderColumn", "build_keyset_condition", "extract_order_columns"]
