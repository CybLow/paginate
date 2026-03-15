"""SQLAlchemy sort backend translating SortSpec to ORDER BY clauses.

Maps SortDirection and NullsPosition to SQLAlchemy column modifiers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.adapters.sqlalchemy.columns import resolve_column
from pypaginate.domain.enums import NullsPosition, SortDirection


if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.sql import Select

    from pypaginate.domain.specs import SortSpec


class SQLAlchemySortBackend:
    """Translates SortSpec to SQLAlchemy ORDER BY clauses.

    Satisfies ``SortBackend`` protocol.
    """

    def apply_sorting(
        self,
        query: object,
        sorting: Sequence[SortSpec],
    ) -> object:
        """Apply sort specs to a SQLAlchemy Select.

        Args:
            query: A SQLAlchemy Select statement.
            sorting: Sort specifications (applied in order).

        Returns:
            Modified Select with ORDER BY clauses.
        """
        stmt: Select[Any] = query  # type: ignore[assignment]
        clauses = [_build_order_clause(stmt, spec) for spec in sorting]
        if not clauses:
            return stmt
        return stmt.order_by(*clauses)


def _build_order_clause(stmt: Select[Any], spec: SortSpec) -> Any:
    """Build an ORDER BY clause from a single SortSpec.

    Args:
        stmt: The Select statement for column resolution.
        spec: A sort specification.

    Returns:
        A SQLAlchemy order expression with direction and nulls.
    """
    column = resolve_column(stmt, spec.field)
    directed = _apply_direction(column, spec.direction)
    return _apply_nulls(directed, spec.nulls)


def _apply_direction(column: Any, direction: SortDirection) -> Any:
    """Apply ASC or DESC to a column.

    Args:
        column: The resolved column attribute.
        direction: Sort direction enum.

    Returns:
        Column with .asc() or .desc() applied.
    """
    if direction is SortDirection.DESC:
        return column.desc()
    return column.asc()


def _apply_nulls(clause: Any, nulls: NullsPosition) -> Any:
    """Apply nulls_first() or nulls_last() to an order clause.

    Args:
        clause: A directed column expression.
        nulls: Null positioning enum.

    Returns:
        Clause with nulls positioning applied.
    """
    if nulls is NullsPosition.FIRST:
        return clause.nulls_first()
    return clause.nulls_last()


__all__ = ["SQLAlchemySortBackend"]
