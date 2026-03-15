"""Benchmark FastAPI full HTTP cycle: TestClient -> routing -> DI -> paginate -> JSON.

Covers ALL operations through the complete HTTP stack, comparing
pypaginate vs fastapi-pagination vs raw FastAPI for every operation.

Groups:
    1. fastapi-paginate  — pure pagination through HTTP
    2. fastapi-filter    — filter through HTTP
    3. fastapi-sort      — sort through HTTP
    4. fastapi-search    — search through HTTP
    5. fastapi-pipeline  — full pipeline through HTTP
    6. fastapi-sa        — SQLAlchemy through HTTP
    7. fastapi-scaling   — scaling through HTTP

Run: uv run pytest tests/perf/test_fastapi_perf.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import Depends, FastAPI, Query
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

try:
    from fastapi_pagination.ext.sqlalchemy import (
        paginate as fp_sa_paginate,
    )

    HAS_FP_SA = True
except ImportError:
    HAS_FP_SA = False

_SKIP_FP = pytest.mark.skipif(
    not HAS_FP,
    reason="fastapi-pagination not installed",
)
_SKIP_FP_SA = pytest.mark.skipif(
    not (HAS_FP and HAS_FP_SA),
    reason="fastapi-pagination[sqlalchemy] not installed",
)


# -- Module-level data (generated once) ----------------------------

_DATA_1K = make_users(1_000)
_DATA_10K = make_users(10_000)
_DATA_100K = make_users(100_000)


# -- Helper: build memory pipeline --------------------------------


def _build_pipeline(
    data: list[dict[str, Any]],
) -> SyncPipeline[Any]:
    """Build a sync memory pipeline for filter/sort/search."""
    backend = MemoryBackend()
    pag: Paginator[Any] = Paginator(backend)
    return SyncPipeline(
        pag,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
        search_backend=MemorySearchBackend(),
    )


# -- pypaginate apps (module-level, reused) ------------------------


def _build_pp_paginate_app(data: list[dict[str, Any]]) -> FastAPI:
    """App with offset pagination endpoint."""
    app = FastAPI()

    @app.get("/users")
    def get_users(params: OffsetDep) -> dict[str, object]:
        return paginate(data, params).model_dump()

    return app


def _build_pp_filter_app(data: list[dict[str, Any]]) -> FastAPI:
    """App with filter endpoint."""
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


def _build_pp_sort_app(data: list[dict[str, Any]]) -> FastAPI:
    """App with sort endpoint."""
    app = FastAPI()
    pipe = _build_pipeline(data)

    @app.get("/sort")
    def sort_users(
        params: OffsetDep,
        sort_field: str = Query("age"),
        sort_dir: str = Query("asc"),
    ) -> dict[str, object]:
        direction = SortDirection.DESC if sort_dir == "desc" else SortDirection.ASC
        sorting = [SortSpec(field=sort_field, direction=direction)]
        return pipe.execute(data, params, sorting=sorting).model_dump()

    return app


def _build_pp_search_app(data: list[dict[str, Any]]) -> FastAPI:
    """App with search endpoint."""
    app = FastAPI()
    pipe = _build_pipeline(data)

    @app.get("/search")
    def search_users(
        params: OffsetDep,
        q: str = Query("User_5"),
    ) -> dict[str, object]:
        spec = SearchSpec(query=q, fields=("name", "email"))
        return pipe.execute(data, params, search=spec).model_dump()

    return app


def _build_pp_pipeline_app(data: list[dict[str, Any]]) -> FastAPI:
    """App with full pipeline (filter+sort+paginate)."""
    app = FastAPI()
    pipe = _build_pipeline(data)

    @app.get("/pipeline")
    def pipeline_users(
        params: OffsetDep,
        age_gte: int = Query(30),
        sort_field: str = Query("name"),
    ) -> dict[str, object]:
        filters = [FilterSpec(field="age", operator="gte", value=age_gte)]
        sorting = [SortSpec(field=sort_field)]
        return pipe.execute(
            data,
            params,
            filters=filters,
            sorting=sorting,
        ).model_dump()

    return app


# -- fp apps (module-level, guarded) -------------------------------


def _build_fp_paginate_app(data: list[dict[str, Any]]) -> FastAPI:
    """fastapi-pagination app for comparison."""
    app = FastAPI()

    @app.get("/users", response_model=Page[dict[str, Any]])  # type: ignore[type-arg]
    def get_users(params: Params = Params()) -> Any:  # type: ignore[assignment]
        return fp_paginate(data, params)  # type: ignore[arg-type]

    add_pagination(app)
    return app


def _build_fp_pipeline_app(data: list[dict[str, Any]]) -> FastAPI:
    """fp app: manual filter+sort, then fp paginate."""
    app = FastAPI()

    @app.get("/pipeline", response_model=Page[dict[str, Any]])  # type: ignore[type-arg]
    def pipeline_users(
        params: Params = Params(),
        age_gte: int = Query(30),
        sort_field: str = Query("name"),
    ) -> Any:
        filtered = [u for u in data if u["age"] >= age_gte]
        sorted_items = sorted(filtered, key=lambda u: u[sort_field])
        return fp_paginate(sorted_items, params)  # type: ignore[arg-type]

    add_pagination(app)
    return app


# -- Raw apps (module-level) ---------------------------------------


def _build_raw_paginate_app(data: list[dict[str, Any]]) -> FastAPI:
    """Raw FastAPI: manual slice, manual dict response."""
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


def _build_raw_filter_app(data: list[dict[str, Any]]) -> FastAPI:
    """Raw FastAPI: manual list comprehension filter."""
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
            "page": page,
        }

    return app


def _build_raw_sort_app(data: list[dict[str, Any]]) -> FastAPI:
    """Raw FastAPI: manual sorted()."""
    app = FastAPI()

    @app.get("/sort")
    def sort_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
        sort_field: str = Query("age"),
    ) -> dict[str, object]:
        sorted_items = sorted(data, key=lambda u: u[sort_field])
        offset = (page - 1) * limit
        return {
            "items": sorted_items[offset : offset + limit],
            "total": len(sorted_items),
            "page": page,
        }

    return app


def _build_raw_search_app(data: list[dict[str, Any]]) -> FastAPI:
    """Raw FastAPI: manual string matching."""
    app = FastAPI()

    @app.get("/search")
    def search_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
        q: str = Query("User_5"),
    ) -> dict[str, object]:
        query_lower = q.lower()
        matched = [
            u for u in data if query_lower in u["name"].lower() or query_lower in u["email"].lower()
        ]
        offset = (page - 1) * limit
        return {
            "items": matched[offset : offset + limit],
            "total": len(matched),
            "page": page,
        }

    return app


def _build_raw_pipeline_app(data: list[dict[str, Any]]) -> FastAPI:
    """Raw FastAPI: manual filter+sort+slice."""
    app = FastAPI()

    @app.get("/pipeline")
    def pipeline_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
        age_gte: int = Query(30),
        sort_field: str = Query("name"),
    ) -> dict[str, object]:
        filtered = [u for u in data if u["age"] >= age_gte]
        sorted_items = sorted(filtered, key=lambda u: u[sort_field])
        offset = (page - 1) * limit
        return {
            "items": sorted_items[offset : offset + limit],
            "total": len(sorted_items),
            "page": page,
        }

    return app


# -- SA apps (module-level, sync for benchmark simplicity) ---------


def _build_pp_sa_app() -> tuple[FastAPI, Any]:
    """pypaginate + sync SQLAlchemy through HTTP."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.pool import StaticPool

    from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyBackend
    from tests.fixtures.models import Base, User

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, class_=Session, expire_on_commit=False)

    with factory() as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    app = FastAPI()

    @app.get("/users")
    def get_users(params: OffsetDep) -> dict[str, object]:
        with factory() as s:
            backend = SyncSQLAlchemyBackend(s)
            page = paginate(select(User), params, backend=backend)
            items = [{"id": u.id, "name": u.name, "email": u.email} for u in page.items]
            return {
                "items": items,
                "total": page.total,
                "page": page.page,
                "limit": page.limit,
            }

    return app, engine


def _build_raw_sa_app() -> tuple[FastAPI, Any]:
    """Raw FastAPI + raw SQLAlchemy."""
    from sqlalchemy import create_engine, func, select
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.pool import StaticPool

    from tests.fixtures.models import Base, User

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, class_=Session, expire_on_commit=False)

    with factory() as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    app = FastAPI()

    @app.get("/users")
    def get_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1),
    ) -> dict[str, object]:
        with factory() as s:
            total = s.execute(
                select(func.count()).select_from(User),
            ).scalar_one()
            offset = (page - 1) * limit
            items = [
                {"id": u.id, "name": u.name, "email": u.email}
                for u in s.execute(
                    select(User).offset(offset).limit(limit),
                ).scalars()
            ]
            return {
                "items": items,
                "total": total,
                "page": page,
                "limit": limit,
            }

    return app, engine


def _build_fp_sa_app() -> tuple[FastAPI, Any]:
    """fastapi-pagination + SA extension through HTTP."""
    from pydantic import BaseModel, ConfigDict
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.pool import StaticPool

    from tests.fixtures.models import Base, User

    class UserOut(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        name: str
        email: str

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, class_=Session, expire_on_commit=False)

    with factory() as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    app = FastAPI()

    def _get_db():  # type: ignore[no-untyped-def]
        with factory() as s:
            yield s

    @app.get("/users", response_model=Page[UserOut])  # type: ignore[type-arg]
    def get_users(db: Session = Depends(_get_db)) -> Any:  # type: ignore[assignment]
        return fp_sa_paginate(db, select(User))  # type: ignore[arg-type]

    add_pagination(app)
    return app, engine


# -- Create module-level clients (once, reused) --------------------

# Group 1-5: memory-backed clients
_pp_paginate_client = TestClient(_build_pp_paginate_app(_DATA_10K))
_pp_filter_client = TestClient(_build_pp_filter_app(_DATA_10K))
_pp_sort_client = TestClient(_build_pp_sort_app(_DATA_10K))
_pp_search_client = TestClient(_build_pp_search_app(_DATA_10K))
_pp_pipeline_client = TestClient(_build_pp_pipeline_app(_DATA_10K))

_raw_paginate_client = TestClient(_build_raw_paginate_app(_DATA_10K))
_raw_filter_client = TestClient(_build_raw_filter_app(_DATA_10K))
_raw_sort_client = TestClient(_build_raw_sort_app(_DATA_10K))
_raw_search_client = TestClient(_build_raw_search_app(_DATA_10K))
_raw_pipeline_client = TestClient(_build_raw_pipeline_app(_DATA_10K))

# Group 6: SA-backed clients
_pp_sa_app, _pp_sa_engine = _build_pp_sa_app()
_pp_sa_client = TestClient(_pp_sa_app)

_raw_sa_app, _raw_sa_engine = _build_raw_sa_app()
_raw_sa_client = TestClient(_raw_sa_app)

# Group 7: scaling clients
_pp_1k_client = TestClient(_build_pp_paginate_app(_DATA_1K))
_pp_100k_client = TestClient(_build_pp_paginate_app(_DATA_100K))

# fp clients (guarded)
_fp_paginate_client: TestClient | None = None
_fp_pipeline_client: TestClient | None = None
_fp_sa_client: TestClient | None = None
_fp_sa_engine: Any = None

if HAS_FP:
    _fp_paginate_client = TestClient(_build_fp_paginate_app(_DATA_10K))
    _fp_pipeline_client = TestClient(_build_fp_pipeline_app(_DATA_10K))

if HAS_FP and HAS_FP_SA:
    _fp_sa_app, _fp_sa_engine = _build_fp_sa_app()
    _fp_sa_client = TestClient(_fp_sa_app)


# ================================================================
# Group 1: fastapi-paginate — pure pagination through HTTP
# ================================================================


@pytest.mark.benchmark(group="fastapi-paginate")
def test_pypaginate_fastapi_offset_10k(benchmark: Any) -> None:
    """pypaginate offset pagination through full HTTP cycle."""

    def run() -> None:
        resp = _pp_paginate_client.get("/users?page=50&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@_SKIP_FP
@pytest.mark.benchmark(group="fastapi-paginate")
def test_fp_fastapi_offset_10k(benchmark: Any) -> None:
    """fastapi-pagination offset through full HTTP cycle."""
    assert _fp_paginate_client is not None

    def run() -> None:
        resp = _fp_paginate_client.get("/users?page=50&size=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-paginate")
def test_raw_fastapi_offset_10k(benchmark: Any) -> None:
    """Raw FastAPI manual slice through full HTTP cycle."""

    def run() -> None:
        resp = _raw_paginate_client.get("/users?page=50&limit=20")
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 2: fastapi-filter — filter through HTTP
# ================================================================


@pytest.mark.benchmark(group="fastapi-filter")
def test_pypaginate_fastapi_filter_10k(benchmark: Any) -> None:
    """pypaginate FilterSpec through full HTTP cycle."""

    def run() -> None:
        resp = _pp_filter_client.get("/filter?page=1&limit=20&age_gte=30")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-filter")
def test_raw_fastapi_filter_10k(benchmark: Any) -> None:
    """Raw FastAPI manual list comprehension filter."""

    def run() -> None:
        resp = _raw_filter_client.get("/filter?page=1&limit=20&age_gte=30")
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 3: fastapi-sort — sort through HTTP
# ================================================================


@pytest.mark.benchmark(group="fastapi-sort")
def test_pypaginate_fastapi_sort_10k(benchmark: Any) -> None:
    """pypaginate SortSpec through full HTTP cycle."""

    def run() -> None:
        resp = _pp_sort_client.get(
            "/sort?page=1&limit=20&sort_field=age&sort_dir=asc",
        )
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-sort")
def test_raw_fastapi_sort_10k(benchmark: Any) -> None:
    """Raw FastAPI manual sorted() through HTTP."""

    def run() -> None:
        resp = _raw_sort_client.get(
            "/sort?page=1&limit=20&sort_field=age",
        )
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 4: fastapi-search — search through HTTP
# ================================================================


@pytest.mark.benchmark(group="fastapi-search")
def test_pypaginate_fastapi_search_10k(benchmark: Any) -> None:
    """pypaginate SearchSpec through full HTTP cycle."""

    def run() -> None:
        resp = _pp_search_client.get(
            "/search?page=1&limit=20&q=User_5",
        )
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-search")
def test_raw_fastapi_search_10k(benchmark: Any) -> None:
    """Raw FastAPI manual string matching through HTTP."""

    def run() -> None:
        resp = _raw_search_client.get(
            "/search?page=1&limit=20&q=User_5",
        )
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 5: fastapi-pipeline — full pipeline through HTTP
# ================================================================


@pytest.mark.benchmark(group="fastapi-pipeline")
def test_pypaginate_fastapi_pipeline_10k(benchmark: Any) -> None:
    """pypaginate Pipeline (filter+sort+paginate) through HTTP."""

    def run() -> None:
        resp = _pp_pipeline_client.get(
            "/pipeline?page=1&limit=20&age_gte=30&sort_field=name",
        )
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-pipeline")
def test_raw_fastapi_pipeline_10k(benchmark: Any) -> None:
    """Raw FastAPI manual filter+sort+slice through HTTP."""

    def run() -> None:
        resp = _raw_pipeline_client.get(
            "/pipeline?page=1&limit=20&age_gte=30&sort_field=name",
        )
        assert resp.status_code == 200

    benchmark(run)


@_SKIP_FP
@pytest.mark.benchmark(group="fastapi-pipeline")
def test_fp_fastapi_pipeline_10k(benchmark: Any) -> None:
    """fp manual filter+sort, then fp paginate through HTTP."""
    assert _fp_pipeline_client is not None

    def run() -> None:
        resp = _fp_pipeline_client.get(
            "/pipeline?page=1&size=20&age_gte=30&sort_field=name",
        )
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 6: fastapi-sa — SQLAlchemy through HTTP
# ================================================================


@pytest.mark.benchmark(group="fastapi-sa")
def test_pypaginate_fastapi_sa_10k(benchmark: Any) -> None:
    """pypaginate + SyncSQLAlchemyBackend through full HTTP cycle."""

    def run() -> None:
        resp = _pp_sa_client.get("/users?page=50&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-sa")
def test_raw_fastapi_sa_10k(benchmark: Any) -> None:
    """Raw FastAPI + raw SQLAlchemy through full HTTP cycle."""

    def run() -> None:
        resp = _raw_sa_client.get("/users?page=50&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@_SKIP_FP_SA
@pytest.mark.benchmark(group="fastapi-sa")
def test_fp_fastapi_sa_10k(benchmark: Any) -> None:
    """fastapi-pagination SA extension through full HTTP cycle."""
    assert _fp_sa_client is not None

    def run() -> None:
        resp = _fp_sa_client.get("/users?page=50&size=20")
        assert resp.status_code == 200

    benchmark(run)


# ================================================================
# Group 7: fastapi-scaling — scaling through HTTP
# ================================================================


@pytest.mark.benchmark(group="fastapi-scaling")
def test_pypaginate_fastapi_1k(benchmark: Any) -> None:
    """pypaginate through HTTP with 1K items."""

    def run() -> None:
        resp = _pp_1k_client.get("/users?page=5&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-scaling")
def test_pypaginate_fastapi_10k(benchmark: Any) -> None:
    """pypaginate through HTTP with 10K items."""

    def run() -> None:
        resp = _pp_paginate_client.get("/users?page=50&limit=20")
        assert resp.status_code == 200

    benchmark(run)


@pytest.mark.benchmark(group="fastapi-scaling")
def test_pypaginate_fastapi_100k(benchmark: Any) -> None:
    """pypaginate through HTTP with 100K items."""

    def run() -> None:
        resp = _pp_100k_client.get("/users?page=500&limit=20")
        assert resp.status_code == 200

    benchmark(run)
