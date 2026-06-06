"""Result pages — generic containers that hold your rows untouched.

A page wraps the matched ``items`` (your own objects/ORM rows, never coerced or
validated) plus pagination metadata, so there is zero per-row cost.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class OffsetPage(Generic[T]):
    """An offset page: the matched ``items`` plus offset metadata."""

    items: Sequence[T]
    total: int
    page: int
    pages: int
    limit: int
    has_next: bool
    has_previous: bool

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]


@dataclass(frozen=True, slots=True)
class CursorPage(Generic[T]):
    """A cursor page: the matched ``items`` plus next/previous cursors."""

    items: Sequence[T]
    limit: int
    has_next: bool
    has_previous: bool
    next_cursor: str | None = None
    previous_cursor: str | None = None

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]
