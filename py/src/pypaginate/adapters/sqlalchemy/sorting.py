"""Translate sort specs into SQLAlchemy ORDER BY clauses.

Maps each ``SortSpec`` to a directed column expression with null placement,
applying ``.asc()`` / ``.desc()`` and ``.nulls_first()`` / ``.nulls_last()``.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pypaginate.adapters.sqlalchemy.columns import resolve_column
from pypaginate.specs import SortSpec


def build_order_by(model: type, sorting: Sequence[SortSpec]) -> list[Any]:
    """Translate ``sorting`` into an ordered list of ORDER BY clauses.

    Args:
        model: The declarative ORM model the fields belong to.
        sorting: Sort specifications, applied in order.

    Returns:
        A list of SQLAlchemy order expressions for ``Select.order_by``.
    """
    return [_order_clause(model, spec) for spec in sorting]


def _order_clause(model: type, spec: SortSpec) -> Any:
    """Build one directed, null-placed ORDER BY clause from a ``SortSpec``."""
    column = resolve_column(model, spec.field)
    directed = column.desc() if spec.direction == "desc" else column.asc()
    if (spec.nulls or "last") == "first":
        return directed.nulls_first()
    return directed.nulls_last()


__all__ = ["build_order_by"]
