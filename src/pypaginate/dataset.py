"""Resident in-memory dataset: filter + sort + paginate in one call.

:class:`Dataset` marshals a sequence of items ONCE and answers repeated
paginated queries. When the native ``paginate-core`` engine is installed it runs
the whole filter -> sort -> paginate pipeline in a single native call (returning
page indices); otherwise it falls back to the pure-Python in-memory backends.
Both paths return an identical :class:`OffsetPage`, so the result never depends
on whether the native extension is present.

This complements the top-level :func:`pypaginate.paginate` — which paginates an
already-prepared sequence — by folding filtering and sorting into the same call:
the "powerful core, thin adapter" shape, where the engine does the work and the
host only selects rows by the returned indices.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from pypaginate._dispatch import paginate
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.domain.enums import NullsPosition, SortDirection
from pypaginate.domain.pages import OffsetPage
from pypaginate.domain.params import OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec


try:
    from paginate_core import Dataset as _NativeDataset

    _HAS_NATIVE = True
except ImportError:
    _HAS_NATIVE = False


ItemT = TypeVar("ItemT")

# Stateless in-memory backends shared by the pure-Python fallback path.
_FILTER = MemoryFilterBackend()
_SORT = MemorySortBackend()
_SEARCH = MemorySearchBackend()

# Enum -> native string maps. The enums use auto() (int values), so the native
# adapter keys on these names — mirroring search/engine.py's _NATIVE_MODES.
_DIRECTION = {SortDirection.ASC: "asc", SortDirection.DESC: "desc"}
_NULLS = {NullsPosition.FIRST: "first", NullsPosition.LAST: "last"}


class Dataset(Generic[ItemT]):
    """An in-memory dataset queried by one-call ``filter + sort + paginate``."""

    __slots__ = ("_items", "_native")

    def __init__(self, items: Sequence[ItemT]) -> None:
        self._items: list[ItemT] = list(items)
        self._native: Any = self._build_native()

    def _build_native(self) -> Any:
        """Marshal the rows into the native engine once, or ``None`` if it is
        unavailable or marshalling fails (the pure-Python path always works)."""
        if not _HAS_NATIVE:
            return None
        try:
            return _NativeDataset(self._items)
        except Exception:
            return None

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        native = "native" if self._native is not None else "pure-python"
        return f"Dataset({len(self._items)} items, {native})"

    def paginate(
        self,
        params: OffsetParams,
        *,
        filters: Sequence[FilterSpec] | None = None,
        sorting: Sequence[SortSpec] | None = None,
        search: SearchSpec | None = None,
    ) -> OffsetPage[ItemT]:
        """Filter, then sort, then offset-paginate; return an :class:`OffsetPage`.

        Uses the native one-call pipeline when available and the query is
        natively supported (no ``search``); otherwise the pure-Python backends.
        Both paths produce the same page. Multiple ``filters`` are combined with
        AND (mirroring the in-memory filter backend); grouped filters are not
        accepted here — use the backend API for those.
        """
        if self._native is not None and search is None:
            page = self._native_paginate(params, filters, sorting)
            if page is not None:
                return page
        return self._python_paginate(params, filters, sorting, search)

    def _native_paginate(
        self,
        params: OffsetParams,
        filters: Sequence[FilterSpec] | None,
        sorting: Sequence[SortSpec] | None,
    ) -> OffsetPage[ItemT] | None:
        """Run the native filter+sort+paginate pass; ``None`` to fall back.

        Metadata is recomputed via :meth:`OffsetPage.create` (not taken from the
        native result) so the native and pure-Python pages are byte-identical.
        """
        try:
            result = self._native.page(
                params.page,
                params.limit,
                _to_native_filters(filters),
                _to_native_sorts(sorting),
            )
        except Exception:
            return None
        items = [self._items[i] for i in result["indices"]]
        page: OffsetPage[ItemT] = OffsetPage.create(items, result["total"], params)
        return page

    def _python_paginate(
        self,
        params: OffsetParams,
        filters: Sequence[FilterSpec] | None,
        sorting: Sequence[SortSpec] | None,
        search: SearchSpec | None,
    ) -> OffsetPage[ItemT]:
        """Pure-Python filter -> sort -> search -> paginate via memory backends."""
        data: Any = self._items
        if filters:
            data = _FILTER.apply_filters(data, list(filters))
        if sorting:
            data = _SORT.apply_sorting(data, list(sorting))
        if search is not None:
            data = _SEARCH.apply_search(data, search)
        return paginate(data, params)


def _to_native_filters(
    filters: Sequence[FilterSpec] | None,
) -> list[tuple[str, str, Any, str]]:
    """Convert flat filter specs to the native tuple form.

    Every spec is joined with AND (``"and"``) to mirror the pure-Python
    ``MemoryFilterBackend``, which ANDs all flat specs regardless of their
    ``logic`` field — keeping the native and fallback paths identical.
    """
    if not filters:
        return []
    return [(f.field, f.operator, f.value, "and") for f in filters]


def _to_native_sorts(
    sorting: Sequence[SortSpec] | None,
) -> list[tuple[str, str, str]]:
    """Convert sort specs to the native tuple form."""
    if not sorting:
        return []
    return [(s.field, _DIRECTION[s.direction], _NULLS[s.nulls]) for s in sorting]


__all__ = ["Dataset"]
