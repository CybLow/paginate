"""Match-filter a QuerySet by a search spec across fields.

Keeps rows where *any* field matches the query via a case-insensitive lookup
per ``spec.mode`` (contains / prefix / exact). This is an unranked match-filter;
relevance ranking lives in the in-memory engine, not the database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from pypaginate.specs import SearchSpec


_MODE_LOOKUP: dict[str, str] = {
    "prefix": "__istartswith",
    "exact": "__iexact",
    "contains": "__icontains",
}


def build_search_q(spec: SearchSpec) -> Any:
    """Build an OR-of-fields case-insensitive match ``Q`` (``None`` when empty)."""
    from django.db.models import Q

    if not spec.query or not spec.fields:
        return None
    lookup = _MODE_LOOKUP.get(spec.mode or "contains", "__icontains")
    combined: Any = None
    for field in spec.fields:
        clause = Q(**{f"{field}{lookup}": spec.query})
        combined = clause if combined is None else combined | clause
    return combined


def apply_search(queryset: Any, spec: SearchSpec) -> Any:
    """Apply a match-filter search to a QuerySet (no-op when empty)."""
    condition = build_search_q(spec)
    if condition is None:
        return queryset
    return queryset.filter(condition)


__all__ = ["apply_search", "build_search_q"]
