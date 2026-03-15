"""SA competitor scaling -- same groups as test_scaling.py.

Side-by-side comparison of pypaginate vs SQLAlchemy competitors
across dataset sizes.  Uses identical benchmark group names so
output merges with test_scaling.py results.

Run: uv run pytest tests/perf/test_competitor_scaling_sa.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest


# -- Competitor imports (guarded) ------------------------------------

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
    from fastapi_pagination import Page, Params
    from fastapi_pagination.api import set_page, set_params
    from fastapi_pagination.ext.sqlalchemy import paginate as fp_sa_paginate
    from fastapi_pagination.utils import disable_installed_extensions_check

    disable_installed_extensions_check()
    HAS_FP_SA = True
except ImportError:
    HAS_FP_SA = False

try:
    from fastapi_filter.contrib.sqlalchemy import Filter as SAFilter

    HAS_FASTAPI_FILTER = True
except ImportError:
    HAS_FASTAPI_FILTER = False


_SKIP_SQLAKEYSET = pytest.mark.skipif(
    not HAS_SQLAKEYSET,
    reason="sqlakeyset not installed",
)
_SKIP_SA_PAGINATION = pytest.mark.skipif(
    not HAS_SA_PAGINATION,
    reason="sqlalchemy-pagination not installed",
)
_SKIP_FP_SA = pytest.mark.skipif(
    not HAS_FP_SA,
    reason="fastapi-pagination[sqlalchemy] not installed",
)
_SKIP_FASTAPI_FILTER = pytest.mark.skipif(
    not HAS_FASTAPI_FILTER,
    reason="fastapi-filter not installed",
)

_slow = pytest.mark.slow
_SA_SIZES = [
    pytest.param(1_000, id="1K"),
    pytest.param(10_000, id="10K"),
    pytest.param(100_000, id="100K", marks=_slow),
]


# -- Helpers ---------------------------------------------------------


def _make_sa_engine(size: int) -> Any:
    """Seed a SQLite engine with *size* users."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from tests.fixtures.models import Base, User

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(size)],
        )
        session.commit()
    return engine


# ===================================================================
# 1. SA PAGINATE scaling -- sync competitors
# ===================================================================


@pytest.mark.benchmark(group="scale-paginate-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_raw_sa_paginate_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw SQLAlchemy COUNT + OFFSET/LIMIT across sizes."""
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

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
    assert result["total"] == size
    engine.dispose()


@_SKIP_SA_PAGINATION
@pytest.mark.benchmark(group="scale-paginate-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_sa_pagination_lib_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """sqlalchemy-pagination (old Query API) across sizes."""
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

    def run() -> Any:
        with Session(engine) as s:
            return sa_pg_paginate(s.query(User), page=50, page_size=20)

    result = benchmark(run)
    assert result.total == size
    engine.dispose()


@_SKIP_SQLAKEYSET
@pytest.mark.benchmark(group="scale-paginate-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_sqlakeyset_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """sqlakeyset keyset pagination across sizes."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

    def run() -> Any:
        with Session(engine) as s:
            query = select(User).order_by(User.id)
            return select_page(s, query, per_page=20)

    page = benchmark(run)
    assert len(page) == 20
    engine.dispose()


@_SKIP_FP_SA
@pytest.mark.benchmark(group="scale-paginate-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_fp_sa_paginate_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """fastapi-pagination SA extension across sizes."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

    def run() -> Any:
        set_page(Page[User])  # type: ignore[type-var]
        set_params(Params(page=50, size=20))
        with Session(engine) as s:
            return fp_sa_paginate(s, select(User))

    result = benchmark(run)
    assert result.total == size  # type: ignore[union-attr]
    engine.dispose()


# ===================================================================
# 2. SA FILTER scaling -- sync competitors
# ===================================================================


@pytest.mark.benchmark(group="scale-filter-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_raw_sa_filter_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw SA WHERE + COUNT + OFFSET/LIMIT across sizes."""
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

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
@pytest.mark.benchmark(group="scale-filter-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_fastapi_filter_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """fastapi-filter SA filtering across sizes."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    class UserFilter(SAFilter):  # type: ignore[misc]
        name__like: str | None = None

        class Constants(SAFilter.Constants):  # type: ignore[name-defined]
            model = User

    engine = _make_sa_engine(size)

    def run() -> list[Any]:
        with Session(engine) as s:
            f = UserFilter(name__like="User_5%")
            query = f.filter(select(User))
            return list(s.execute(query.offset(0).limit(20)).scalars())

    result = benchmark(run)
    assert len(result) <= 20
    engine.dispose()


# ===================================================================
# 3. SA SORT scaling -- sync competitors
# ===================================================================


@pytest.mark.benchmark(group="scale-sort-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_raw_sa_sort_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw SA ORDER BY + OFFSET/LIMIT across sizes."""
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

    def run() -> dict[str, Any]:
        with Session(engine) as s:
            base = select(User).order_by(User.name)
            items = list(
                s.execute(base.offset(0).limit(20)).scalars(),
            )
            return {"items": items, "total": size}

    result = benchmark(run)
    assert result["total"] == size
    engine.dispose()


# ===================================================================
# 4. SA SEARCH scaling -- sync competitors
# ===================================================================


@pytest.mark.benchmark(group="scale-search-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_raw_sa_search_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw SA LIKE search + COUNT + OFFSET/LIMIT across sizes."""
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

    def run() -> dict[str, Any]:
        with Session(engine) as s:
            base = select(User).where(User.name.contains("User_5"))
            total = s.execute(
                select(func.count()).select_from(base.subquery()),
            ).scalar_one()
            items = list(
                s.execute(base.offset(0).limit(20)).scalars(),
            )
            return {"items": items, "total": total}

    result = benchmark(run)
    assert result["total"] >= 0
    engine.dispose()


# ===================================================================
# 5. SA PIPELINE scaling -- sync competitors
# ===================================================================


@pytest.mark.benchmark(group="scale-pipeline-sa-sync")
@pytest.mark.parametrize("size", _SA_SIZES)
def test_raw_sa_pipeline_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw SA WHERE + ORDER BY + OFFSET/LIMIT across sizes."""
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import User

    engine = _make_sa_engine(size)

    def run() -> dict[str, Any]:
        with Session(engine) as s:
            base = select(User).where(User.name.startswith("User_5")).order_by(User.email)
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
