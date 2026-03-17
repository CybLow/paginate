"""Architecture tests verifying protocol satisfaction.

Ensures that concrete memory backends satisfy their corresponding
protocol interfaces via runtime isinstance checks.
"""

from __future__ import annotations

from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.domain.protocols import (
    FilterBackend,
    SearchBackend,
    SortBackend,
    SyncPaginationBackend,
)


def test_memory_backend_satisfies_sync_pagination():
    """MemoryBackend implements SyncPaginationBackend protocol."""
    backend = MemoryBackend()
    assert isinstance(backend, SyncPaginationBackend)


def test_memory_filter_backend_satisfies_filter():
    """MemoryFilterBackend implements FilterBackend protocol."""
    backend = MemoryFilterBackend()
    assert isinstance(backend, FilterBackend)


def test_memory_sort_backend_satisfies_sort():
    """MemorySortBackend implements SortBackend protocol."""
    backend = MemorySortBackend()
    assert isinstance(backend, SortBackend)


def test_memory_search_backend_satisfies_search():
    """MemorySearchBackend implements SearchBackend protocol."""
    backend = MemorySearchBackend()
    assert isinstance(backend, SearchBackend)


def test_memory_backend_has_count_method():
    """MemoryBackend exposes count method matching protocol."""
    backend = MemoryBackend()
    result = backend.count([1, 2, 3])
    assert result == 3


def test_memory_backend_has_fetch_method():
    """MemoryBackend exposes fetch method matching protocol."""
    backend = MemoryBackend()
    result = backend.fetch([10, 20, 30, 40], offset=1, limit=2)
    assert result == [20, 30]
