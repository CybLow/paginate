"""Integration tests for custom user-defined backends.

Verifies that custom backends implementing SyncPaginationBackend
protocol work with paginate(), Paginator, and SyncPipeline.
"""

from __future__ import annotations

from collections.abc import Sequence

from pypaginate import OffsetPage, OffsetParams, OverflowStrategy, paginate
from pypaginate.domain.protocols import SyncPaginationBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


class DictBackend:
    """Custom backend wrapping a dict of lists."""

    def __init__(self, data: dict[str, list[object]]) -> None:
        self._data = data

    def count(self, query: object) -> int:
        """Count items for a given key."""
        items = self._resolve(query)
        return len(items)

    def fetch(self, query: object, offset: int, limit: int) -> list[object]:
        """Fetch a slice of items for a given key."""
        items = self._resolve(query)
        return items[offset : offset + limit]

    def _resolve(self, query: object) -> Sequence[object]:
        if isinstance(query, str):
            return self._data.get(query, [])
        if isinstance(query, Sequence) and not isinstance(query, (str, bytes)):
            return list(query)
        return []


class TestCustomBackendProtocol:
    """Custom backend satisfies SyncPaginationBackend protocol."""

    def test_satisfies_protocol(self) -> None:
        """DictBackend is recognized as SyncPaginationBackend."""
        backend = DictBackend({"users": [1, 2, 3]})

        assert isinstance(backend, SyncPaginationBackend)


class TestCustomBackendWithPaginator:
    """Custom backend used directly with Paginator."""

    def test_paginator_with_custom_backend(self) -> None:
        """Paginator produces valid OffsetPage from custom backend."""
        items = list(range(25))
        backend = DictBackend({"items": items})
        paginator: Paginator[object] = Paginator(backend)

        page = paginator.paginate("items", OffsetParams(page=1, limit=10))

        assert isinstance(page, OffsetPage)
        assert page.total == 25
        assert len(page.items) == 10

    def test_paginator_last_page(self) -> None:
        """Custom backend paginates to the last page correctly."""
        items = list(range(25))
        backend = DictBackend({"items": items})
        paginator: Paginator[object] = Paginator(backend)

        page = paginator.paginate("items", OffsetParams(page=3, limit=10))

        assert len(page.items) == 5
        assert page.has_next is False


class TestCustomBackendWithPaginate:
    """Custom backend used via paginate() dispatch."""

    def test_paginate_with_explicit_backend(self) -> None:
        """paginate() works with explicit backend= parameter."""
        items = list(range(30))
        backend = DictBackend({"k": items})

        page = paginate("k", OffsetParams(page=1, limit=10), backend=backend)

        assert isinstance(page, OffsetPage)
        assert page.total == 30

    def test_paginate_with_clamp_overflow(self) -> None:
        """Custom backend + CLAMP overflow returns last page."""
        items = list(range(20))
        backend = DictBackend({"k": items})

        page = paginate(
            "k",
            OffsetParams(page=99, limit=10),
            backend=backend,
            overflow=OverflowStrategy.CLAMP,
        )

        assert len(page.items) > 0
        assert page.page <= page.pages


class TestCustomBackendWithPipeline:
    """Custom backend inside SyncPipeline with filter backend."""

    def test_pipeline_with_custom_paginator(self) -> None:
        """SyncPipeline uses custom backend for pagination."""
        data = [{"name": f"u{i}", "age": 20 + i} for i in range(20)]
        backend = DictBackend({"_": data})
        paginator: Paginator[object] = Paginator(backend)
        pipeline: SyncPipeline[object] = SyncPipeline(paginator)

        page = pipeline.execute("_", OffsetParams(page=1, limit=5))

        assert page.total == 20
        assert len(page.items) == 5
