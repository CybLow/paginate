"""Custom backend integration tests — user-defined backends."""

from __future__ import annotations

from collections.abc import Sequence

from pypaginate import OffsetParams, SortDirection, SortSpec, paginate
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


class DictBackend:
    """User-defined sync backend working with plain dicts."""

    def count(self, query: object) -> int:
        return len(query)  # type: ignore[arg-type]

    def fetch(self, query: object, offset: int, limit: int) -> list[object]:
        items: Sequence[object] = query  # type: ignore[assignment]
        return list(items[offset : offset + limit])


class DictSortBackend:
    """User-defined sort backend for dicts."""

    @staticmethod
    def apply_sorting(query: object, sorting: Sequence[SortSpec]) -> object:
        items = list(query)  # type: ignore[call-overload]
        for spec in reversed(sorting):
            reverse = spec.direction is SortDirection.DESC
            items = sorted(
                items,
                key=lambda item: item.get(spec.field, ""),  # type: ignore[union-attr]
                reverse=reverse,
            )
        return items


async def test_custom_sync_backend() -> None:
    """A user-defined backend works with paginate()."""
    data = [{"id": i, "name": f"Item_{i}"} for i in range(20)]
    backend = DictBackend()
    page = paginate(data, OffsetParams(page=1, limit=5), backend=backend)
    assert page.total == 20
    assert len(page.items) == 5


async def test_custom_with_pipeline() -> None:
    """A user-defined backend works in SyncPipeline."""
    data = [{"id": i, "name": f"Item_{i}"} for i in range(10)]
    backend = DictBackend()
    sort_backend = DictSortBackend()

    pipeline = SyncPipeline(
        Paginator(backend),  # type: ignore[arg-type]
        sort_backend=sort_backend,
    )
    page = pipeline.execute(
        data,
        OffsetParams(page=1, limit=100),
        sorting=[SortSpec(field="name", direction=SortDirection.DESC)],
    )
    names = [item["name"] for item in page.items]  # type: ignore[index]
    assert names == sorted(names, reverse=True)
