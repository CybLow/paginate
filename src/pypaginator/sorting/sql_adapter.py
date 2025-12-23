"""SQL adapter for sorting operations.

This module provides SQL-specific sorting capabilities that complement
the in-memory sorting engine.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import asc, desc, nulls_first, nulls_last


if TYPE_CHECKING:
    from typing import Any

    from sqlalchemy.orm import InstrumentedAttribute
    from sqlalchemy.sql.elements import UnaryExpression


class SqlSortAdapter:
    """Build SQLAlchemy ORDER BY clauses from sort specifications.

    This adapter translates high-level sort specifications into
    SQLAlchemy order by expressions with proper null handling.
    """

    @staticmethod
    def build_order_expression(
        column: InstrumentedAttribute[Any],
        descending: bool = False,
        nulls_position: str | None = None,
    ) -> UnaryExpression[Any]:
        """Build a SQLAlchemy ORDER BY expression.

        Args:
            column: SQLAlchemy column to sort by
            descending: Whether to sort in descending order
            nulls_position: Where to place NULL values ("first" or "last")

        Returns:
            SQLAlchemy order by expression
        """
        # Apply ascending or descending
        order_expr = desc(column) if descending else asc(column)

        # Apply null positioning if specified
        if nulls_position == "first":
            order_expr = nulls_first(order_expr)
        elif nulls_position == "last":
            order_expr = nulls_last(order_expr)

        return order_expr


__all__ = ["SqlSortAdapter"]
