"""Django sort backend: translate ``SortSpec`` to ``QuerySet.order_by``.

Null placement is honored via ``F(field).asc(nulls_last=...)`` /
``.desc(nulls_first=...)`` (Django emulates ``NULLS FIRST/LAST`` on backends
that lack native support).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.domain.enums import NullsPosition, SortDirection


if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import QuerySet

    from pypaginate.domain.specs import SortSpec


def _order_expr(spec: SortSpec) -> Any:
    """Build a null-aware Django ordering expression for one sort key."""
    from django.db.models import F

    column = F(spec.field)
    nulls = {"nulls_first": True} if spec.nulls is NullsPosition.FIRST else {"nulls_last": True}
    if spec.direction is SortDirection.DESC:
        return column.desc(**nulls)
    return column.asc(**nulls)


class DjangoSortBackend:
    """Translate ``SortSpec`` lists to ``QuerySet.order_by(...)``."""

    __slots__ = ()

    @staticmethod
    def apply_sorting(query: object, sorting: Sequence[SortSpec]) -> object:
        """Apply ordered sort specs to a Django QuerySet."""
        qs: QuerySet[Any] = query  # type: ignore[assignment]
        if not sorting:
            return qs
        return qs.order_by(*(_order_expr(spec) for spec in sorting))


__all__ = ["DjangoSortBackend"]
