"""Benchmark pypaginate against competing pagination solutions.

Competitors:
- Raw Python (list slicing, sorted, list comprehension)
- Raw SQLAlchemy (manual SELECT COUNT + OFFSET/LIMIT)
- fastapi-pagination (1.6K stars, most popular pagination lib)
- paginate (simple list paginator)
- sqlakeyset (keyset/cursor pagination for SQLAlchemy)
- sqlalchemy-pagination (simple SA paginator, old Query API)
- fastapi-filter (filtering for FastAPI + SQLAlchemy)

Run: uv run pytest tests/perf/test_competitors.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.models import OffsetParams
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import _run_in_loop, _setup_memory_sync


# -- Competitor imports (guarded) ---------------------------------

try:
    from fastapi_pagination import Page, Params, paginate as fp_paginate
    from fastapi_pagination.api import set_page, set_params
    from fastapi_pagination.utils import disable_installed_extensions_check

    disable_installed_extensions_check()
    HAS_FP = True
except ImportError:
    HAS_FP = False

try:
    import paginate as paginate_lib

    HAS_PAGINATE = True
except ImportError:
    HAS_PAGINATE = False

try:
    from sqlakeyset import select_page

    HAS_SQLAKEYSET = True
except ImportError:
    HAS_SQLAKEYSET = False

try:
    from sqlalchemy_pagination import paginate as sa_pg_paginate

    HAS_SA_PAGINATION = True
except ImportError:
    HAS_SA_PAGINATION = False

try:
    from fastapi_filter.contrib.sqlalchemy import Filter as SAFilter

    HAS_FASTAPI_FILTER = True
except ImportError:
    HAS_FASTAPI_FILTER = False


_SKIP_FP = pytest.mark.skipif(
    not HAS_FP,
    reason="fastapi-pagination not installed",
)
_SKIP_PAGINATE = pytest.mark.skipif(
    not HAS_PAGINATE,
    reason="paginate not installed",
)
_SKIP_SQLAKEYSET = pytest.mark.skipif(
    not HAS_SQLAKEYSET,
    reason="sqlakeyset not installed",
)
_SKIP_SA_PAGINATION = pytest.mark.skipif(
    not HAS_SA_PAGINATION,
    reason="sqlalchemy-pagination not installed",
)
_SKIP_FASTAPI_FILTER = pytest.mark.skipif(
    not HAS_FASTAPI_FILTER,
    reason="fastapi-filter not installed",
)


# -- Shared params ------------------------------------------------

_PARAMS_50 = OffsetParams(page=50, limit=20)
_PARAMS_1 = OffsetParams(page=1, limit=20)
_FILTER_SPECS = [FilterSpec(field="age", operator="gte", value=30)]
_SORT_SPECS = [SortSpec(field="age", direction=SortDirection.ASC)]
_SORT_NAME = [SortSpec(field="name")]
_SEARCH_SPEC = SearchSpec(query="User_5", fields=("name",))


# ================================================================
# Group 1: in-memory-paginate
# Who paginates a list fastest?
# ================================================================


@pytest.mark.benchmark(group="in-memory-paginate")
def test_pypaginate_memory(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate memory pagination (page 50, limit 20)."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(env.do_paginate, env.query, _PARAMS_50)
    assert result.total == 10_000


@_SKIP_FP
@pytest.mark.benchmark(group="in-memory-paginate")
def test_fastapi_pagination_memory(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """fastapi-pagination in-memory paginate."""

    def run() -> Any:
        set_page(Page[dict])  # type: ignore[type-var]
        set_params(Params(page=50, size=20))
        return fp_paginate(dataset_10k)

    result = benchmark(run)
    assert result.total == 10_000  # type: ignore[union-attr]


@_SKIP_PAGINATE
@pytest.mark.benchmark(group="in-memory-paginate")
def test_paginate_lib_memory(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """paginate lib in-memory paginate."""

    def run() -> Any:
        return paginate_lib.Page(
            dataset_10k,
            page=50,
            items_per_page=20,
        )

    page = benchmark(run)
    assert page.item_count == 10_000


@pytest.mark.benchmark(group="in-memory-paginate")
def test_raw_python_slice(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Raw Python list slicing (page 50, limit 20)."""

    def run() -> dict[str, Any]:
        return {"items": dataset_10k[980:1000], "total": len(dataset_10k)}

    result = benchmark(run)
    assert result["total"] == 10_000


# ================================================================
# Group 2: in-memory-filter-paginate
# Filter then paginate
# ================================================================


@pytest.mark.benchmark(group="in-memory-filter-paginate")
def test_pypaginate_filter_paginate(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate pipeline: filter (age>=30) then paginate."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(
        env.do_pipeline,
        env.query,
        _PARAMS_1,
        filters=_FILTER_SPECS,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="in-memory-filter-paginate")
def test_raw_python_filter_paginate(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Raw Python: list comprehension filter + slice."""

    def run() -> dict[str, Any]:
        filtered = [u for u in dataset_10k if u["age"] >= 30]
        return {"items": filtered[0:20], "total": len(filtered)}

    result = benchmark(run)
    assert result["total"] > 0


# ================================================================
# Group 3: in-memory-sort-paginate
# Sort then paginate
# ================================================================


@pytest.mark.benchmark(group="in-memory-sort-paginate")
def test_pypaginate_sort_paginate(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate pipeline: sort by age then paginate."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(
        env.do_pipeline,
        env.query,
        _PARAMS_1,
        sorting=_SORT_SPECS,
    )
    assert result.total == 10_000


@pytest.mark.benchmark(group="in-memory-sort-paginate")
def test_raw_python_sort_paginate(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Raw Python: sorted() + slice."""

    def run() -> dict[str, Any]:
        sorted_items = sorted(dataset_10k, key=lambda u: u["age"])
        return {"items": sorted_items[0:20], "total": len(sorted_items)}

    result = benchmark(run)
    assert result["total"] == 10_000


# ================================================================
# Group 4: in-memory-search-paginate
# Search then paginate
# ================================================================


@pytest.mark.benchmark(group="in-memory-search-paginate")
def test_pypaginate_search_paginate(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate pipeline: search 'User_5' in name then paginate."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(
        env.do_pipeline,
        env.query,
        _PARAMS_1,
        search=_SEARCH_SPEC,
    )
    assert result.total >= 0


@pytest.mark.benchmark(group="in-memory-search-paginate")
def test_raw_python_search_paginate(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Raw Python: manual string matching + slice."""

    def run() -> dict[str, Any]:
        query = "user_5"
        matched = [d for d in dataset_10k if query in d["name"].lower()]
        return {"items": matched[0:20], "total": len(matched)}

    result = benchmark(run)
    assert result["total"] >= 0


# ================================================================
# Group 5: in-memory-full-pipeline
# Filter + sort + paginate (all competitors)
# ================================================================


@pytest.mark.benchmark(group="in-memory-full-pipeline")
def test_pypaginate_full_pipeline(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """pypaginate: filter + sort + paginate pipeline."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(
        env.do_pipeline,
        env.query,
        _PARAMS_1,
        filters=_FILTER_SPECS,
        sorting=_SORT_NAME,
    )
    assert result.total > 0


@_SKIP_FP
@pytest.mark.benchmark(group="in-memory-full-pipeline")
def test_fastapi_pagination_full_pipeline(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """fastapi-pagination: manual filter/sort then paginate."""

    def run() -> Any:
        filtered = [u for u in dataset_10k if u["age"] >= 30]
        sorted_items = sorted(filtered, key=lambda u: u["name"])
        set_page(Page[dict])  # type: ignore[type-var]
        set_params(Params(page=1, size=20))
        return fp_paginate(sorted_items)

    result = benchmark(run)
    assert result.total > 0  # type: ignore[union-attr]


@_SKIP_PAGINATE
@pytest.mark.benchmark(group="in-memory-full-pipeline")
def test_paginate_lib_full_pipeline(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """paginate lib: manual filter/sort then paginate."""

    def run() -> Any:
        filtered = [u for u in dataset_10k if u["age"] >= 30]
        sorted_items = sorted(filtered, key=lambda u: u["name"])
        return paginate_lib.Page(sorted_items, page=1, items_per_page=20)

    page = benchmark(run)
    assert page.item_count > 0


@pytest.mark.benchmark(group="in-memory-full-pipeline")
def test_raw_python_full_pipeline(
    benchmark: Any,
    dataset_10k: list[dict[str, Any]],
) -> None:
    """Raw Python: filter + sort + slice chain."""

    def run() -> dict[str, Any]:
        filtered = [u for u in dataset_10k if u["age"] >= 30]
        sorted_items = sorted(filtered, key=lambda u: u["name"])
        return {"items": sorted_items[0:20], "total": len(sorted_items)}

    result = benchmark(run)
    assert result["total"] > 0


# ================================================================
# Group 6: sqlalchemy-paginate
# Who paginates SQL fastest?
# ================================================================


@pytest.mark.benchmark(group="sqlalchemy-paginate")
def test_pypaginate_sa_sync(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """pypaginate SyncSQLAlchemyBackend (offset pagination)."""
    result = benchmark(
        sa_sync_env_10k.do_paginate,
        sa_sync_env_10k.query,
        _PARAMS_50,
    )
    assert result.total == 10_000


@pytest.mark.benchmark(group="sqlalchemy-paginate")
def test_pypaginate_sa_async(
    benchmark: Any,
    sa_async_env_10k: BackendEnv,
    sa_async_loop_10k: Any,
) -> None:
    """pypaginate async SQLAlchemyBackend (via asyncio.run)."""
    coro_fn = sa_async_env_10k.do_paginate

    def run() -> Any:
        return _run_in_loop(
            sa_async_loop_10k,
            coro_fn(sa_async_env_10k.query, _PARAMS_50),
        )

    result = benchmark(run)
    assert result.total == 10_000


@pytest.mark.benchmark(group="sqlalchemy-paginate")
def test_raw_sqlalchemy(benchmark: Any) -> None:
    """Raw SQLAlchemy: manual COUNT + OFFSET/LIMIT."""
    from sqlalchemy import create_engine, func, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import Base, User

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    def run() -> dict[str, Any]:
        with Session(engine) as s:
            total = s.execute(
                select(func.count()).select_from(User),
            ).scalar_one()
            items = list(
                s.execute(select(User).offset(980).limit(20)).scalars(),
            )
            return {"items": items, "total": total}

    result = benchmark(run)
    assert result["total"] == 10_000
    engine.dispose()


@_SKIP_SQLAKEYSET
@pytest.mark.benchmark(group="sqlalchemy-paginate")
def test_sqlakeyset_keyset(benchmark: Any) -> None:
    """sqlakeyset: direct keyset/cursor pagination."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import Base, User

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    def run() -> Any:
        with Session(engine) as s:
            query = select(User).order_by(User.id)
            return select_page(s, query, per_page=20)

    page = benchmark(run)
    assert len(page) == 20
    engine.dispose()


@_SKIP_SA_PAGINATION
@pytest.mark.benchmark(group="sqlalchemy-paginate")
def test_sqlalchemy_pagination_lib_10k(benchmark: Any) -> None:
    """sqlalchemy-pagination library (old Query API)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from tests.fixtures.models import Base, User

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    def run() -> Any:
        with Session(engine) as s:
            return sa_pg_paginate(s.query(User), page=50, page_size=20)

    result = benchmark(run)
    assert result.total == 10_000
    engine.dispose()


# ================================================================
# Group 7: sqlalchemy-filter-paginate
# Filter SQL then paginate
# ================================================================


@pytest.mark.benchmark(group="sqlalchemy-filter-paginate")
def test_pypaginate_sa_filter(
    benchmark: Any,
    sa_sync_env_10k: BackendEnv,
) -> None:
    """pypaginate SA pipeline: filter by name prefix then paginate."""
    name_filter = [FilterSpec(field="name", operator="starts_with", value="User_5")]
    result = benchmark(
        sa_sync_env_10k.do_pipeline,
        sa_sync_env_10k.query,
        _PARAMS_1,
        filters=name_filter,
    )
    assert result.total > 0


@pytest.mark.benchmark(group="sqlalchemy-filter-paginate")
def test_raw_sa_filter(benchmark: Any) -> None:
    """Raw SQLAlchemy: manual WHERE + COUNT + OFFSET/LIMIT."""
    from sqlalchemy import create_engine, func, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import Base, User

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    def run() -> dict[str, Any]:
        with Session(engine) as s:
            base = select(User).where(User.name.startswith("User_5"))
            total = s.execute(
                select(func.count()).select_from(base.subquery()),
            ).scalar_one()
            items = list(
                s.execute(base.offset(0).limit(20)).scalars(),
            )
            return {"items": items, "total": total}

    result = benchmark(run)
    assert result["total"] > 0
    engine.dispose()


@_SKIP_FASTAPI_FILTER
@pytest.mark.benchmark(group="sqlalchemy-filter-paginate")
def test_fastapi_filter_10k(benchmark: Any) -> None:
    """fastapi-filter library for SQL filtering."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import Base, User

    class UserFilter(SAFilter):
        name__like: str | None = None

        class Constants(SAFilter.Constants):
            model = User

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)],
        )
        s.commit()

    def run() -> list[Any]:
        with Session(engine) as s:
            f = UserFilter(name__like="User_5%")
            query = f.filter(select(User))
            return list(s.execute(query.offset(0).limit(20)).scalars())

    result = benchmark(run)
    assert len(result) <= 20
    engine.dispose()


# ================================================================
# Group 8: at-scale-100k
# Large dataset comparison (memory only)
# ================================================================


@pytest.mark.benchmark(group="at-scale-100k")
def test_pypaginate_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """pypaginate memory pagination on 100K items."""
    env = _setup_memory_sync(dataset_100k)
    params = OffsetParams(page=500, limit=20)
    result = benchmark(env.do_paginate, env.query, params)
    assert result.total == 100_000


@_SKIP_FP
@pytest.mark.benchmark(group="at-scale-100k")
def test_fastapi_pagination_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """fastapi-pagination on 100K items."""

    def run() -> Any:
        set_page(Page[dict])  # type: ignore[type-var]
        set_params(Params(page=500, size=20))
        return fp_paginate(dataset_100k)

    result = benchmark(run)
    assert result.total == 100_000  # type: ignore[union-attr]


@_SKIP_PAGINATE
@pytest.mark.benchmark(group="at-scale-100k")
def test_paginate_lib_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """paginate lib on 100K items."""

    def run() -> Any:
        return paginate_lib.Page(
            dataset_100k,
            page=500,
            items_per_page=20,
        )

    page = benchmark(run)
    assert page.item_count == 100_000


@pytest.mark.benchmark(group="at-scale-100k")
def test_raw_python_100k(
    benchmark: Any,
    dataset_100k: list[dict[str, Any]],
) -> None:
    """Raw Python slice on 100K items."""
    offset = (500 - 1) * 20

    def run() -> dict[str, Any]:
        return {
            "items": dataset_100k[offset : offset + 20],
            "total": len(dataset_100k),
        }

    result = benchmark(run)
    assert result["total"] == 100_000
