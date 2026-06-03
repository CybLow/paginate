"""In-memory ranked search — a thin adapter over the native ``_core`` engine.

``SearchEngine`` delegates filtering + relevance ranking (exact/prefix/contains
matching, fuzzy / token-sort scoring, optional per-field weights, min/max
limits) to ``pypaginate._core`` via :mod:`pypaginate._native`. The host only
selects rows by the indices the engine returns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pypaginate import _native


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pypaginate.domain.specs import SearchSpec


T = TypeVar("T")


class SearchEngine:
    """Stateless engine that searches sequences by ``SearchSpec`` (native)."""

    __slots__ = ()

    def apply(self, items: Sequence[T], spec: SearchSpec) -> list[T]:
        """Filter and rank items by search relevance via the native engine.

        Returns items in ranked (relevance) order. A query shorter than
        ``spec.min_length`` (or one that tokenizes to nothing) returns every
        item in original order, matching the engine's contract.
        """
        return _native.search(items, spec)


__all__ = ["SearchEngine"]
