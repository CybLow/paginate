"""Shared fixtures for memory integration tests.

Provides pre-wired pipeline for cross-module tests.
``sample_users`` is inherited from root ``tests/conftest.py``.
"""

from __future__ import annotations

import pytest

from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


@pytest.fixture()
def memory_pipeline() -> SyncPipeline[dict[str, object]]:
    """SyncPipeline wired with all memory backends."""
    backend = MemoryBackend()
    paginator: Paginator[dict[str, object]] = Paginator(backend)
    return SyncPipeline(
        paginator,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
        search_backend=MemorySearchBackend(),
    )
