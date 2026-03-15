"""FastAPI integration tests — real app with real pagination."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pypaginate import paginate
from pypaginate.adapters.fastapi import OffsetDep


# -- Sync memory FastAPI app ------------------------------------------------


def _build_memory_app() -> FastAPI:
    """Build a FastAPI app that paginates an in-memory list."""
    app = FastAPI()
    users = [{"id": i, "name": f"User_{i}", "email": f"u{i}@test.com"} for i in range(50)]

    @app.get("/users")
    def get_users(params: OffsetDep) -> dict:  # type: ignore[type-arg]
        page = paginate(users, params)
        return page.model_dump()

    return app


_memory_app = _build_memory_app()
_memory_client = TestClient(_memory_app)


def test_fastapi_offset_returns_page() -> None:
    """GET /users?page=1&limit=10 returns correct page."""
    response = _memory_client.get("/users?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 50
    assert len(data["items"]) == 10
    assert data["page"] == 1


def test_fastapi_default_params() -> None:
    """GET /users with no params uses defaults (page=1, limit=20)."""
    response = _memory_client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 20


def test_fastapi_second_page() -> None:
    """GET /users?page=2&limit=10 returns second page."""
    response = _memory_client.get("/users?page=2&limit=10")
    data = response.json()
    assert data["page"] == 2
    assert data["has_previous"] is True
    assert len(data["items"]) == 10


def test_fastapi_last_page() -> None:
    """Last page has has_next=False."""
    response = _memory_client.get("/users?page=5&limit=10")
    data = response.json()
    assert data["has_next"] is False
    assert data["page"] == 5


def test_fastapi_response_schema() -> None:
    """Response JSON has all OffsetPage fields."""
    response = _memory_client.get("/users?page=1&limit=5")
    data = response.json()
    required = {"items", "total", "page", "limit", "has_next", "has_previous", "pages"}
    assert required.issubset(data.keys())


# -- Async SQLAlchemy FastAPI app -------------------------------------------


@pytest.fixture()
async def sa_app_client():
    """Build a FastAPI app backed by async SQLAlchemy."""
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
        for i in range(30):
            session.add(User(id=i + 1, name=f"User_{i + 1}", email=f"u{i + 1}@test.com"))
        await session.commit()

    app = FastAPI()

    @app.get("/db-users")
    async def get_db_users(params: OffsetDep) -> dict:  # type: ignore[type-arg]
        async with factory() as session:
            backend = SQLAlchemyBackend(session)
            query = select(User)
            page = await paginate(query, params, backend=backend)  # type: ignore[misc]
            # Convert ORM objects to dicts for JSON serialization
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

    import httpx

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    await engine.dispose()


async def test_fastapi_with_sqlalchemy(sa_app_client) -> None:  # type: ignore[no-untyped-def]
    """FastAPI + async SQLAlchemy returns correct page."""
    response = await sa_app_client.get("/db-users?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 30
    assert len(data["items"]) == 10


async def test_fastapi_sa_pagination_across_pages(sa_app_client) -> None:  # type: ignore[no-untyped-def]
    """All pages from SA-backed endpoint collect all items."""
    collected = 0
    page_num = 1
    limit = 10

    while True:
        response = await sa_app_client.get(f"/db-users?page={page_num}&limit={limit}")
        data = response.json()
        collected += len(data["items"])
        if not data["has_next"]:
            break
        page_num += 1

    assert collected == 30
