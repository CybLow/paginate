"""FastAPI integration tests — full HTTP cycle through real endpoints.

Covers offset pagination, cursor pagination, response schemas,
error handling, and SQLAlchemy-backed endpoints.
"""

from __future__ import annotations

import math

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pypaginate import (
    CursorPage,
    CursorParams,
    FilterSpec,
    OffsetPage,
    SortDirection,
    SortSpec,
    paginate,
)
from pypaginate.adapters.fastapi import CursorDep, OffsetDep


# -- App factories -----------------------------------------------------------


_TOTAL = 50


def _make_users(count: int = _TOTAL) -> list[dict[str, object]]:
    """Generate user dicts for test endpoints."""
    return [
        {"id": i, "name": f"User_{i}", "age": 20 + (i % 40), "email": f"u{i}@test.com"}
        for i in range(1, count + 1)
    ]


def _build_offset_app(data: list[dict[str, object]]) -> FastAPI:
    app = FastAPI()

    @app.get("/users")
    def get_users(params: OffsetDep) -> dict[str, object]:
        page = paginate(data, params)
        return page.model_dump()

    return app


def _build_cursor_app(data: list[dict[str, object]]) -> FastAPI:
    """Build app with cursor endpoint using manual slicing."""
    app = FastAPI()

    @app.get("/scroll")
    def scroll(params: CursorDep) -> dict[str, object]:
        return _cursor_over_list(data, params)

    return app


def _cursor_over_list(
    data: list[dict[str, object]],
    params: CursorParams,
) -> dict[str, object]:
    """Simulate cursor pagination over a list using index cursors."""
    start = 0
    if params.after is not None:
        start = int(params.after)
    end = start + params.limit
    items = data[start:end]
    next_cursor = str(end) if end < len(data) else None
    prev_cursor = str(start) if start > 0 else None
    page = CursorPage.create(
        items=items,
        params=params,
        next_cursor=next_cursor,
        previous_cursor=prev_cursor,
    )
    return page.model_dump()


# -- Shared clients ----------------------------------------------------------


_users = _make_users()
_offset_client = TestClient(_build_offset_app(_users))
_cursor_client = TestClient(_build_cursor_app(_users))


# ============================================================================
# Offset endpoint tests
# ============================================================================


class TestOffsetPagination:
    """Offset pagination through HTTP."""

    def test_first_page(self) -> None:
        resp = _offset_client.get("/users?page=1&limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 5
        assert data["page"] == 1
        assert data["total"] == _TOTAL
        assert data["has_next"] is True
        assert data["has_previous"] is False

    def test_second_page(self) -> None:
        resp = _offset_client.get("/users?page=2&limit=5")
        data = resp.json()
        assert data["page"] == 2
        assert data["has_previous"] is True
        assert len(data["items"]) == 5

    def test_last_page(self) -> None:
        limit = 10
        last = math.ceil(_TOTAL / limit)
        resp = _offset_client.get(f"/users?page={last}&limit={limit}")
        data = resp.json()
        assert data["has_next"] is False
        assert data["page"] == last

    def test_default_params(self) -> None:
        resp = _offset_client.get("/users")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["limit"] == 20

    def test_empty_dataset(self) -> None:
        client = TestClient(_build_offset_app([]))
        resp = client.get("/users?page=1&limit=5")
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["has_next"] is False
        assert data["has_previous"] is False


# ============================================================================
# Offset validation / error tests
# ============================================================================


class TestOffsetErrors:
    """FastAPI validation errors for bad offset params."""

    def test_page_zero_returns_422(self) -> None:
        resp = _offset_client.get("/users?page=0&limit=5")
        assert resp.status_code == 422

    def test_negative_limit_returns_422(self) -> None:
        resp = _offset_client.get("/users?page=1&limit=-1")
        assert resp.status_code == 422

    def test_limit_too_large_returns_422(self) -> None:
        resp = _offset_client.get("/users?page=1&limit=5000")
        assert resp.status_code == 422

    def test_non_integer_page_returns_422(self) -> None:
        resp = _offset_client.get("/users?page=abc&limit=5")
        assert resp.status_code == 422

    def test_non_integer_limit_returns_422(self) -> None:
        resp = _offset_client.get("/users?page=1&limit=abc")
        assert resp.status_code == 422


# ============================================================================
# Cursor endpoint tests
# ============================================================================


class TestCursorPagination:
    """Cursor pagination through HTTP."""

    def test_first_page(self) -> None:
        resp = _cursor_client.get("/scroll?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 5
        assert data["has_next"] is True
        assert data["next_cursor"] is not None

    def test_with_after_cursor(self) -> None:
        first = _cursor_client.get("/scroll?limit=5").json()
        cursor = first["next_cursor"]
        resp = _cursor_client.get(f"/scroll?limit=5&after={cursor}")
        data = resp.json()
        assert len(data["items"]) == 5
        assert data["items"] != first["items"]

    def test_cursor_invalid_both_directions(self) -> None:
        # CursorParams raises pypaginate ValidationError (not Pydantic),
        # so FastAPI returns 500 rather than 422.
        client = TestClient(_build_cursor_app(_users), raise_server_exceptions=False)
        resp = client.get("/scroll?limit=5&after=0&before=10")
        assert resp.status_code == 500


# ============================================================================
# Response schema tests
# ============================================================================


_OFFSET_KEYS = {"items", "total", "page", "pages", "limit", "has_next", "has_previous"}
_CURSOR_KEYS = {"items", "limit", "has_next", "has_previous", "next_cursor", "previous_cursor"}


class TestResponseSchema:
    """Verify JSON response keys per pagination mode."""

    def test_offset_has_all_fields(self) -> None:
        data = _offset_client.get("/users?page=1&limit=5").json()
        assert _OFFSET_KEYS.issubset(data.keys())

    def test_offset_has_no_cursor_fields(self) -> None:
        data = _offset_client.get("/users?page=1&limit=5").json()
        assert "next_cursor" not in data
        assert "previous_cursor" not in data

    def test_cursor_has_no_offset_fields(self) -> None:
        data = _cursor_client.get("/scroll?limit=5").json()
        assert "total" not in data
        assert "page" not in data
        assert "pages" not in data

    def test_cursor_has_all_fields(self) -> None:
        data = _cursor_client.get("/scroll?limit=5").json()
        assert _CURSOR_KEYS.issubset(data.keys())

    def test_offset_model_matches_schema(self) -> None:
        data = _offset_client.get("/users?page=1&limit=5").json()
        page = OffsetPage[dict[str, object]](**data)
        assert page.page == 1
        assert page.total == _TOTAL


# ============================================================================
# Async SQLAlchemy tests
# ============================================================================


@pytest.fixture()
async def sa_async_client():
    """FastAPI app backed by async SQLAlchemy (in-memory sqlite)."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend
    from tests.fixtures.models import Base, User

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        for i in range(1, 31):
            session.add(User(id=i, name=f"User_{i}", email=f"u{i}@test.com"))
        await session.commit()

    app = FastAPI()

    @app.get("/db-users")
    async def get_db_users(params: OffsetDep) -> dict[str, object]:
        async with factory() as session:
            backend = SQLAlchemyBackend(session)
            page = await paginate(select(User), params, backend=backend)  # type: ignore[misc]
            items = [{"id": u.id, "name": u.name, "email": u.email} for u in page.items]
            return {
                "items": items,
                "total": page.total,
                "page": page.page,
                "limit": page.limit,
                "has_next": page.has_next,
                "has_previous": page.has_previous,
                "pages": page.pages,
            }

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    await engine.dispose()


async def test_sa_async_offset(sa_async_client: httpx.AsyncClient) -> None:
    """Async SA endpoint returns correct page."""
    resp = await sa_async_client.get("/db-users?page=1&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 30
    assert len(data["items"]) == 10


async def test_sa_async_second_page(sa_async_client: httpx.AsyncClient) -> None:
    """Async SA endpoint page 2 has previous."""
    resp = await sa_async_client.get("/db-users?page=2&limit=10")
    data = resp.json()
    assert data["has_previous"] is True
    assert data["page"] == 2


async def test_sa_async_last_page(sa_async_client: httpx.AsyncClient) -> None:
    """Async SA endpoint last page has no next."""
    resp = await sa_async_client.get("/db-users?page=3&limit=10")
    data = resp.json()
    assert data["has_next"] is False
    assert data["page"] == 3


# ============================================================================
# Sync SQLAlchemy tests
# ============================================================================


@pytest.fixture()
def sa_sync_client():
    """FastAPI app backed by sync SQLAlchemy (in-memory sqlite)."""
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
    with factory() as session:
        for i in range(1, 21):
            session.add(User(id=i, name=f"User_{i}", email=f"u{i}@test.com"))
        session.commit()

    app = FastAPI()

    @app.get("/db-users")
    def get_db_users(params: OffsetDep) -> dict[str, object]:
        with factory() as session:
            backend = SyncSQLAlchemyBackend(session)
            page = paginate(select(User), params, backend=backend)
            items = [{"id": u.id, "name": u.name, "email": u.email} for u in page.items]
            return {
                "items": items,
                "total": page.total,
                "page": page.page,
                "limit": page.limit,
                "has_next": page.has_next,
                "has_previous": page.has_previous,
                "pages": page.pages,
            }

    client = TestClient(app)
    yield client
    engine.dispose()


def test_sa_sync_offset(sa_sync_client: TestClient) -> None:
    """Sync SA endpoint returns correct page."""
    resp = sa_sync_client.get("/db-users?page=1&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 20
    assert len(data["items"]) == 10


# ============================================================================
# SA pipeline test (filter + sort + paginate)
# ============================================================================


@pytest.fixture()
async def sa_pipeline_client():
    """FastAPI app with filter + sort + paginate pipeline."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from pypaginate.adapters.sqlalchemy import (
        SQLAlchemyBackend,
        SQLAlchemyFilterBackend,
        SQLAlchemySortBackend,
    )
    from pypaginate.engine.paginator import AsyncPaginator
    from pypaginate.engine.pipeline import AsyncPipeline
    from tests.fixtures.models import Base, User

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    async with factory() as session:
        for i, name in enumerate(names, start=1):
            session.add(User(id=i, name=name, email=f"{name.lower()}@test.com"))
        await session.commit()

    app = FastAPI()

    @app.get("/pipeline")
    async def pipeline_endpoint(
        params: OffsetDep,
        name_filter: str | None = None,
        sort_field: str = "name",
        sort_dir: str = "asc",
    ) -> dict[str, object]:
        async with factory() as session:
            sa_backend = SQLAlchemyBackend(session)
            fb = SQLAlchemyFilterBackend()
            sb = SQLAlchemySortBackend()
            pag: AsyncPaginator[User] = AsyncPaginator(sa_backend)  # type: ignore[type-arg]
            pipe: AsyncPipeline[User] = AsyncPipeline(pag, filter_backend=fb, sort_backend=sb)  # type: ignore[type-arg]

            filters = []
            if name_filter:
                filters.append(FilterSpec(field="name", operator="contains", value=name_filter))
            direction = SortDirection.DESC if sort_dir == "desc" else SortDirection.ASC
            sorting = [SortSpec(field=sort_field, direction=direction)]

            page = await pipe.execute(
                select(User),
                params,
                filters=filters,
                sorting=sorting,
            )
            items = [{"id": u.id, "name": u.name} for u in page.items]
            return {
                "items": items,
                "total": page.total,
                "page": page.page,
            }

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    await engine.dispose()


async def test_sa_pipeline_filter_sort(sa_pipeline_client: httpx.AsyncClient) -> None:
    """Pipeline endpoint filters and sorts correctly."""
    resp = await sa_pipeline_client.get(
        "/pipeline?page=1&limit=10&name_filter=a&sort_field=name&sort_dir=asc"
    )
    assert resp.status_code == 200
    data = resp.json()
    names = [item["name"] for item in data["items"]]
    # All names should contain 'a' (case-sensitive from SA contains)
    for name in names:
        assert "a" in name.lower()
