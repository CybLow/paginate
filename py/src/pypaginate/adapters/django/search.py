"""Django search backend: match-filter ``SearchSpec`` across fields.

Keeps rows where **any** field matches the query, via a case-insensitive lookup
per ``spec.mode`` (contains / prefix / exact). This is a match-filter (unranked)
— ranking lives in the in-memory engine, not the database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.domain.enums import SearchFieldMode


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from pypaginate.domain.specs import SearchSpec


_MODE_LOOKUP = {
    SearchFieldMode.PREFIX: "__istartswith",
    SearchFieldMode.EXACT: "__iexact",
    SearchFieldMode.CONTAINS: "__icontains",
}


def _any_field_q(query: str, fields: tuple[str, ...], lookup: str) -> Any:
    """OR a ``field <lookup> query`` clause across every field."""
    from django.db.models import Q

    combined: Any | None = None
    for field in fields:
        clause = Q(**{f"{field}{lookup}": query})
        combined = clause if combined is None else combined | clause
    return combined


class DjangoSearchBackend:
    """Translate a ``SearchSpec`` to a ``QuerySet.filter`` match-filter."""

    __slots__ = ()

    @staticmethod
    def apply_search(query: object, spec: SearchSpec) -> object:
        """Apply a match-filter search to a Django QuerySet."""
        qs: QuerySet[Any] = query  # type: ignore[assignment]
        if not spec.query or not spec.fields:
            return qs
        lookup = _MODE_LOOKUP.get(spec.mode, "__icontains")
        condition = _any_field_q(spec.query, spec.fields, lookup)
        return qs.filter(condition) if condition is not None else qs


__all__ = ["DjangoSearchBackend"]
