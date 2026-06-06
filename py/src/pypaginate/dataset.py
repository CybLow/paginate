"""Resident in-memory dataset: filter + sort + paginate in one call.

:class:`Dataset` marshals a sequence of items ONCE and answers repeated
paginated queries. It has two execution shapes, both driven by the native
``_core`` engine:

* the **resident one-call pipeline** — filter -> search -> sort -> paginate in a
  single native call returning page indices (the normal path, covering every
  combination of filters / sorting / search), and
* **per-stage native calls** — filter / sort / search routed through the memory
  backends (each its own ``_core`` call), used only as a fallback if the resident
  dataset could not be built (a row failed to marshal).

Both shapes return an identical :class:`OffsetPage`, so the result never depends
on which path ran. The engine itself is mandatory (built into the wheel), so
there is no pure-Python execution: the ``_native`` guard below covers only a
resident-marshalling failure, never an absent engine.

In the one-call pipeline ``search`` is a match-filter (keep rows matching the
query); explicit ``sorting`` still decides the order, and the resident trigram
index prunes fuzzy candidates. This complements the top-level
:func:`pypaginate.paginate` — which paginates an already-prepared sequence — by
folding filtering, search, and sorting into the same call: the "powerful core,
thin adapter" shape, where the engine does the work and the host only selects
rows by the returned indices.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar, cast

from pypaginate._dispatch import paginate
from pypaginate._native import and_filter_tuples, search_stage_tuple, sort_tuples
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.domain.pages import OffsetPage
from pypaginate.domain.params import OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec


try:
    from pypaginate._core import Dataset as _NativeDataset

    _HAS_NATIVE = True
except ImportError:
    _HAS_NATIVE = False


ItemT = TypeVar("ItemT")

# Stateless in-memory backends for the per-stage fallback (filter / sort / search
# all delegate to the native _core engine). Used only when the resident dataset
# could not be built; the normal path is the one-call native pipeline.
_FILTER = MemoryFilterBackend()
_SORT = MemorySortBackend()
_SEARCH = MemorySearchBackend()


class Dataset(Generic[ItemT]):
    """An in-memory dataset queried by one-call ``filter + sort + paginate``."""

    __slots__ = ("_items", "_native")

    def __init__(self, items: Sequence[ItemT]) -> None:
        self._items: list[ItemT] = list(items)
        self._native: Any = self._build_native()

    def _build_native(self) -> Any:
        """Build the resident native dataset once, or ``None`` to use the
        per-stage path — when the (mandatory) engine import is somehow missing,
        or a row cannot be marshalled for the one-call pipeline."""
        if not _HAS_NATIVE:
            return None
        try:
            return _NativeDataset(self._items)
        except Exception:
            return None

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        path = "resident" if self._native is not None else "per-stage"
        return f"Dataset({len(self._items)} items, {path})"

    def paginate(
        self,
        params: OffsetParams,
        *,
        filters: Sequence[FilterSpec] | None = None,
        sorting: Sequence[SortSpec] | None = None,
        search: SearchSpec | None = None,
    ) -> OffsetPage[ItemT]:
        """Filter, search, sort, then offset-paginate; return an
        :class:`OffsetPage`.

        Runs the resident one-call native pipeline (filter -> search -> sort ->
        paginate); falls back to the per-stage backends only if the resident
        dataset couldn't be built. Both paths produce the same page. ``search``
        is a match-filter and explicit ``sorting`` decides the order. Multiple
        ``filters`` are combined with AND (mirroring the in-memory filter
        backend); grouped filters are not accepted here — use the backend API.
        """
        if self._native is not None:
            page = self._native_paginate(params, filters, sorting, search)
            if page is not None:
                return page
        return self._per_stage_paginate(params, filters, sorting, search)

    def _native_paginate(
        self,
        params: OffsetParams,
        filters: Sequence[FilterSpec] | None,
        sorting: Sequence[SortSpec] | None,
        search: SearchSpec | None,
    ) -> OffsetPage[ItemT] | None:
        """Run the resident filter -> search -> sort -> paginate pass in one
        native call; ``None`` to fall back to the per-stage path.

        Search is a match-filter (explicit ``sorting`` still decides order), and
        the trigram index prunes fuzzy candidates. Metadata is recomputed via
        :meth:`OffsetPage.create` (not taken from the native result) so the
        resident and per-stage pages are byte-identical.
        """
        try:
            result = self._native.page(
                params.page,
                params.limit,
                and_filter_tuples(filters or []),
                sort_tuples(sorting or []),
                search_stage_tuple(search) if search is not None else None,
            )
        except Exception:
            return None
        items = [self._items[i] for i in result["indices"]]
        page: OffsetPage[ItemT] = OffsetPage.create(items, result["total"], params)
        return page

    def _per_stage_paginate(
        self,
        params: OffsetParams,
        filters: Sequence[FilterSpec] | None,
        sorting: Sequence[SortSpec] | None,
        search: SearchSpec | None,
    ) -> OffsetPage[ItemT]:
        """Fallback: per-stage filter -> sort -> search -> paginate via the
        (native-backed) memory backends.

        This runs the stages in the original pypaginate order (sort before
        search), which yields the **same page** as the native pipeline's
        filter -> search -> sort: search is an order-preserving match-filter and
        the sort is stable, so the two orders commute. ``test_dataset`` asserts
        this byte-for-byte by running both paths.
        """
        data: Any = self._items
        if filters:
            data = _FILTER.apply_filters(data, list(filters))
        if sorting:
            data = _SORT.apply_sorting(data, list(sorting))
        if search is not None:
            data = _SEARCH.apply_search(data, search)
        return paginate(cast("Sequence[ItemT]", data), params)


__all__ = ["Dataset"]
