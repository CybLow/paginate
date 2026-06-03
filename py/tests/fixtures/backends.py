"""BackendEnv registry — canonical test infrastructure.

Every non-unit test parameterises over ``BACKEND_REGISTRY`` so that
memory, SA-async, and SA-sync backends share the same assertions.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from pypaginate._dispatch import paginate
from pypaginate.domain.params import OffsetParams
from pypaginate.engine.paginator import AsyncPaginator, Paginator
from pypaginate.engine.pipeline import AsyncPipeline, SyncPipeline


# -- Canonical seed data (8 users) ------------------------------------------


SEED_DATA: list[dict[str, Any]] = [
    {"id": 1, "name": "Alice", "age": 30, "email": "alice@test.com"},
    {"id": 2, "name": "Bob", "age": 25, "email": "bob@test.com"},
    {"id": 3, "name": "Charlie", "age": 35, "email": "charlie@test.com"},
    {"id": 4, "name": "Diana", "age": 28, "email": "diana@test.com"},
    {"id": 5, "name": "Eve", "age": 22, "email": "eve@test.com"},
    {"id": 6, "name": "Frank", "age": 40, "email": "frank@test.com"},
    {"id": 7, "name": "Grace", "age": 33, "email": "grace@test.com"},
    {"id": 8, "name": "Henry", "age": 27, "email": "henry@test.com"},
]

FIELD_NAMES: tuple[str, ...] = ("id", "name", "age", "email")


# -- Sentinel for required callable fields -----------------------------------


def _required(*_a: object, **_kw: object) -> None:  # pragma: no cover
    msg = "BackendEnv callable field was not set"
    raise NotImplementedError(msg)


# -- BackendEnv dataclass ---------------------------------------------------


@dataclass
class BackendEnv:
    """Everything a test needs to exercise one backend."""

    name: str
    mode: str
    pagination_backend: object
    query: object
    total: int
    field_names: tuple[str, ...] = FIELD_NAMES
    filter_backend: object | None = None
    sort_backend: object | None = None
    search_backend: object | None = None
    get_field: Callable[[object, str], object] = field(
        default=_required,
    )
    do_paginate: Callable[..., Any] = field(default=_required)
    do_filter: Callable[..., Any] = field(default=_required)
    do_sort: Callable[..., Any] = field(default=_required)
    do_search: Callable[..., Any] = field(default=_required)
    do_pipeline: Callable[..., Any] = field(default=_required)
    cleanup: Callable[[], Awaitable[None]] | None = None


# -- Memory setup ------------------------------------------------------------


def _dict_field(item: object, name: str) -> object:
    return item[name]  # type: ignore[index]


async def setup_memory(
    data: list[dict[str, Any]] | None = None,
) -> BackendEnv:
    """Create a BackendEnv for the in-memory backend."""
    from pypaginate.adapters.memory.backend import MemoryBackend
    from pypaginate.adapters.memory.filters import MemoryFilterBackend
    from pypaginate.adapters.memory.search import MemorySearchBackend
    from pypaginate.adapters.memory.sorting import MemorySortBackend

    items = data if data is not None else list(SEED_DATA)
    backend = MemoryBackend()
    fb = MemoryFilterBackend()
    sb = MemorySortBackend()
    srch = MemorySearchBackend()

    paginator: Paginator[Any] = Paginator(backend)
    pipeline: SyncPipeline[Any] = SyncPipeline(
        paginator,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
    )

    return BackendEnv(
        name="memory",
        mode="sync",
        pagination_backend=backend,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
        query=items,
        total=len(items),
        get_field=_dict_field,
        do_paginate=lambda q, p, **kw: paginate(q, p, **kw),
        do_filter=lambda q, specs: fb.apply_filters(q, specs),
        do_sort=lambda q, specs: sb.apply_sorting(q, specs),
        do_search=lambda q, spec: srch.apply_search(q, spec),
        do_pipeline=lambda q, p, **kw: pipeline.execute(q, p, **kw),
    )


# -- SA async setup ----------------------------------------------------------


def _orm_field(item: object, name: str) -> object:
    return getattr(item, name)


async def setup_sa_async(
    data: list[dict[str, Any]] | None = None,
) -> BackendEnv:
    """Create a BackendEnv for SQLAlchemy async."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from pypaginate.adapters.sqlalchemy.backend import SQLAlchemyBackend
    from pypaginate.adapters.sqlalchemy.filters import (
        SQLAlchemyFilterBackend,
    )
    from pypaginate.adapters.sqlalchemy.search import (
        SQLAlchemySearchBackend,
    )
    from pypaginate.adapters.sqlalchemy.sorting import (
        SQLAlchemySortBackend,
    )
    from tests.fixtures.models import Base, User

    items = data if data is not None else list(SEED_DATA)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = factory()
    users = [User(id=d["id"], name=d["name"], email=d["email"]) for d in items]
    session.add_all(users)
    await session.commit()

    sa_backend = SQLAlchemyBackend(session)
    fb = SQLAlchemyFilterBackend()
    sb = SQLAlchemySortBackend()
    srch = SQLAlchemySearchBackend()
    query = select(User)

    async def _paginate(q: object, p: OffsetParams, **kw: Any) -> Any:
        return await paginate(q, p, backend=sa_backend, **kw)

    async def _pipeline(q: object, p: OffsetParams, **kw: Any) -> Any:
        pag: AsyncPaginator[Any] = AsyncPaginator(sa_backend)
        pipe: AsyncPipeline[Any] = AsyncPipeline(
            pag,
            filter_backend=fb,
            sort_backend=sb,
            search_backend=srch,
        )
        return await pipe.execute(q, p, **kw)

    async def _cleanup() -> None:
        await session.close()
        await engine.dispose()

    return BackendEnv(
        name="sa_async",
        mode="async",
        pagination_backend=sa_backend,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
        query=query,
        total=len(items),
        get_field=_orm_field,
        do_paginate=_paginate,
        do_filter=lambda q, specs: fb.apply_filters(q, specs),
        do_sort=lambda q, specs: sb.apply_sorting(q, specs),
        do_search=lambda q, spec: srch.apply_search(q, spec),
        do_pipeline=_pipeline,
        cleanup=_cleanup,
    )


# -- SA sync setup -----------------------------------------------------------


async def setup_sa_sync(
    data: list[dict[str, Any]] | None = None,
) -> BackendEnv:
    """Create a BackendEnv for SQLAlchemy sync."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session, sessionmaker

    from pypaginate.adapters.sqlalchemy.backend import (
        SyncSQLAlchemyBackend,
    )
    from pypaginate.adapters.sqlalchemy.filters import (
        SQLAlchemyFilterBackend,
    )
    from pypaginate.adapters.sqlalchemy.search import (
        SQLAlchemySearchBackend,
    )
    from pypaginate.adapters.sqlalchemy.sorting import (
        SQLAlchemySortBackend,
    )
    from tests.fixtures.models import Base, User

    items = data if data is not None else list(SEED_DATA)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    factory = sessionmaker(
        engine,
        class_=Session,
        expire_on_commit=False,
    )
    session = factory()
    users = [User(id=d["id"], name=d["name"], email=d["email"]) for d in items]
    session.add_all(users)
    session.commit()

    sync_backend = SyncSQLAlchemyBackend(session)
    fb = SQLAlchemyFilterBackend()
    sb = SQLAlchemySortBackend()
    srch = SQLAlchemySearchBackend()
    query = select(User)

    paginator: Paginator[Any] = Paginator(sync_backend)  # type: ignore[arg-type]
    pipeline: SyncPipeline[Any] = SyncPipeline(
        paginator,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
    )

    async def _cleanup() -> None:
        session.close()
        engine.dispose()

    return BackendEnv(
        name="sa_sync",
        mode="sync",
        pagination_backend=sync_backend,
        filter_backend=fb,
        sort_backend=sb,
        search_backend=srch,
        query=query,
        total=len(items),
        get_field=_orm_field,
        do_paginate=lambda q, p, **kw: paginate(q, p, backend=sync_backend, **kw),
        do_filter=lambda q, specs: fb.apply_filters(q, specs),
        do_sort=lambda q, specs: sb.apply_sorting(q, specs),
        do_search=lambda q, spec: srch.apply_search(q, spec),
        do_pipeline=lambda q, p, **kw: pipeline.execute(q, p, **kw),
        cleanup=_cleanup,
    )


# -- Registry ----------------------------------------------------------------


SetupFn = Callable[..., Awaitable[BackendEnv]]

BACKEND_REGISTRY: dict[str, SetupFn] = {
    "memory": setup_memory,
    "sa_async": setup_sa_async,
    "sa_sync": setup_sa_sync,
}


async def setup_with_size(name: str, count: int) -> BackendEnv:
    """Create a BackendEnv with *count* generated items.

    Args:
        name: Registry key.
        count: Number of items to generate.

    Returns:
        A BackendEnv populated with *count* users.
    """
    data = [
        {
            "id": i + 1,
            "name": f"User_{i + 1}",
            "age": 20 + (i % 50),
            "email": f"user{i + 1}@test.com",
        }
        for i in range(count)
    ]
    setup_fn = BACKEND_REGISTRY[name]
    return await setup_fn(data=data)


__all__ = [
    "BACKEND_REGISTRY",
    "FIELD_NAMES",
    "SEED_DATA",
    "BackendEnv",
    "setup_memory",
    "setup_sa_async",
    "setup_sa_sync",
    "setup_with_size",
]
