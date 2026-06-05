"""Resident in-memory dataset: filter + sort + paginate in one call.

:class:`Dataset` marshals a sequence of items ONCE and answers repeated
paginated queries. It has two execution shapes, both driven by the native
``_core`` engine:

* the **resident one-call pipeline** — filter -> sort -> paginate in a single
  native call returning page indices (used when no ``search`` is requested), and
* **per-stage native calls** — filter / sort / search routed through the memory
  backends (each its own ``_core`` call), used for ``search`` (which the one-call
  pipeline does not cover) or if the one-shot resident dataset could not be built.

Both shapes return an identical :class:`OffsetPage`, so the result never depends
on which path ran. The engine itself is mandatory (built into the wheel), so
there is no pure-Python execution: the ``_native`` guard below covers only a
resident-marshalling failure, never an absent engine.

This complements the top-level :func:`pypaginate.paginate` — which paginates an
already-prepared sequence — by folding filtering and sorting into the same call:
the "powerful core, thin adapter" shape, where the engine does the work and the
host only selects rows by the returned indices.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar, cast

from pypaginate._dispatch import paginate
from pypaginate._native import and_filter_tuples, dataset_match_filter, sort_tuples
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

# Stateless in-memory backends for the per-stage path (filter / sort / search
# all delegate to the native _core engine). Used when a search is requested
# (which the resident one-call page() doesn't cover) or the resident dataset
# could not be built.
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
        """Filter, then sort, then offset-paginate; return an :class:`OffsetPage`.

        Uses the resident one-call pipeline when the query is supported (no
        ``search``); otherwise the per-stage native backends. Both paths produce
        the same page. Multiple ``filters`` are combined with AND (mirroring the
        in-memory filter backend); grouped filters are not accepted here — use
        the backend API for those.
        """
        if self._native is not None and search is None:
            page = self._native_paginate(params, filters, sorting)
            if page is not None:
                return page
        if self._native is not None and search is not None and not filters and not sorting:
            page = self._native_search(params, search)
            if page is not None:
                return page
        return self._per_stage_paginate(params, filters, sorting, search)

    def _native_search(
        self,
        params: OffsetParams,
        search: SearchSpec,
    ) -> OffsetPage[ItemT] | None:
        """Index-backed match-filter on the resident dataset, then paginate.

        Used for a search with no filters/sorting (so it runs over the full
        resident rows the trigram index covers); ``None`` to fall back.
        """
        try:
            indices = dataset_match_filter(self._native, search)
        except Exception:
            return None
        matched = [self._items[i] for i in indices]
        return paginate(cast("Sequence[ItemT]", matched), params)

    def _native_paginate(
        self,
        params: OffsetParams,
        filters: Sequence[FilterSpec] | None,
        sorting: Sequence[SortSpec] | None,
    ) -> OffsetPage[ItemT] | None:
        """Run the resident filter+sort+paginate pass; ``None`` to fall back.

        Metadata is recomputed via :meth:`OffsetPage.create` (not taken from the
        native result) so the resident and per-stage pages are byte-identical.
        """
        try:
            result = self._native.page(
                params.page,
                params.limit,
                and_filter_tuples(filters or []),
                sort_tuples(sorting or []),
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
        """Per-stage filter -> sort -> search -> paginate via the (native-backed)
        memory backends."""
        data: Any = self._items
        if filters:
            data = _FILTER.apply_filters(data, list(filters))
        if sorting:
            data = _SORT.apply_sorting(data, list(sorting))
        if search is not None:
            data = _SEARCH.apply_search(data, search)
        return paginate(cast("Sequence[ItemT]", data), params)


__all__ = ["Dataset"]
