"""FastAPI E2E flows — full user journeys through HTTP endpoints.

Tests iterate pages, combine filter + sort + paginate, and verify
data completeness through the HTTP layer.
"""

from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pypaginate import (
    CursorPage,
    CursorParams,
    FilterSpec,
    SortDirection,
    SortSpec,
    paginate,
)
from pypaginate.adapters.fastapi import CursorDep, OffsetDep
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline


# -- Data & app factories ---------------------------------------------------


_TOTAL = 30


def _make_users(count: int = _TOTAL) -> list[dict[str, object]]:
    return [
        {"id": i, "name": f"User_{i}", "age": 20 + (i % 40), "email": f"u{i}@test.com"}
        for i in range(1, count + 1)
    ]


def _build_flow_app(data: list[dict[str, object]]) -> FastAPI:
    """App with offset, cursor, filter, and sort endpoints."""
    app = FastAPI()
    fb = MemoryFilterBackend()
    sb = MemorySortBackend()

    @app.get("/users")
    def get_users(params: OffsetDep) -> dict[str, object]:
        page = paginate(data, params)
        return page.model_dump()

    @app.get("/scroll")
    def scroll(params: CursorDep) -> dict[str, object]:
        return _cursor_over_list(data, params)

    @app.get("/filtered")
    def filtered(
        params: OffsetDep,
        age_gte: int | None = None,
        name_contains: str | None = None,
    ) -> dict[str, object]:
        filters = _build_filters(age_gte, name_contains)
        from pypaginate.adapters.memory.backend import MemoryBackend

        pag: Paginator[dict[str, object]] = Paginator(MemoryBackend())  # type: ignore[type-arg]
        pipe: SyncPipeline[dict[str, object]] = SyncPipeline(pag, filter_backend=fb)  # type: ignore[type-arg]
        page = pipe.execute(data, params, filters=filters)
        return page.model_dump()

    @app.get("/sorted")
    def sorted_users(
        params: OffsetDep,
        sort: str = "name",
        direction: str = "asc",
    ) -> dict[str, object]:
        from pypaginate.adapters.memory.backend import MemoryBackend

        sort_dir = SortDirection.DESC if direction == "desc" else SortDirection.ASC
        sorting = [SortSpec(field=sort, direction=sort_dir)]
        pag: Paginator[dict[str, object]] = Paginator(MemoryBackend())  # type: ignore[type-arg]
        pipe: SyncPipeline[dict[str, object]] = SyncPipeline(pag, sort_backend=sb)  # type: ignore[type-arg]
        page = pipe.execute(data, params, sorting=sorting)
        return page.model_dump()

    @app.get("/combined")
    def combined(
        params: OffsetDep,
        age_gte: int | None = None,
        sort: str = "name",
        direction: str = "asc",
    ) -> dict[str, object]:
        from pypaginate.adapters.memory.backend import MemoryBackend

        filters = _build_age_filter(age_gte)
        sort_dir = SortDirection.DESC if direction == "desc" else SortDirection.ASC
        sorting = [SortSpec(field=sort, direction=sort_dir)]
        pag: Paginator[dict[str, object]] = Paginator(MemoryBackend())  # type: ignore[type-arg]
        pipe: SyncPipeline[dict[str, object]] = SyncPipeline(
            pag,
            filter_backend=fb,
            sort_backend=sb,
        )  # type: ignore[type-arg]
        page = pipe.execute(data, params, filters=filters, sorting=sorting)
        return page.model_dump()

    return app


def _build_filters(
    age_gte: int | None,
    name_contains: str | None,
) -> list[FilterSpec]:
    filters: list[FilterSpec] = []
    if age_gte is not None:
        filters.append(FilterSpec(field="age", operator="gte", value=age_gte))
    if name_contains is not None:
        filters.append(FilterSpec(field="name", operator="contains", value=name_contains))
    return filters


def _build_age_filter(age_gte: int | None) -> list[FilterSpec]:
    if age_gte is None:
        return []
    return [FilterSpec(field="age", operator="gte", value=age_gte)]


def _cursor_over_list(
    data: list[dict[str, object]],
    params: CursorParams,
) -> dict[str, object]:
    start = int(params.after) if params.after else 0
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


# -- Shared client -----------------------------------------------------------


_users = _make_users()
_client = TestClient(_build_flow_app(_users))


# ============================================================================
# Full pagination walk
# ============================================================================


class TestPaginateAllPages:
    """Walk all pages via HTTP, verify completeness."""

    def test_offset_walk_collects_all(self) -> None:
        """Iterate pages until has_next=false, verify total items."""
        limit = 7
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            resp = _client.get(f"/users?page={page_num}&limit={limit}")
            assert resp.status_code == 200
            data = resp.json()
            collected.extend(data["items"])
            if not data["has_next"]:
                break
            page_num += 1

        assert len(collected) == _TOTAL

    def test_cursor_walk_collects_all(self) -> None:
        """Iterate via cursor until has_next=false."""
        limit = 7
        collected: list[dict[str, object]] = []
        cursor: str | None = None

        while True:
            url = f"/scroll?limit={limit}"
            if cursor:
                url += f"&after={cursor}"
            resp = _client.get(url)
            assert resp.status_code == 200
            data = resp.json()
            collected.extend(data["items"])
            if not data["has_next"]:
                break
            cursor = data["next_cursor"]

        assert len(collected) == _TOTAL

    def test_no_duplicate_items_across_pages(self) -> None:
        """Items across offset pages are unique by id."""
        limit = 5
        seen_ids: set[int] = set()
        page_num = 1

        while True:
            resp = _client.get(f"/users?page={page_num}&limit={limit}")
            data = resp.json()
            for item in data["items"]:
                assert item["id"] not in seen_ids
                seen_ids.add(item["id"])
            if not data["has_next"]:
                break
            page_num += 1

        assert len(seen_ids) == _TOTAL


# ============================================================================
# Filter via query params
# ============================================================================


class TestFilterViaHttp:
    """Filter through HTTP query parameters."""

    def test_filter_age_gte(self) -> None:
        """?age_gte=50 returns only users with age >= 50."""
        resp = _client.get("/filtered?page=1&limit=100&age_gte=50")
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["age"] >= 50

    def test_filter_name_contains(self) -> None:
        """?name_contains=User_1 returns matching users."""
        resp = _client.get("/filtered?page=1&limit=100&name_contains=User_1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for item in data["items"]:
            assert "User_1" in str(item["name"])

    def test_filter_returns_empty(self) -> None:
        """Filter that matches nothing returns empty items."""
        resp = _client.get("/filtered?page=1&limit=10&age_gte=999")
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []


# ============================================================================
# Sort via query params
# ============================================================================


class TestSortViaHttp:
    """Sort through HTTP query parameters."""

    def test_sort_by_name_asc(self) -> None:
        resp = _client.get("/sorted?page=1&limit=100&sort=name&direction=asc")
        data = resp.json()
        names = [item["name"] for item in data["items"]]
        assert names == sorted(names)

    def test_sort_by_id_desc(self) -> None:
        resp = _client.get("/sorted?page=1&limit=100&sort=id&direction=desc")
        data = resp.json()
        ids = [item["id"] for item in data["items"]]
        assert ids == sorted(ids, reverse=True)


# ============================================================================
# Combined flow: filter + sort + paginate
# ============================================================================


class TestCombinedFlow:
    """Filter + sort + paginate in a single HTTP request."""

    def test_filter_sort_paginate(self) -> None:
        resp = _client.get("/combined?page=1&limit=100&age_gte=30&sort=age&direction=asc")
        assert resp.status_code == 200
        data = resp.json()
        ages = [item["age"] for item in data["items"]]
        assert all(a >= 30 for a in ages)
        assert ages == sorted(ages)

    def test_combined_walk_all_pages(self) -> None:
        """Walk filtered+sorted results across pages."""
        limit = 3
        collected: list[dict[str, object]] = []
        page_num = 1

        while True:
            resp = _client.get(
                f"/combined?page={page_num}&limit={limit}&age_gte=40&sort=id&direction=asc"
            )
            data = resp.json()
            collected.extend(data["items"])
            if not data["has_next"]:
                break
            page_num += 1

        # Verify filter applied
        for item in collected:
            assert item["age"] >= 40
        # Verify sort applied
        ids = [item["id"] for item in collected]
        assert ids == sorted(ids)
        # Verify completeness
        assert len(collected) == data["total"]


# ============================================================================
# SA async E2E flow
# ============================================================================


@pytest.fixture()
async def sa_flow_client():
    """Async SA app for E2E flow testing."""
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
        for i in range(1, 26):
            session.add(User(id=i, name=f"User_{i}", email=f"u{i}@test.com"))
        await session.commit()

    app = FastAPI()

    @app.get("/db-users")
    async def get_db_users(params: OffsetDep) -> dict[str, object]:
        async with factory() as session:
            backend = SQLAlchemyBackend(session)
            page = await paginate(select(User), params, backend=backend)  # type: ignore[misc]
            items = [{"id": u.id, "name": u.name} for u in page.items]
            return {
                "items": items,
                "total": page.total,
                "page": page.page,
                "limit": page.limit,
                "has_next": page.has_next,
                "has_previous": page.has_previous,
            }

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    await engine.dispose()


async def test_sa_walk_all_pages(sa_flow_client: httpx.AsyncClient) -> None:
    """Iterate all SA-backed pages via HTTP until done."""
    limit = 7
    collected: list[dict[str, object]] = []
    page_num = 1

    while True:
        resp = await sa_flow_client.get(f"/db-users?page={page_num}&limit={limit}")
        assert resp.status_code == 200
        data = resp.json()
        collected.extend(data["items"])
        if not data["has_next"]:
            break
        page_num += 1

    assert len(collected) == 25
