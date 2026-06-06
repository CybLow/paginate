"""Resident in-memory dataset: marshal once, query many times.

Marshals a sequence into the Rust core ONCE, then answers repeated filter / sort
/ search / page queries natively (the core returns indices; this wrapper selects
your original objects). Build once, query many — the only in-memory shape where
crossing into Rust pays off versus native ``list`` operations.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

from pypaginate import _core, _native
from pypaginate.errors import FilterError, SearchError, SortError
from pypaginate.pages import OffsetPage
from pypaginate.params import OffsetParams
from pypaginate.specs import FilterSpec, SearchSpec, SortSpec


ItemT = TypeVar("ItemT")


class Dataset(Generic[ItemT]):
    """An in-memory dataset queried natively (marshalled once)."""

    __slots__ = ("_inner", "_items")

    def __init__(self, items: Sequence[ItemT]) -> None:
        self._items: list[ItemT] = list(items)
        self._inner = _core.Dataset(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Dataset({len(self._items)} items)"

    def _select(self, indices: list[int]) -> list[ItemT]:
        return [self._items[i] for i in indices]

    def filter(self, filters: Sequence[FilterSpec]) -> list[ItemT]:
        """Rows matching the flat ``filters`` (each keeps its own AND/OR logic)."""
        tuples = _native.filter_tuples(filters)
        try:
            return self._select(self._inner.filter(tuples))
        except (KeyError, ValueError) as exc:
            raise FilterError(str(exc)) from exc

    def sort(self, sorting: Sequence[SortSpec]) -> list[ItemT]:
        """Rows sorted by ``sorting`` (stable, null-aware)."""
        tuples = _native.sort_tuples(sorting)
        try:
            return self._select(self._inner.sort(tuples))
        except (KeyError, ValueError) as exc:
            raise SortError(str(exc)) from exc

    def search(self, spec: SearchSpec) -> list[ItemT]:
        """Rows ranked by relevance of ``spec`` over its fields."""
        try:
            return self._select(self._search(spec))
        except (KeyError, ValueError) as exc:
            raise SearchError(str(exc)) from exc

    def _search(self, spec: SearchSpec) -> list[int]:
        return self._inner.search(
            spec.query,
            list(spec.fields),
            spec.mode or "contains",
            spec.fuzzy or "exact",
            spec.threshold if spec.threshold is not None else 30,
            spec.min_length if spec.min_length is not None else 1,
            spec.max_results,
        )

    def page(
        self,
        params: OffsetParams,
        *,
        filters: Sequence[FilterSpec] | None = None,
        sorting: Sequence[SortSpec] | None = None,
        search: SearchSpec | None = None,
    ) -> OffsetPage[ItemT]:
        """Filter + search + sort + offset-paginate in one native call."""
        result = self._inner.page(
            params.page,
            params.limit,
            _native.filter_tuples(filters or []),
            _native.sort_tuples(sorting or []),
            _native.search_stage(search) if search is not None else None,
        )
        items = self._select(result["indices"])
        return _native.build_offset_page(items, result["total"], params)


__all__ = ["Dataset"]
