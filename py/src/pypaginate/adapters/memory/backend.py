"""In-memory pagination backend.

Implements SyncPaginationBackend for Python sequences.
Validates input type at runtime for clear error messages.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar, cast


ItemT = TypeVar("ItemT")


class MemoryBackend(Generic[ItemT]):
    """Sync pagination backend for in-memory sequences.

    Counts via ``len()`` and fetches via slicing.
    Satisfies ``SyncPaginationBackend[ItemT]`` protocol.
    """

    __slots__ = ()

    def count(self, query: object) -> int:
        """Count items in a sequence.

        Args:
            query: A Python sequence (list, tuple, etc.).

        Returns:
            Number of items.

        Raises:
            TypeError: If query is not a Sequence.
        """
        self._validate(query)
        return len(cast("Sequence[ItemT]", query))

    def fetch(
        self,
        query: object,
        offset: int,
        limit: int,
    ) -> list[ItemT]:
        """Fetch a slice of items from a sequence.

        Args:
            query: A Python sequence.
            offset: Start index.
            limit: Maximum items to return.

        Returns:
            List of items for the requested slice.

        Raises:
            TypeError: If query is not a Sequence.
        """
        self._validate(query)
        return list(cast("Sequence[ItemT]", query)[offset : offset + limit])

    @staticmethod
    def _validate(query: object) -> None:
        if not isinstance(query, Sequence) or isinstance(query, (str, bytes)):
            msg = f"MemoryBackend requires a Sequence, got {type(query).__name__}"
            raise TypeError(msg)


__all__ = ["MemoryBackend"]
