"""Django filter backend: translate ``FilterSpec`` to ``Q`` objects.

Maps each filter operator to a Django field lookup. As with the SQLAlchemy
adapter, this covers the SQL-mappable operator set; the in-memory-only
``empty`` / ``not_empty`` / ``exists`` operators are not supported here (they
raise ``FilterError``). ``like`` / ``ilike`` map to (case-insensitive) substring
lookups — SQL ``LIKE`` wildcard metacharacters are not interpreted.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.domain.enums import FilterLogic
from pypaginate.domain.exceptions import FilterError


if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import QuerySet

    from pypaginate.domain.specs import FilterSpec


# operator -> (lookup suffix, negate). Operators needing custom values
# (between / is_null / is_not_null) are handled separately in ``_to_q``.
_LOOKUPS: dict[str, tuple[str, bool]] = {
    "eq": ("", False),
    "ne": ("", True),
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


def _to_q(spec: FilterSpec) -> Any:
    """Translate one ``FilterSpec`` to a Django ``Q`` object."""
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


def _combine(specs: Sequence[FilterSpec]) -> Any:
    """Combine specs into one ``Q``: AND the ``AND`` specs with the OR group."""
    from django.db.models import Q

    and_q: Any = Q()
    or_q: Any | None = None
    for spec in specs:
        condition = _to_q(spec)
        if spec.logic is FilterLogic.OR:
            or_q = condition if or_q is None else or_q | condition
        else:
            and_q &= condition
    return and_q if or_q is None else and_q & or_q


class DjangoFilterBackend:
    """Translate ``FilterSpec`` lists to ``QuerySet.filter(Q(...))``."""

    __slots__ = ()

    @staticmethod
    def apply_filters(query: object, filters: Sequence[FilterSpec]) -> object:
        """Apply filter specs to a Django QuerySet."""
        qs: QuerySet[Any] = query  # type: ignore[assignment]
        if not filters:
            return qs
        return qs.filter(_combine(filters))


__all__ = ["DjangoFilterBackend"]
