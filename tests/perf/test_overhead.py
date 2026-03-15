"""Benchmark overhead isolation: HTTP vs paginate vs serialization.

Shows:
    raw paginate:      X us
    + serialization:   Y us  (Y - X = serialization overhead)
    + HTTP:            Z us  (Z - Y = HTTP/FastAPI overhead)

Group: overhead-breakdown

Run: uv run pytest tests/perf/test_overhead.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pypaginate import paginate
from pypaginate.adapters.fastapi import OffsetDep
from pypaginate.domain.params import OffsetParams
from tests.factories.data import make_users


# -- Module-level data + app (created once) ------------------------

_DATA = make_users(10_000)

_app = FastAPI()


@_app.get("/users")
def _get_users(params: OffsetDep) -> dict[str, object]:
    return paginate(_DATA, params).model_dump()


_client = TestClient(_app)

_PARAMS = OffsetParams(page=50, limit=20)


# -- Overhead breakdown benchmarks ---------------------------------


@pytest.mark.benchmark(group="overhead-breakdown")
def test_raw_paginate_only(benchmark: Any) -> None:
    """Pure paginate() call -- no HTTP, no serialization."""
    result = benchmark(paginate, _DATA, _PARAMS)
    assert result.total == 10_000


@pytest.mark.benchmark(group="overhead-breakdown")
def test_paginate_plus_serialize(benchmark: Any) -> None:
    """paginate() + model_dump_json() -- no HTTP."""

    def paginate_and_serialize() -> str:
        page = paginate(_DATA, _PARAMS)
        return page.model_dump_json()

    benchmark(paginate_and_serialize)


@pytest.mark.benchmark(group="overhead-breakdown")
def test_full_http_cycle(benchmark: Any) -> None:
    """TestClient -> FastAPI -> paginate -> serialize -> response."""

    def run() -> None:
        resp = _client.get("/users?page=50&limit=20")
        assert resp.status_code == 200

    benchmark(run)
