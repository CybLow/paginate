"""In-memory search backend.

Implements the ``SearchBackend`` protocol for Python sequences. All matching —
exact / prefix / contains and fuzzy / token-sort — runs in the native ``_core``
engine via :func:`pypaginate._native.match_filter`, so the backend normalizes
and scores identically to :func:`pypaginate._native.search` and the resident
``Dataset``. There is no Python-side similarity heuristic to drift from the
engine (the previous char-overlap score did, and silently mishandled
``TOKEN_SORT``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pypaginate import _native


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import SearchSpec


class MemorySearchBackend:
    """Search backend for in-memory sequences."""

    __slots__ = ()

    @staticmethod
    def apply_search(query: object, spec: SearchSpec) -> object:
        """Keep items where any field matches the query (native match-filter).

        Args:
            query: A Python sequence of items.
            spec: Search specification (query, fields, mode, fuzzy, threshold).

        Returns:
            Matching items in original order.
        """
        items = cast("Sequence[object]", query)
        return _native.match_filter(items, spec)


__all__ = ["MemorySearchBackend"]
