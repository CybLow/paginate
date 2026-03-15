"""Benchmark FastAPI full HTTP cycle: request -> params -> paginate -> response.

Measures end-to-end latency including TestClient overhead,
query param parsing, pagination, and JSON serialization.

Run: uv run pytest tests/perf/test_fastapi_perf.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pypaginate import paginate
from pypaginate.adapters.fastapi import OffsetDep
from tests.factories.data import make_users


# -- Competitor imports (guarded) ------------------------------------------

try:
    from fastapi_pagination import Page, Params, paginate as fp_paginate
    from fastapi_pagination.utils import disable_installed_extensions_check

    disable_installed_extensions_check()
    HAS_FP = True
except ImportError:
    HAS_FP = False


# -- App factories ---------------------------------------------------------


def _build_pypaginate_app(data: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI()

    @app.get("/users")
    def get_users(params: OffsetDep) -> dict[str, object]:
        page = paginate(data, params)
        return page.model_dump()

    return app


def _build_fp_app(data: list[dict[str, Any]]) -> FastAPI:
    """Build fastapi-pagination app for comparison."""
    app = FastAPI()

    @app.get("/users", response_model=Page[dict[str, Any]])  # type: ignore[type-arg]
    def get_users(params: Params = Params()) -> Any:  # type: ignore[assignment]
        return fp_paginate(data, params)  # type: ignore[arg-type]

    return app


# -- Fixtures --------------------------------------------------------------


@pytest.fixture(scope="module")
def dataset_10k() -> list[dict[str, Any]]:
    """10K user dicts for benchmarks."""
    return make_users(10_000)


@pytest.fixture(scope="module")
def pypaginate_client(dataset_10k: list[dict[str, Any]]) -> TestClient:
    """TestClient for pypaginate app with 10K items."""
    return TestClient(_build_pypaginate_app(dataset_10k))


@pytest.fixture(scope="module")
def fp_client(dataset_10k: list[dict[str, Any]]) -> TestClient | None:
    """TestClient for fastapi-pagination app, or None."""
    if not HAS_FP:
        return None
    return TestClient(_build_fp_app(dataset_10k))


# -- Benchmarks ------------------------------------------------------------


@pytest.mark.benchmark
def test_bench_offset_10k(
    benchmark: Any,
    pypaginate_client: TestClient,
) -> None:
    """Benchmark pypaginate HTTP cycle with 10K items."""

    def _request() -> None:
        resp = pypaginate_client.get("/users?page=1&limit=20")
        assert resp.status_code == 200

    benchmark(_request)


@pytest.mark.benchmark
def test_bench_offset_small_page(
    benchmark: Any,
    pypaginate_client: TestClient,
) -> None:
    """Benchmark pypaginate with small page size (limit=5)."""

    def _request() -> None:
        resp = pypaginate_client.get("/users?page=50&limit=5")
        assert resp.status_code == 200

    benchmark(_request)


@pytest.mark.benchmark
def test_bench_offset_large_page(
    benchmark: Any,
    pypaginate_client: TestClient,
) -> None:
    """Benchmark pypaginate with large page size (limit=1000)."""

    def _request() -> None:
        resp = pypaginate_client.get("/users?page=1&limit=1000")
        assert resp.status_code == 200

    benchmark(_request)


@pytest.mark.benchmark
@pytest.mark.skipif(not HAS_FP, reason="fastapi-pagination not installed")
def test_bench_fp_offset_10k(
    benchmark: Any,
    fp_client: TestClient | None,
) -> None:
    """Benchmark fastapi-pagination HTTP cycle with 10K items."""
    assert fp_client is not None

    def _request() -> None:
        resp = fp_client.get("/users?page=1&size=20")
        assert resp.status_code == 200

    benchmark(_request)
