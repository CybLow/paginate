"""Translate sort specs to Django ``order_by`` arguments.

Without null placement a key renders to a plain ``"field"`` / ``"-field"``
string; with ``nulls`` set it renders to an ``F(field).asc(nulls_last=...)`` /
``.desc(nulls_first=...)`` expression (Django emulates ``NULLS FIRST/LAST`` on
backends lacking native support).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.specs import SortSpec


def _nulls_arg(spec: SortSpec) -> Any:
    """Null-aware ordering expression for one sort key."""
    from django.db.models import F

    column = F(spec.field)
    nulls = {"nulls_first": True} if spec.nulls == "first" else {"nulls_last": True}
    if spec.direction == "desc":
        return column.desc(**nulls)
    return column.asc(**nulls)


def _order_arg(spec: SortSpec) -> Any:
    """Render one sort key to a string (no nulls) or an ``F`` expression."""
    if spec.nulls is None:
        return f"-{spec.field}" if spec.direction == "desc" else spec.field
    return _nulls_arg(spec)


def build_order_by(sorting: Sequence[SortSpec]) -> list[Any]:
    """Render sort specs to a list of ``order_by`` arguments."""
    return [_order_arg(spec) for spec in sorting]


def apply_sorting(queryset: Any, sorting: Sequence[SortSpec]) -> Any:
    """Apply ordered sort specs to a QuerySet (no-op when empty)."""
    if not sorting:
        return queryset
    return queryset.order_by(*build_order_by(sorting))


__all__ = ["apply_sorting", "build_order_by"]
