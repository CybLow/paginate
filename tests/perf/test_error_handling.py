"""Benchmark error handling and validation overhead.

Groups:
    1. validation-params — OffsetParams / CursorParams creation speed
    2. fastapi-error     — valid vs invalid requests through HTTP

Run: uv run pytest tests/perf/test_error_handling.py --benchmark-enable -v
"""

from __future__ import annotations

import contextlib
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pypaginate import paginate
from pypaginate.adapters.fastapi import OffsetDep
from pypaginate.domain.params import CursorParams, OffsetParams
from tests.factories.data import make_users


# -- Module-level app + client (created once) ----------------------

_DATA = make_users(1_000)

_app = FastAPI()


@_app.get("/users")
def _get_users(params: OffsetDep) -> dict[str, object]:
    return paginate(_DATA, params).model_dump()


_client = TestClient(_app)


# ================================================================
# Group 1: Params validation speed
# ================================================================


@pytest.mark.benchmark(group="validation-params")
def test_valid_offset_params(benchmark: Any) -> None:
    """Creating valid OffsetParams."""
    benchmark(OffsetParams, page=5, limit=20)


@pytest.mark.benchmark(group="validation-params")
def test_valid_cursor_params(benchmark: Any) -> None:
    """Creating valid CursorParams."""
    benchmark(CursorParams, limit=20, after="abc123")


@pytest.mark.benchmark(group="validation-params")
def test_invalid_params_caught(benchmark: Any) -> None:
    """Creating invalid params (caught by validation)."""

    def create_invalid() -> None:
        with contextlib.suppress(Exception):
            OffsetParams(page=0)

    benchmark(create_invalid)


# ================================================================
# Group 2: FastAPI error response speed
# ================================================================


@pytest.mark.benchmark(group="fastapi-error")
def test_fastapi_valid_request(benchmark: Any) -> None:
    """Valid request through FastAPI."""

    def run() -> None:
        resp = _client.get("/users?page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-error")
def test_fastapi_invalid_page(benchmark: Any) -> None:
    """Invalid page=0 through FastAPI -> 422."""

    def run() -> None:
        resp = _client.get("/users?page=0")
        assert resp.status_code == 422

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-error")
def test_fastapi_invalid_limit(benchmark: Any) -> None:
    """Invalid limit=5000 through FastAPI -> 422."""

    def run() -> None:
        resp = _client.get("/users?limit=5000")
        assert resp.status_code == 422

    benchmark(run)
