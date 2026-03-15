"""Benchmark pypaginate against competing pagination solutions.

Competitors: raw Python, raw SQLAlchemy, fastapi-pagination (if installed).
Run: uv run pytest tests/perf/test_competitors.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.models import OffsetParams
from pypaginate.domain.specs import FilterSpec, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.perf.conftest import _setup_memory_sync


try:
    from fastapi_pagination import Page, Params, paginate as fp_paginate
    from fastapi_pagination.api import set_page, set_params

    HAS_FP = True
except ImportError:
    HAS_FP = False

_SKIP_FP = pytest.mark.skipif(not HAS_FP, reason="fastapi-pagination not installed")
_PARAMS_50 = OffsetParams(page=50, limit=20)
_PARAMS_1 = OffsetParams(page=1, limit=20)
_FILTER_SPECS = [FilterSpec(field="age", operator="gte", value=30)]
_SORT_SPECS = [SortSpec(field="age", direction=SortDirection.ASC)]


# -- helpers ---------------------------------------------------


def _raw_paginate(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Raw list slice: page=50, limit=20."""
    return {"items": data[980:1000], "total": len(data)}


def _raw_pipeline(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Raw Python filter + sort + slice pipeline."""
    filtered = [u for u in data if u["age"] >= 30]
    sorted_items = sorted(filtered, key=lambda u: u["name"])
    return {"items": sorted_items[0:20], "total": len(sorted_items)}


# -- Group 1: Memory paginate ---------------------------------


@pytest.mark.benchmark(group="competitors-memory-paginate")
def test_pypaginate_memory_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """pypaginate memory pagination."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(env.do_paginate, env.query, _PARAMS_50)
    assert result.total == 10_000


@pytest.mark.benchmark(group="competitors-memory-paginate")
def test_raw_slice_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """Baseline: raw Python list slicing."""
    result = benchmark(_raw_paginate, dataset_10k)
    assert result["total"] == 10_000


@pytest.mark.benchmark(group="competitors-memory-paginate")
@_SKIP_FP
def test_fastapi_pagination_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """fastapi-pagination in-memory paginate."""

    def fp() -> Any:
        set_page(Page[dict])  # type: ignore[type-var]
        set_params(Params(page=50, size=20))
        return fp_paginate(dataset_10k)

    result = benchmark(fp)
    assert result.total == 10_000  # type: ignore[union-attr]


# -- Group 2: SA paginate vs raw SA ---------------------------


@pytest.mark.benchmark(group="competitors-sa-paginate")
def test_pypaginate_sa_sync_10k(benchmark: Any, sa_sync_env_10k: BackendEnv) -> None:
    """pypaginate with SyncSQLAlchemyBackend."""
    result = benchmark(sa_sync_env_10k.do_paginate, sa_sync_env_10k.query, _PARAMS_50)
    assert result.total == 10_000


@pytest.mark.benchmark(group="competitors-sa-paginate")
def test_raw_sqlalchemy_10k(benchmark: Any) -> None:
    """Baseline: raw SQLAlchemy without pypaginate."""
    from sqlalchemy import create_engine, func, select
    from sqlalchemy.orm import Session

    from tests.fixtures.models import Base, User

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all([User(id=i, name=f"User_{i}", email=f"u{i}@test.com") for i in range(10_000)])
        s.commit()

    def raw_paginate() -> dict[str, Any]:
        with Session(engine) as s:
            total = s.execute(select(func.count()).select_from(User)).scalar_one()
            items = list(s.execute(select(User).offset(980).limit(20)).scalars())
            return {"items": items, "total": total}

    result = benchmark(raw_paginate)
    assert result["total"] == 10_000
    engine.dispose()


# -- Group 3: Memory filter -----------------------------------


@pytest.mark.benchmark(group="competitors-memory-filter")
def test_pypaginate_filter_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """pypaginate FilterEngine."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(env.do_filter, env.query, _FILTER_SPECS)
    assert len(result) <= 10_000


@pytest.mark.benchmark(group="competitors-memory-filter")
def test_raw_filter_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """Baseline: raw list comprehension."""
    result = benchmark(lambda: [d for d in dataset_10k if d["age"] >= 30])
    assert len(result) <= 10_000


# -- Group 4: Memory sort -------------------------------------


@pytest.mark.benchmark(group="competitors-memory-sort")
def test_pypaginate_sort_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """pypaginate SortEngine."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(env.do_sort, env.query, _SORT_SPECS)
    assert len(result) == 10_000


@pytest.mark.benchmark(group="competitors-memory-sort")
def test_raw_sort_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """Baseline: raw sorted()."""
    result = benchmark(lambda: sorted(dataset_10k, key=lambda d: d["age"]))
    assert len(result) == 10_000


# -- Group 5: Full pipeline -----------------------------------


@pytest.mark.benchmark(group="competitors-pipeline")
def test_pypaginate_pipeline_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """pypaginate full pipeline: filter + sort + paginate."""
    env = _setup_memory_sync(dataset_10k)
    result = benchmark(
        env.do_pipeline,
        env.query,
        _PARAMS_1,
        filters=_FILTER_SPECS,
        sorting=[SortSpec(field="name")],
    )
    assert result.total > 0


@pytest.mark.benchmark(group="competitors-pipeline")
def test_raw_pipeline_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """Baseline: raw Python filter + sort + slice."""
    result = benchmark(_raw_pipeline, dataset_10k)
    assert result["total"] > 0


@pytest.mark.benchmark(group="competitors-pipeline")
@_SKIP_FP
def test_fp_pipeline_10k(benchmark: Any, dataset_10k: list[dict[str, Any]]) -> None:
    """fastapi-pagination: filter + sort + paginate."""

    def fp_pipeline() -> Any:
        filtered = [u for u in dataset_10k if u["age"] >= 30]
        sorted_items = sorted(filtered, key=lambda u: u["name"])
        set_page(Page[dict])  # type: ignore[type-var]
        set_params(Params(page=1, size=20))
        return fp_paginate(sorted_items)

    result = benchmark(fp_pipeline)
    assert result.total > 0  # type: ignore[union-attr]
