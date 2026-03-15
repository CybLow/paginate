"""Hypothesis configuration and sync setup for property tests."""

from __future__ import annotations

from typing import Any

from hypothesis import settings

from pypaginate._dispatch import paginate
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline
from tests.fixtures.backends import BackendEnv


settings.register_profile("ci", max_examples=50, deadline=1000)
settings.register_profile("dev", max_examples=100, deadline=500)
settings.load_profile("dev")


def setup_memory_sync(data: list[dict[str, Any]]) -> BackendEnv:
    """Build a memory BackendEnv synchronously for Hypothesis."""
    backend = MemoryBackend()
    fb = MemoryFilterBackend()
    sb = MemorySortBackend()
    srch = MemorySearchBackend()
    paginator: Paginator[Any] = Paginator(backend)
    pipeline: SyncPipeline[Any] = SyncPipeline(
        paginator,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
    )
    return BackendEnv(
        name="memory",
        mode="sync",
        pagination_backend=backend,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
        query=data,
        total=len(data),
        field_names=("id", "name", "age", "email", "active"),
        get_field=lambda item, f: item[f],
        do_paginate=lambda q, p, **kw: paginate(q, p, **kw),
        do_filter=lambda q, specs: fb.apply_filters(q, specs),
        do_sort=lambda q, specs: sb.apply_sorting(q, specs),
        do_search=lambda q, spec: srch.apply_search(q, spec),
        do_pipeline=lambda q, p, **kw: pipeline.execute(q, p, **kw),
    )
