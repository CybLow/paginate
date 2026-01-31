"""SQL adapter for filter operations.

Provides SQL-specific filtering capabilities for repositories.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, or_


if TYPE_CHECKING:
    from sqlalchemy.orm import InstrumentedAttribute
    from sqlalchemy.sql.elements import ColumnElement


class SqlFilterAdapter:
    """Build SQLAlchemy filter conditions from operator specifications."""

    @staticmethod
    def build_condition(
        column: InstrumentedAttribute[Any],
        operator: str,
        value: object,
    ) -> ColumnElement[bool]:
        """Build a SQLAlchemy filter condition."""
        match operator:
            case "eq" | "equals":
                return column == value
            case "ne" | "not_equals":
                return column != value
            case "gt" | "greater_than":
                return column > value
            case "gte" | "greater_than_or_equal":
                return column >= value
            case "lt" | "less_than":
                return column < value
            case "lte" | "less_than_or_equal":
                return column <= value
            case "in":
                return (
                    column.in_(value) if isinstance(value, (list, tuple, set)) else column == value
                )
            case "not_in":
                return (
                    ~column.in_(value) if isinstance(value, (list, tuple, set)) else column != value
                )
            case "like":
                return column.like(str(value))
            case "ilike":
                return column.ilike(str(value))
            case "is_null":
                return column.is_(None) if value else column.is_not(None)
            case "contains":
                return column.contains(value)
            case "startswith":
                return column.startswith(value)
            case "endswith":
                return column.endswith(value)
            case _:
                raise ValueError(f"Unsupported filter operator: {operator}")

    @staticmethod
    def combine_conditions(
        conditions: list[ColumnElement[bool]],
        logic: str = "and",
    ) -> ColumnElement[bool]:
        """Combine multiple conditions with AND or OR logic."""
        if not conditions:
            raise ValueError("Cannot combine empty list of conditions")

        if len(conditions) == 1:
            return conditions[0]

        return and_(*conditions) if logic == "and" else or_(*conditions)


__all__ = ["SqlFilterAdapter"]
