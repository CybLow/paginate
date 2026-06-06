"""Small assertion helpers shared across the test lanes."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _id_of(item: Any) -> Any:
    """The ``id`` of a row, whether it is a mapping or an attribute object."""
    if isinstance(item, dict):
        return item["id"]
    return item.id


def ids_of(items: Iterable[Any]) -> list[Any]:
    """The ``id`` values of every row in a page (or any iterable of rows)."""
    return [_id_of(item) for item in items]


def names_of(items: Iterable[Any]) -> list[Any]:
    """The ``name`` values of every row in a page (or any iterable of rows)."""
    return [item["name"] if isinstance(item, dict) else item.name for item in items]


__all__ = ["ids_of", "names_of"]
