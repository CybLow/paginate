"""Translate filter specs/groups to Django ``Q`` objects.

Each operator maps to a Django field lookup. The in-memory-only ``empty`` /
``not_empty`` / ``exists`` operators have no SQL equivalent and raise
:class:`~pypaginate.errors.FilterError`. ``like`` / ``ilike`` map to
(case-insensitive) substring lookups; SQL ``LIKE`` wildcards are not interpreted.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.errors import FilterError
from pypaginate.specs import FilterGroup, FilterSpec


if TYPE_CHECKING:
    from collections.abc import Sequence


# operator -> (lookup suffix, negate). ``between`` / ``is_null`` / ``is_not_null``
# need custom values and are handled separately in ``_spec_to_q``.
_LOOKUPS: dict[str, tuple[str, bool]] = {
    "eq": ("__exact", False),
    "ne": ("__exact", True),
    "gt": ("__gt", False),
    "gte": ("__gte", False),
    "lt": ("__lt", False),
    "lte": ("__lte", False),
    "in": ("__in", False),
    "not_in": ("__in", True),
    "contains": ("__contains", False),
    "starts_with": ("__startswith", False),
    "ends_with": ("__endswith", False),
    "like": ("__contains", False),
    "ilike": ("__icontains", False),
    "regex": ("__regex", False),
}


def _between_q(field: str, value: Any) -> Any:
    """``field BETWEEN low AND high`` from a two-element sequence."""
    from django.db.models import Q

    try:
        low, high = value[0], value[1]
    except (TypeError, IndexError, KeyError) as exc:
        raise FilterError("BETWEEN requires a two-element sequence", field=field) from exc
    return Q(**{f"{field}__range": (low, high)})


def _spec_to_q(spec: FilterSpec) -> Any:
    """Translate one ``FilterSpec`` into a Django ``Q`` object."""
    from django.db.models import Q

    field, operator, value = spec.field, spec.operator, spec.value
    if operator == "between":
        return _between_q(field, value)
    if operator in ("is_null", "is_not_null"):
        return Q(**{f"{field}__isnull": operator == "is_null"})
    entry = _LOOKUPS.get(operator)
    if entry is None:
        msg = f"Unsupported filter operator: '{operator}'"
        raise FilterError(msg, field=field, details={"operator": operator})
    suffix, negate = entry
    condition = Q(**{f"{field}{suffix}": value})
    return ~condition if negate else condition


def _node_to_q(node: FilterSpec | FilterGroup) -> Any:
    """Dispatch a tree node to the group or leaf translator."""
    if isinstance(node, FilterGroup):
        return _group_to_q(node)
    return _spec_to_q(node)


def _group_to_q(group: FilterGroup) -> Any:
    """Recursively combine a nested AND/OR group into one ``Q``."""
    from django.db.models import Q

    combined: Any = None
    for child in group.conditions:
        clause = _node_to_q(child)
        if combined is None:
            combined = clause
        elif group.logic == "or":
            combined = combined | clause
        else:
            combined = combined & clause
    return combined if combined is not None else Q()


def _combine_flat(specs: Sequence[FilterSpec]) -> Any:
    """Combine flat specs: AND the ``and`` specs with the ``or`` group."""
    from django.db.models import Q

    and_q: Any = Q()
    or_q: Any = None
    for spec in specs:
        condition = _spec_to_q(spec)
        if spec.logic == "or":
            or_q = condition if or_q is None else or_q | condition
        else:
            and_q &= condition
    return and_q if or_q is None else and_q & or_q


def build_filter_q(filters: Sequence[FilterSpec] | FilterGroup) -> Any:
    """Build a Django ``Q`` from a flat spec list or a nested AND/OR group."""
    if isinstance(filters, FilterGroup):
        return _group_to_q(filters)
    return _combine_flat(filters)


def apply_filters(queryset: Any, filters: Sequence[FilterSpec] | FilterGroup) -> Any:
    """Apply filter specs/group to a QuerySet (no-op when empty)."""
    if not isinstance(filters, FilterGroup) and not filters:
        return queryset
    return queryset.filter(build_filter_q(filters))


__all__ = ["apply_filters", "build_filter_q"]
