"""FastAPI HTTP scaling (1K -> 100K) for ALL operations with competitors.

Side-by-side comparison of pypaginate vs fastapi-pagination vs raw FastAPI
across dataset sizes, through the complete HTTP stack.

Groups (merge with test_fastapi_perf.py single-size tests):
    1. fastapi-scale-paginate  -- paginate scaling through HTTP
    2. fastapi-scale-filter    -- filter scaling through HTTP
    3. fastapi-scale-sort      -- sort scaling through HTTP
    4. fastapi-scale-search    -- search scaling through HTTP
    5. fastapi-scale-pipeline  -- full pipeline scaling through HTTP

Run: uv run pytest tests/perf/test_fastapi_scaling.py --benchmark-enable -v
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
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline
from tests.factories.data import make_users


# -- Competitor imports (guarded) ---------------------------------

try:
    from fastapi_pagination import (
        Page,
        Params,
        add_pagination,
        paginate as fp_paginate,
    )
    from fastapi_pagination.utils import disable_installed_extensions_check

    disable_installed_extensions_check()
    HAS_FP = True
except ImportError:
    HAS_FP = False

_SKIP_FP = pytest.mark.skipif(
    not HAS_FP,
    reason="fastapi-pagination not installed",
)

_slow = pytest.mark.slow
_SIZES = [
    pytest.param(1_000, id="1K"),
    pytest.param(10_000, id="10K"),
    pytest.param(100_000, id="100K", marks=_slow),
]


# -- Helpers: build apps for a given dataset ----------------------


def _build_pipeline(data: list[dict[str, Any]]) -> SyncPipeline[Any]:
    """Build a sync memory pipeline for filter/sort/search."""
    backend = MemoryBackend()
    pag: Paginator[Any] = Paginator(backend)
    return SyncPipeline(
        pag,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
        search_backend=MemorySearchBackend(),
    )


def _pp_paginate_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/users")
    def get_users(params: OffsetDep) -> dict[str, object]:
        return paginate(data, params).model_dump()

    return app


def _pp_filter_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()
    pipe = _build_pipeline(data)

    @app.get("/filter")
    def filter_users(
        params: OffsetDep,
        age_gte: int = Query(30),
    ) -> dict[str, object]:
        filters = [FilterSpec(field="age", operator="gte", value=age_gte)]
        return pipe.execute(data, params, filters=filters).model_dump()

    return app


def _pp_sort_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()
    pipe = _build_pipeline(data)

    @app.get("/sort")
    def sort_users(params: OffsetDep) -> dict[str, object]:
        sorting = [SortSpec(field="age", direction=SortDirection.ASC)]
        return pipe.execute(data, params, sorting=sorting).model_dump()

    return app


def _pp_search_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()
    pipe = _build_pipeline(data)

    @app.get("/search")
    def search_users(params: OffsetDep) -> dict[str, object]:
        spec = SearchSpec(query="User_5", fields=("name", "email"))
        return pipe.execute(data, params, search=spec).model_dump()

    return app


def _pp_pipeline_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()
    pipe = _build_pipeline(data)

    @app.get("/pipeline")
    def pipeline_users(params: OffsetDep) -> dict[str, object]:
        filters = [FilterSpec(field="age", operator="gte", value=30)]
        sorting = [SortSpec(field="name")]
        return pipe.execute(
            data,
            params,
            filters=filters,
            sorting=sorting,
        ).model_dump()

    return app


# -- Raw apps -----------------------------------------------------


def _raw_paginate_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/users")
    def get_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=1000),
    ) -> dict[str, object]:
        offset = (page - 1) * limit
        return {
            "items": data[offset : offset + limit],
            "total": len(data),
            "page": page,
            "limit": limit,
        }

    return app


def _raw_filter_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/filter")
    def filter_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
        age_gte: int = Query(30),
    ) -> dict[str, object]:
        filtered = [u for u in data if u["age"] >= age_gte]
        offset = (page - 1) * limit
        return {
            "items": filtered[offset : offset + limit],
            "total": len(filtered),
        }

    return app


def _raw_sort_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/sort")
    def sort_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
    ) -> dict[str, object]:
        sorted_items = sorted(data, key=lambda u: u["age"])
        offset = (page - 1) * limit
        return {
            "items": sorted_items[offset : offset + limit],
            "total": len(sorted_items),
        }

    return app


def _raw_search_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/search")
    def search_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
    ) -> dict[str, object]:
        matched = [
            u for u in data if "user_5" in u["name"].lower() or "user_5" in u["email"].lower()
        ]
        offset = (page - 1) * limit
        return {
            "items": matched[offset : offset + limit],
            "total": len(matched),
        }

    return app


def _raw_pipeline_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/pipeline")
    def pipeline_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
    ) -> dict[str, object]:
        filtered = [u for u in data if u["age"] >= 30]
        sorted_items = sorted(filtered, key=lambda u: u["name"])
        offset = (page - 1) * limit
        return {
            "items": sorted_items[offset : offset + limit],
            "total": len(sorted_items),
        }

    return app


# -- fp apps (guarded) --------------------------------------------


def _fp_paginate_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/users", response_model=Page[dict[str, Any]])  # type: ignore[type-arg]
    def get_users(params: Params = Params()) -> Any:  # type: ignore[assignment]
        return fp_paginate(data, params)  # type: ignore[arg-type]

    add_pagination(app)
    return app


# -- Module-level data + clients (built once) ---------------------

_DATA_1K = make_users(1_000)
_DATA_10K = make_users(10_000)
_DATA_100K = make_users(100_000)

_DATASETS: dict[int, list[dict[str, Any]]] = {
    1_000: _DATA_1K,
    10_000: _DATA_10K,
    100_000: _DATA_100K,
}

# Pre-built clients per (operation, size)
_PP_PAG_CLIENTS = {s: TestClient(_pp_paginate_app(d)) for s, d in _DATASETS.items()}
_PP_FIL_CLIENTS = {s: TestClient(_pp_filter_app(d)) for s, d in _DATASETS.items()}
_PP_SRT_CLIENTS = {s: TestClient(_pp_sort_app(d)) for s, d in _DATASETS.items()}
_PP_SCH_CLIENTS = {s: TestClient(_pp_search_app(d)) for s, d in _DATASETS.items()}
_PP_PIP_CLIENTS = {s: TestClient(_pp_pipeline_app(d)) for s, d in _DATASETS.items()}

_RAW_PAG_CLIENTS = {s: TestClient(_raw_paginate_app(d)) for s, d in _DATASETS.items()}
_RAW_FIL_CLIENTS = {s: TestClient(_raw_filter_app(d)) for s, d in _DATASETS.items()}
_RAW_SRT_CLIENTS = {s: TestClient(_raw_sort_app(d)) for s, d in _DATASETS.items()}
_RAW_SCH_CLIENTS = {s: TestClient(_raw_search_app(d)) for s, d in _DATASETS.items()}
_RAW_PIP_CLIENTS = {s: TestClient(_raw_pipeline_app(d)) for s, d in _DATASETS.items()}

_FP_PAG_CLIENTS: dict[int, TestClient] = {}
if HAS_FP:
    _FP_PAG_CLIENTS = {s: TestClient(_fp_paginate_app(d)) for s, d in _DATASETS.items()}


# ================================================================
# 1. fastapi-scale-paginate
# ================================================================


@pytest.mark.benchmark(group="fastapi-scale-paginate")
@pytest.mark.parametrize("size", _SIZES)
def test_pypaginate_http_paginate_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """pypaginate pagination through HTTP at various sizes."""
    client = _PP_PAG_CLIENTS[size]
    resp = benchmark(client.get, "/users?page=5&limit=20")
    assert resp.status_code == 200


@_SKIP_FP
@pytest.mark.benchmark(group="fastapi-scale-paginate")
@pytest.mark.parametrize("size", _SIZES)
def test_fp_http_paginate_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """fastapi-pagination through HTTP at various sizes."""
    client = _FP_PAG_CLIENTS[size]
    resp = benchmark(client.get, "/users?page=5&size=20")
    assert resp.status_code == 200


@pytest.mark.benchmark(group="fastapi-scale-paginate")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_http_paginate_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw FastAPI manual slice through HTTP at various sizes."""
    client = _RAW_PAG_CLIENTS[size]
    resp = benchmark(client.get, "/users?page=5&limit=20")
    assert resp.status_code == 200


# ================================================================
# 2. fastapi-scale-filter
# ================================================================


@pytest.mark.benchmark(group="fastapi-scale-filter")
@pytest.mark.parametrize("size", _SIZES)
def test_pypaginate_http_filter_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """pypaginate filter through HTTP at various sizes."""
    client = _PP_FIL_CLIENTS[size]
    resp = benchmark(client.get, "/filter?page=1&limit=20&age_gte=30")
    assert resp.status_code == 200


@pytest.mark.benchmark(group="fastapi-scale-filter")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_http_filter_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw filter through HTTP at various sizes."""
    client = _RAW_FIL_CLIENTS[size]
    resp = benchmark(client.get, "/filter?page=1&limit=20&age_gte=30")
    assert resp.status_code == 200


# ================================================================
# 3. fastapi-scale-sort
# ================================================================


@pytest.mark.benchmark(group="fastapi-scale-sort")
@pytest.mark.parametrize("size", _SIZES)
def test_pypaginate_http_sort_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """pypaginate sort through HTTP at various sizes."""
    client = _PP_SRT_CLIENTS[size]
    resp = benchmark(client.get, "/sort?page=1&limit=20")
    assert resp.status_code == 200


@pytest.mark.benchmark(group="fastapi-scale-sort")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_http_sort_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw sort through HTTP at various sizes."""
    client = _RAW_SRT_CLIENTS[size]
    resp = benchmark(client.get, "/sort?page=1&limit=20")
    assert resp.status_code == 200


# ================================================================
# 4. fastapi-scale-search
# ================================================================


@pytest.mark.benchmark(group="fastapi-scale-search")
@pytest.mark.parametrize("size", _SIZES)
def test_pypaginate_http_search_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """pypaginate search through HTTP at various sizes."""
    client = _PP_SCH_CLIENTS[size]
    resp = benchmark(client.get, "/search?page=1&limit=20")
    assert resp.status_code == 200


@pytest.mark.benchmark(group="fastapi-scale-search")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_http_search_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw search through HTTP at various sizes."""
    client = _RAW_SCH_CLIENTS[size]
    resp = benchmark(client.get, "/search?page=1&limit=20")
    assert resp.status_code == 200


# ================================================================
# 5. fastapi-scale-pipeline
# ================================================================


@pytest.mark.benchmark(group="fastapi-scale-pipeline")
@pytest.mark.parametrize("size", _SIZES)
def test_pypaginate_http_pipeline_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """pypaginate pipeline through HTTP at various sizes."""
    client = _PP_PIP_CLIENTS[size]
    resp = benchmark(client.get, "/pipeline?page=1&limit=20")
    assert resp.status_code == 200


@pytest.mark.benchmark(group="fastapi-scale-pipeline")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_http_pipeline_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw pipeline through HTTP at various sizes."""
    client = _RAW_PIP_CLIENTS[size]
    resp = benchmark(client.get, "/pipeline?page=1&limit=20")
    assert resp.status_code == 200
