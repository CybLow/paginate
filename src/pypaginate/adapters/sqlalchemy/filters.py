"""SQLAlchemy filter backend translating FilterSpec to WHERE clauses.

Maps each FilterOperator to a SQLAlchemy column expression builder.
Supports AND/OR logic via ``FilterLogic``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.adapters.sqlalchemy.columns import resolve_column
from pypaginate.domain.enums import FilterLogic
from pypaginate.domain.exceptions import FilterError


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from sqlalchemy.sql import Select

    from pypaginate.domain.specs import FilterSpec

    OperatorFn = Callable[[Any, Any], Any]


def _build_operator_map() -> dict[str, OperatorFn]:
    """Build mapping from operator names to column expression builders.

    Returns:
        Dict mapping operator string to a callable(column, value).
    """
    return {
        "eq": lambda col, val: col == val,
        "ne": lambda col, val: col != val,
        "gt": lambda col, val: col > val,
        "gte": lambda col, val: col >= val,
        "lt": lambda col, val: col < val,
        "lte": lambda col, val: col <= val,
        "in": lambda col, val: col.in_(val),
        "not_in": lambda col, val: col.not_in(val),
        "contains": lambda col, val: col.contains(val),
        "starts_with": lambda col, val: col.startswith(val),
        "ends_with": lambda col, val: col.endswith(val),
        "like": lambda col, val: col.like(val),
        "ilike": lambda col, val: col.ilike(val),
        "between": _apply_between,
        "is_null": _apply_is_null,
        "is_not_null": _apply_is_not_null,
        "regex": lambda col, val: col.regexp_match(val),
    }


def _apply_between(column: Any, value: Any) -> Any:
    """Apply BETWEEN with a two-element sequence."""
    try:
        low, high = value[0], value[1]
    except (TypeError, IndexError, KeyError) as exc:
        raise FilterError(
            "BETWEEN requires a two-element sequence",
            details={"value": repr(value)},
        ) from exc
    return column.between(low, high)


def _apply_is_null(column: Any, _value: Any) -> Any:
    """Apply IS NULL check."""
    return column.is_(None)


def _apply_is_not_null(column: Any, _value: Any) -> Any:
    """Apply IS NOT NULL check."""
    return column.is_not(None)


class SQLAlchemyFilterBackend:
    """Translates FilterSpec to SQLAlchemy WHERE clauses.

    Satisfies ``FilterBackend`` protocol.
    """

    def __init__(self) -> None:
        self._operators = _build_operator_map()

    def apply_filters(
        self,
        query: object,
        filters: Sequence[FilterSpec],
    ) -> object:
        """Apply filter specs to a SQLAlchemy Select.

        Args:
            query: A SQLAlchemy Select statement.
            filters: Filter specifications to apply.

        Returns:
            Modified Select with WHERE clauses.
        """
        stmt: Select[Any] = query  # type: ignore[assignment]
        and_conditions, or_conditions = _partition_filters(
            stmt,
            filters,
            self._operators,
        )
        return _apply_conditions(stmt, and_conditions, or_conditions)


def _partition_filters(
    stmt: Select[Any],
    filters: Sequence[FilterSpec],
    operators: dict[str, OperatorFn],
) -> tuple[list[Any], list[Any]]:
    """Split filters into AND and OR condition lists.

    Args:
        stmt: The Select statement for column resolution.
        filters: Filter specifications.
        operators: Operator function mapping.

    Returns:
        Tuple of (and_conditions, or_conditions).
    """
    and_conds: list[Any] = []
    or_conds: list[Any] = []
    for spec in filters:
        condition = _build_condition(stmt, spec, operators)
        if spec.logic is FilterLogic.OR:
            or_conds.append(condition)
        else:
            and_conds.append(condition)
    return and_conds, or_conds


def _build_condition(
    stmt: Select[Any],
    spec: FilterSpec,
    operators: dict[str, OperatorFn],
) -> Any:
    """Build a single SQLAlchemy condition from a FilterSpec.

    Args:
        stmt: The Select statement for column resolution.
        spec: A single filter specification.
        operators: Operator function mapping.

    Returns:
        A SQLAlchemy column expression.

    Raises:
        FilterError: If the operator is unsupported.
    """
    column = resolve_column(stmt, spec.field)
    operator_fn = operators.get(spec.operator)
    if operator_fn is None:
        msg = f"Unsupported filter operator: '{spec.operator}'"
        raise FilterError(
            msg,
            field=spec.field,
            details={"operator": spec.operator, "supported": list(operators)},
        )
    return operator_fn(column, spec.value)


def _apply_conditions(
    stmt: Select[Any],
    and_conditions: list[Any],
    or_conditions: list[Any],
) -> Select[Any]:
    """Combine AND/OR conditions and apply to the statement.

    Args:
        stmt: The Select statement.
        and_conditions: Conditions joined with AND.
        or_conditions: Conditions joined with OR.

    Returns:
        Modified Select with WHERE clauses applied.
    """
    from sqlalchemy import and_, or_

    clauses: list[Any] = []
    if and_conditions:
        clauses.append(and_(*and_conditions))
    if or_conditions:
        clauses.append(or_(*or_conditions))
    if not clauses:
        return stmt
    return stmt.where(and_(*clauses))


__all__ = ["SQLAlchemyFilterBackend"]
