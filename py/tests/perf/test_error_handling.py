"""Benchmark error handling and validation overhead.

Groups:
    1. validation-params       — OffsetParams / CursorParams creation
    2. fastapi-error           — valid vs invalid paginate requests
    3. validation-filter       — FilterSpec creation (valid/invalid)
    4. validation-sort         — SortSpec creation
    5. validation-search       — SearchSpec creation
    6. fastapi-error-filter    — valid vs invalid filter requests
    7. fastapi-error-sort      — valid vs invalid sort requests
    8. fastapi-error-search    — valid vs invalid search requests

Run: uv run pytest tests/perf/test_error_handling.py --benchmark-enable -v
"""

from __future__ import annotations

import contextlib
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
from pypaginate.domain.params import CursorParams, OffsetParams
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline
from tests.factories.data import make_users


# -- Module-level data + pipeline -----------------------------------

_DATA = make_users(1_000)


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


# -- Module-level app + client (created once) ----------------------

_app = FastAPI()


@_app.get("/users")
def _get_users(params: OffsetDep) -> dict[str, object]:
    return paginate(_DATA, params).model_dump()


@_app.get("/filter")
def _filter_users(
    params: OffsetDep,
    age_gte: int = Query(30),
) -> dict[str, object]:
    filters = [FilterSpec(field="age", operator="gte", value=age_gte)]
    return _pipeline.execute(_DATA, params, filters=filters).model_dump()


@_app.get("/sort")
def _sort_users(
    params: OffsetDep,
    sort_field: str = Query("age"),
    sort_dir: str = Query("asc"),
) -> dict[str, object]:
    direction = SortDirection.DESC if sort_dir == "desc" else SortDirection.ASC
    sorting = [SortSpec(field=sort_field, direction=direction)]
    return _pipeline.execute(_DATA, params, sorting=sorting).model_dump()


@_app.get("/search")
def _search_users(
    params: OffsetDep,
    q: str = Query("User_5"),
) -> dict[str, object]:
    spec = SearchSpec(query=q, fields=("name", "email"))
    return _pipeline.execute(_DATA, params, search=spec).model_dump()


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


# ================================================================
# Group 3: Filter spec validation speed
# ================================================================


@pytest.mark.benchmark(group="validation-filter")
def test_valid_filter_spec(benchmark: Any) -> None:
    """Creating valid FilterSpec."""
    benchmark(FilterSpec, field="age", operator="gte", value=30)


@pytest.mark.benchmark(group="validation-filter")
def test_invalid_filter_operator(benchmark: Any) -> None:
    """Invalid operator caught by Pydantic Literal validation."""

    def create_invalid() -> None:
        with contextlib.suppress(Exception):
            FilterSpec(field="age", operator="invalid_op", value=30)  # type: ignore[arg-type]

    benchmark(create_invalid)


@pytest.mark.benchmark(group="validation-filter")
def test_filter_spec_empty_field(benchmark: Any) -> None:
    """FilterSpec with empty field name (still valid Pydantic)."""
    benchmark(FilterSpec, field="", operator="eq", value=None)


# ================================================================
# Group 4: Sort spec validation speed
# ================================================================


@pytest.mark.benchmark(group="validation-sort")
def test_valid_sort_spec(benchmark: Any) -> None:
    """Creating valid SortSpec."""
    benchmark(SortSpec, field="name")


@pytest.mark.benchmark(group="validation-sort")
def test_sort_spec_desc(benchmark: Any) -> None:
    """Creating SortSpec with explicit direction."""
    benchmark(SortSpec, field="age", direction=SortDirection.DESC)


# ================================================================
# Group 5: Search spec validation speed
# ================================================================


@pytest.mark.benchmark(group="validation-search")
def test_valid_search_spec(benchmark: Any) -> None:
    """Creating valid SearchSpec."""
    benchmark(SearchSpec, query="alice", fields=("name", "email"))


@pytest.mark.benchmark(group="validation-search")
def test_search_spec_many_fields(benchmark: Any) -> None:
    """SearchSpec with many search fields."""
    fields = ("name", "email", "age", "active", "id")
    benchmark(SearchSpec, query="test", fields=fields)


# ================================================================
# Group 6: FastAPI filter error responses
# ================================================================


@pytest.mark.benchmark(group="fastapi-error-filter")
def test_fastapi_valid_filter_request(benchmark: Any) -> None:
    """Valid filter request through FastAPI."""

    def run() -> None:
        resp = _client.get("/filter?age_gte=30&page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-error-filter")
def test_fastapi_invalid_filter_param(benchmark: Any) -> None:
    """Invalid filter param (non-int) through FastAPI -> 422."""

    def run() -> None:
        resp = _client.get("/filter?age_gte=invalid&page=1&limit=20")
        assert resp.status_code == 422

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-error-filter")
def test_fastapi_filter_invalid_page(benchmark: Any) -> None:
    """Valid filter but invalid page=0 -> 422."""

    def run() -> None:
        resp = _client.get("/filter?age_gte=30&page=0&limit=20")
        assert resp.status_code == 422

    benchmark(run)


# ================================================================
# Group 7: FastAPI sort error responses
# ================================================================


@pytest.mark.benchmark(group="fastapi-error-sort")
def test_fastapi_valid_sort_request(benchmark: Any) -> None:
    """Valid sort request through FastAPI."""

    def run() -> None:
        resp = _client.get("/sort?sort_field=age&page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-error-sort")
def test_fastapi_sort_invalid_limit(benchmark: Any) -> None:
    """Sort with invalid limit=5000 -> 422."""

    def run() -> None:
        resp = _client.get("/sort?sort_field=age&page=1&limit=5000")
        assert resp.status_code == 422

    benchmark(run)


# ================================================================
# Group 8: FastAPI search error responses
# ================================================================


@pytest.mark.benchmark(group="fastapi-error-search")
def test_fastapi_valid_search_request(benchmark: Any) -> None:
    """Valid search request through FastAPI."""

    def run() -> None:
        resp = _client.get("/search?q=User_5&page=1&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-error-search")
def test_fastapi_search_invalid_page(benchmark: Any) -> None:
    """Search with invalid page=0 -> 422."""

    def run() -> None:
        resp = _client.get("/search?q=User_5&page=0&limit=20")
        assert resp.status_code == 422

    benchmark(run)
