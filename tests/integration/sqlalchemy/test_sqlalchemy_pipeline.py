"""Integration tests for the full SQLAlchemy async pipeline.

Combines filter, sort, search, and pagination backends
against a real in-memory SQLite database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from pypaginate import (
    FilterSpec,
    OffsetParams,
    SearchSpec,
    SortDirection,
    SortSpec,
)
from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.adapters.sqlalchemy.search import SQLAlchemySearchBackend
from pypaginate.adapters.sqlalchemy.sorting import SQLAlchemySortBackend
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline
from tests.fixtures.models import Product, User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _build_pipeline(session: AsyncSession) -> AsyncPipeline[Product]:
    """Wire up an async pipeline with all SQLAlchemy backends."""
    backend: SQLAlchemyBackend[Product] = SQLAlchemyBackend(session)
    paginator: AsyncPaginator[Product] = AsyncPaginator(backend)
    return AsyncPipeline(
        paginator,
        filter_backend=SQLAlchemyFilterBackend(),
        sort_backend=SQLAlchemySortBackend(),
        search_backend=SQLAlchemySearchBackend(),
    )


async def test_filter_and_sort(seeded_session: AsyncSession) -> None:
    """Filter by category then sort by price DESC."""
    pipeline = _build_pipeline(seeded_session)
    page = await pipeline.execute(
        select(Product),
        OffsetParams(page=1, limit=10),
        filters=[FilterSpec(field="category", operator="eq", value="electronics")],
        sorting=[SortSpec(field="price", direction=SortDirection.DESC)],
    )
    prices = [p.price for p in page.items]
    assert prices == sorted(prices, reverse=True)
    assert all(p.category == "electronics" for p in page.items)


async def test_search_and_filter(seeded_session: AsyncSession) -> None:
    """Search users by name then filter by id > 10."""
    backend: SQLAlchemyBackend[User] = SQLAlchemyBackend(seeded_session)
    paginator: AsyncPaginator[User] = AsyncPaginator(backend)
    pipeline: AsyncPipeline[User] = AsyncPipeline(
        paginator,
        filter_backend=SQLAlchemyFilterBackend(),
        search_backend=SQLAlchemySearchBackend(),
    )
    page = await pipeline.execute(
        select(User),
        OffsetParams(page=1, limit=20),
        filters=[FilterSpec(field="id", operator="gt", value=10)],
        search=SearchSpec(query="User", fields=("name",)),
    )
    assert all(u.id > 10 for u in page.items)


async def test_full_pipeline_all_specs(seeded_session: AsyncSession) -> None:
    """Filter + sort + search combined in one pipeline call."""
    pipeline = _build_pipeline(seeded_session)
    page = await pipeline.execute(
        select(Product),
        OffsetParams(page=1, limit=5),
        filters=[FilterSpec(field="in_stock", operator="eq", value=True)],
        sorting=[SortSpec(field="price", direction=SortDirection.ASC)],
        search=SearchSpec(query="Product", fields=("name",)),
    )
    prices = [p.price for p in page.items]
    assert prices == sorted(prices)
    assert all(p.in_stock for p in page.items)


async def test_pipeline_matches_manual_query(
    seeded_session: AsyncSession,
) -> None:
    """Pipeline result matches a manual SQL query."""
    # Manual query
    backend: SQLAlchemyBackend[Product] = SQLAlchemyBackend(seeded_session)
    fb = SQLAlchemyFilterBackend()
    sb = SQLAlchemySortBackend()
    manual_stmt = fb.apply_filters(
        select(Product),
        [FilterSpec(field="category", operator="eq", value="books")],
    )
    manual_stmt = sb.apply_sorting(
        manual_stmt,
        [SortSpec(field="price", direction=SortDirection.ASC)],
    )
    manual_items = await backend.fetch(manual_stmt, offset=0, limit=10)

    # Pipeline query
    pipeline = _build_pipeline(seeded_session)
    page = await pipeline.execute(
        select(Product),
        OffsetParams(page=1, limit=10),
        filters=[FilterSpec(field="category", operator="eq", value="books")],
        sorting=[SortSpec(field="price", direction=SortDirection.ASC)],
    )
    assert [p.id for p in page.items] == [p.id for p in manual_items]


async def test_pipeline_paginate_subset(seeded_session: AsyncSession) -> None:
    """Pipeline pages through a filtered subset correctly."""
    pipeline = _build_pipeline(seeded_session)
    all_items: list[Product] = []
    page_num = 1
    while True:
        page = await pipeline.execute(
            select(Product),
            OffsetParams(page=page_num, limit=2),
            filters=[
                FilterSpec(field="category", operator="eq", value="electronics"),
            ],
        )
        all_items.extend(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert len(all_items) == 4
    assert all(p.category == "electronics" for p in all_items)
