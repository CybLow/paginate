"""Benchmark overhead isolation: HTTP vs operation vs serialization.

Shows per-operation overhead breakdown:
    operation only:      X us
    + paginate:          Y us  (Y - X = paginate overhead)
    + serialize:         Z us  (Z - Y = serialization overhead)
    + HTTP:              W us  (W - Z = HTTP/FastAPI overhead)

Groups:
    1. overhead-paginate   — paginate-only breakdown
    2. overhead-filter     — filter breakdown
    3. overhead-sort       — sort breakdown
    4. overhead-search     — search breakdown
    5. overhead-pipeline   — filter+sort+search+paginate breakdown

Run: uv run pytest tests/perf/test_overhead.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

from pypaginate import (
    FilterSpec,
    SearchSpec,
    SortDirection,
    SortSpec,
    paginate,
)
from pypaginate.adapters.fastapi import OffsetDep
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.domain.params import OffsetParams
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline
from tests.factories.data import make_users


# -- Module-level data + backends -----------------------------------

_DATA = make_users(10_000)
_PARAMS = OffsetParams(page=1, limit=20)

_fb = MemoryFilterBackend()
_sb = MemorySortBackend()
_srch = MemorySearchBackend()

_FILTER_SPECS = [FilterSpec(field="age", operator="gte", value=30)]
_SORT_SPECS = [SortSpec(field="age", direction=SortDirection.ASC)]
_SEARCH_SPEC = SearchSpec(query="User_5", fields=("name", "email"))


def _build_pipeline() -> SyncPipeline[Any]:
    """Build a sync memory pipeline."""
    backend = MemoryBackend()
    pag: Paginator[Any] = Paginator(backend)
    return SyncPipeline(
        pag,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
        search_backend=MemorySearchBackend(),
    )


_pipeline = _build_pipeline()


# -- Module-level FastAPI app with all endpoints --------------------

_app = FastAPI()
_http_pipeline = _build_pipeline()


@_app.get("/users")
def _get_users(params: OffsetDep) -> dict[str, object]:
    return paginate(_DATA, params).model_dump()


@_app.get("/filter")
def _filter_users(
    params: OffsetDep,
    age_gte: int = Query(30),
) -> dict[str, object]:
    filters = [FilterSpec(field="age", operator="gte", value=age_gte)]
    return _http_pipeline.execute(
        _DATA,
        params,
        filters=filters,
    ).model_dump()


@_app.get("/sort")
def _sort_users(
    params: OffsetDep,
    sort_field: str = Query("age"),
    sort_dir: str = Query("asc"),
) -> dict[str, object]:
    direction = SortDirection.DESC if sort_dir == "desc" else SortDirection.ASC
    sorting = [SortSpec(field=sort_field, direction=direction)]
    return _http_pipeline.execute(
        _DATA,
        params,
        sorting=sorting,
    ).model_dump()


@_app.get("/search")
def _search_users(
    params: OffsetDep,
    q: str = Query("User_5"),
) -> dict[str, object]:
    spec = SearchSpec(query=q, fields=("name", "email"))
    return _http_pipeline.execute(
        _DATA,
        params,
        search=spec,
    ).model_dump()


@_app.get("/pipeline")
def _pipeline_users(
    params: OffsetDep,
    age_gte: int = Query(30),
    sort_field: str = Query("name"),
    q: str = Query("User_5"),
) -> dict[str, object]:
    filters = [FilterSpec(field="age", operator="gte", value=age_gte)]
    sorting = [SortSpec(field=sort_field)]
    spec = SearchSpec(query=q, fields=("name", "email"))
    return _http_pipeline.execute(
        _DATA,
        params,
        filters=filters,
        sorting=sorting,
        search=spec,
    ).model_dump()


_client = TestClient(_app)


# ================================================================
# Group 1: overhead-paginate — paginate-only breakdown
# ================================================================


@pytest.mark.benchmark(group="overhead-paginate")
def test_paginate_only(benchmark: Any) -> None:
    """Pure paginate() call — no HTTP, no serialize."""
    result = benchmark(paginate, _DATA, _PARAMS)
    assert result.total == 10_000


@pytest.mark.benchmark(group="overhead-paginate")
def test_paginate_plus_serialize(benchmark: Any) -> None:
    """paginate() + model_dump_json() — no HTTP."""

    def run() -> str:
        page = paginate(_DATA, _PARAMS)
        return page.model_dump_json()

    benchmark(run)


@pytest.mark.benchmark(group="overhead-paginate")
def test_paginate_full_http(benchmark: Any) -> None:
    """Full HTTP cycle: paginate + serialize + HTTP."""

    def run() -> None:
        resp = _client.get("/users?page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 2: overhead-filter — filter breakdown
# ================================================================


@pytest.mark.benchmark(group="overhead-filter")
def test_filter_only(benchmark: Any) -> None:
    """Pure filter apply — no paginate, no HTTP, no serialize."""
    benchmark(_fb.apply_filters, _DATA, _FILTER_SPECS)


@pytest.mark.benchmark(group="overhead-filter")
def test_filter_plus_paginate(benchmark: Any) -> None:
    """Filter + paginate — no HTTP, no serialize."""

    def run() -> None:
        _pipeline.execute(_DATA, _PARAMS, filters=_FILTER_SPECS)

    benchmark(run)


@pytest.mark.benchmark(group="overhead-filter")
def test_filter_plus_paginate_plus_serialize(benchmark: Any) -> None:
    """Filter + paginate + serialize — no HTTP."""

    def run() -> str:
        page = _pipeline.execute(
            _DATA,
            _PARAMS,
            filters=_FILTER_SPECS,
        )
        return page.model_dump_json()

    benchmark(run)


@pytest.mark.benchmark(group="overhead-filter")
def test_filter_full_http(benchmark: Any) -> None:
    """Full HTTP cycle: filter + paginate + serialize + HTTP."""

    def run() -> None:
        resp = _client.get("/filter?age_gte=30&page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 3: overhead-sort — sort breakdown
# ================================================================


@pytest.mark.benchmark(group="overhead-sort")
def test_sort_only(benchmark: Any) -> None:
    """Pure sort apply — no paginate, no HTTP, no serialize."""
    benchmark(_sb.apply_sorting, _DATA, _SORT_SPECS)


@pytest.mark.benchmark(group="overhead-sort")
def test_sort_plus_paginate(benchmark: Any) -> None:
    """Sort + paginate — no HTTP, no serialize."""

    def run() -> None:
        _pipeline.execute(_DATA, _PARAMS, sorting=_SORT_SPECS)

    benchmark(run)


@pytest.mark.benchmark(group="overhead-sort")
def test_sort_plus_paginate_plus_serialize(benchmark: Any) -> None:
    """Sort + paginate + serialize — no HTTP."""

    def run() -> str:
        page = _pipeline.execute(
            _DATA,
            _PARAMS,
            sorting=_SORT_SPECS,
        )
        return page.model_dump_json()

    benchmark(run)


@pytest.mark.benchmark(group="overhead-sort")
def test_sort_full_http(benchmark: Any) -> None:
    """Full HTTP cycle: sort + paginate + serialize + HTTP."""

    def run() -> None:
        resp = _client.get("/sort?sort_field=age&page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 4: overhead-search — search breakdown
# ================================================================


@pytest.mark.benchmark(group="overhead-search")
def test_search_only(benchmark: Any) -> None:
    """Pure search apply — no paginate, no HTTP, no serialize."""
    benchmark(_srch.apply_search, _DATA, _SEARCH_SPEC)


@pytest.mark.benchmark(group="overhead-search")
def test_search_plus_paginate(benchmark: Any) -> None:
    """Search + paginate — no HTTP, no serialize."""

    def run() -> None:
        _pipeline.execute(_DATA, _PARAMS, search=_SEARCH_SPEC)

    benchmark(run)


@pytest.mark.benchmark(group="overhead-search")
def test_search_plus_paginate_plus_serialize(benchmark: Any) -> None:
    """Search + paginate + serialize — no HTTP."""

    def run() -> str:
        page = _pipeline.execute(
            _DATA,
            _PARAMS,
            search=_SEARCH_SPEC,
        )
        return page.model_dump_json()

    benchmark(run)


@pytest.mark.benchmark(group="overhead-search")
def test_search_full_http(benchmark: Any) -> None:
    """Full HTTP cycle: search + paginate + serialize + HTTP."""

    def run() -> None:
        resp = _client.get("/search?q=User_5&page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 5: overhead-pipeline — full pipeline breakdown
# ================================================================


@pytest.mark.benchmark(group="overhead-pipeline")
def test_pipeline_ops_only(benchmark: Any) -> None:
    """Filter + sort + search (no paginate, no serialize)."""

    def run() -> None:
        filtered = _fb.apply_filters(_DATA, _FILTER_SPECS)
        sorted_data = _sb.apply_sorting(filtered, _SORT_SPECS)
        _srch.apply_search(sorted_data, _SEARCH_SPEC)

    benchmark(run)


@pytest.mark.benchmark(group="overhead-pipeline")
def test_pipeline_plus_paginate(benchmark: Any) -> None:
    """Full pipeline (filter+sort+search+paginate) — no HTTP."""

    def run() -> None:
        _pipeline.execute(
            _DATA,
            _PARAMS,
            filters=_FILTER_SPECS,
            sorting=_SORT_SPECS,
            search=_SEARCH_SPEC,
        )

    benchmark(run)


@pytest.mark.benchmark(group="overhead-pipeline")
def test_pipeline_plus_serialize(benchmark: Any) -> None:
    """Full pipeline + serialize — no HTTP."""

    def run() -> str:
        page = _pipeline.execute(
            _DATA,
            _PARAMS,
            filters=_FILTER_SPECS,
            sorting=_SORT_SPECS,
            search=_SEARCH_SPEC,
        )
        return page.model_dump_json()

    benchmark(run)


@pytest.mark.benchmark(group="overhead-pipeline")
def test_pipeline_full_http(benchmark: Any) -> None:
    """Full HTTP: filter+sort+search+paginate+serialize+HTTP."""

    def run() -> None:
        resp = _client.get(
            "/pipeline?age_gte=30&sort_field=name&q=User_5&page=1&limit=20",
        )
        assert resp.status_code == 200

    benchmark(run)
