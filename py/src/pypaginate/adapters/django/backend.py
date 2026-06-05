"""Offset pagination backend for Django QuerySets.

Implements ``SyncPaginationBackend[T]``: counts via ``QuerySet.count()`` and
fetches a page via slicing (``qs[offset:offset + limit]``), which Django renders
to ``LIMIT``/``OFFSET``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from django.db.models import QuerySet


class DjangoBackend(Generic[ItemT]):
    """Sync offset pagination backend for Django QuerySets."""

    __slots__ = ()

    def count(self, query: object) -> int:
        """Count rows matching the QuerySet."""
        qs: QuerySet[ItemT] = query  # type: ignore[assignment]
        return int(qs.count())

    def fetch(self, query: object, offset: int, limit: int) -> list[ItemT]:
        """Fetch a page slice via ``LIMIT``/``OFFSET``."""
        qs: QuerySet[ItemT] = query  # type: ignore[assignment]
        return list(qs[offset : offset + limit])


__all__ = ["DjangoBackend"]
