"""Translate filter specs into SQLAlchemy boolean expressions.

Maps each ``FilterSpec.operator`` wire-string to a column-expression builder and
combines specs either as a flat list (each spec carries its own AND/OR ``logic``)
or as a nested :class:`~pypaginate.specs.FilterGroup` (recursing with and_/or_).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from sqlalchemy import and_, or_, true

from pypaginate.adapters.sqlalchemy.columns import resolve_column
from pypaginate.errors import FilterError
from pypaginate.specs import FilterGroup, FilterNode, FilterSpec


OperatorFn = Callable[[Any, Any], Any]


def _between(column: Any, value: Any) -> Any:
    """Render ``column BETWEEN value[0] AND value[1]``."""
    try:
        low, high = value[0], value[1]
    except (TypeError, IndexError, KeyError) as exc:
        msg = "between requires a two-element sequence"
        raise FilterError(msg, details={"value": repr(value)}) from exc
    return column.between(low, high)


def _build_operator_map() -> dict[str, OperatorFn]:
    """Build the wire-operator -> column-expression builder table."""
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
        "between": _between,
        "is_null": lambda col, _val: col.is_(None),
        "is_not_null": lambda col, _val: col.is_not(None),
        "regex": lambda col, val: col.regexp_match(val),
        "empty": lambda col, _val: or_(col.is_(None), col == ""),
        "not_empty": lambda col, _val: and_(col.is_not(None), col != ""),
        "exists": lambda _col, _val: true(),
    }


_OPERATORS: dict[str, OperatorFn] = _build_operator_map()


def _condition(model: type, spec: FilterSpec) -> Any:
    """Render a single ``FilterSpec`` as a column expression."""
    operator_fn = _OPERATORS.get(spec.operator)
    if operator_fn is None:
        msg = f"unsupported filter operator: '{spec.operator}'"
        raise FilterError(msg, field=spec.field, details={"supported": list(_OPERATORS)})
    return operator_fn(resolve_column(model, spec.field), spec.value)


def build_filter(model: type, filters: Sequence[FilterSpec]) -> Any | None:
    """Combine flat ``filters`` into one boolean expression (``None`` if empty).

    Each spec's ``logic`` selects its group: AND-specs are conjoined, OR-specs are
    disjoined, and the two groups are then conjoined — ``(a AND b) AND (c OR d)``.

    Args:
        model: The declarative ORM model the fields belong to.
        filters: Flat filter specifications to translate.

    Returns:
        A SQLAlchemy boolean expression, or ``None`` when ``filters`` is empty.
    """
    and_conds: list[Any] = []
    or_conds: list[Any] = []
    for spec in filters:
        target = or_conds if (spec.logic or "and") == "or" else and_conds
        target.append(_condition(model, spec))
    return _combine(and_conds, or_conds)


def _combine(and_conds: list[Any], or_conds: list[Any]) -> Any | None:
    """Fold the partitioned AND / OR condition lists into one expression."""
    clauses: list[Any] = []
    if and_conds:
        clauses.append(and_(*and_conds))
    if or_conds:
        clauses.append(or_(*or_conds))
    if not clauses:
        return None
    return and_(*clauses)


def build_filter_group(model: type, group: FilterGroup) -> Any:
    """Translate a nested ``And`` / ``Or`` group into a boolean expression.

    Args:
        model: The declarative ORM model the fields belong to.
        group: A (possibly nested) filter group.

    Returns:
        A SQLAlchemy boolean expression combining every child condition.
    """
    return _node(model, group)


def _node(model: type, node: FilterNode) -> Any:
    """Recurse a spec / group tree into a combined boolean expression."""
    if isinstance(node, FilterGroup):
        children = [_node(model, child) for child in node.conditions]
        combine = or_ if node.logic == "or" else and_
        return combine(*children)
    return _condition(model, node)


__all__ = ["build_filter", "build_filter_group"]
