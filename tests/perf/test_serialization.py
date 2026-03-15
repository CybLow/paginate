"""Benchmark Page model serialization vs raw dict/JSON.

Groups:
    1. serialize-model-dump        — OffsetPage.model_dump() vs raw dict
    2. serialize-json              — OffsetPage.model_dump_json() vs json.dumps
    3. serialize-cursor            — CursorPage.model_dump()
    4. page-construction           — OffsetPage.create() vs raw dict
    5. serialize-filtered-result   — serialize after filter (realistic dicts)
    6. serialize-sorted-result     — serialize after sort (realistic dicts)
    7. serialize-searched-result   — serialize after search (realistic dicts)
    8. serialize-pipeline-result   — serialize full pipeline result

Run: uv run pytest tests/perf/test_serialization.py --benchmark-enable -v
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from pypaginate import (
    FilterSpec,
    SortDirection,
    SortSpec,
)
from pypaginate.adapters.memory.backend import MemoryBackend
from pypaginate.adapters.memory.filters import MemoryFilterBackend
from pypaginate.adapters.memory.search import MemorySearchBackend
from pypaginate.adapters.memory.sorting import MemorySortBackend
from pypaginate.domain.pages import CursorPage, OffsetPage
from pypaginate.domain.params import OffsetParams
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline
from tests.factories.data import make_users


# -- Competitor imports (guarded) -----------------------------------

try:
    from fastapi_pagination import Params, paginate as fp_paginate
    from fastapi_pagination.utils import disable_installed_extensions_check

    disable_installed_extensions_check()
    _HAS_FP = True
except ImportError:
    _HAS_FP = False

_SKIP_FP = pytest.mark.skipif(
    not _HAS_FP,
    reason="fastapi-pagination not installed",
)


_SIZES = [20, 100, 1000]


# -- Helpers --------------------------------------------------------


def _build_pipeline(
    data: list[dict[str, Any]],
) -> SyncPipeline[Any]:
    """Build a sync memory pipeline."""
    backend = MemoryBackend()
    pag: Paginator[Any] = Paginator(backend)
    return SyncPipeline(
        pag,
        filter_backend=MemoryFilterBackend(),
        sort_backend=MemorySortBackend(),
        search_backend=MemorySearchBackend(),
    )


# ================================================================
# Group 1: model_dump (Python dict)
# ================================================================


@pytest.mark.benchmark(group="serialize-model-dump")
@pytest.mark.parametrize("size", _SIZES)
def test_offset_page_model_dump(benchmark: Any, size: int) -> None:
    """OffsetPage.model_dump() with N items."""
    page = OffsetPage(
        items=list(range(size)),
        total=10000,
        page=1,
        limit=size,
        has_next=True,
        has_previous=False,
    )
    benchmark(page.model_dump)


@pytest.mark.benchmark(group="serialize-model-dump")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_dict_dump(benchmark: Any, size: int) -> None:
    """Baseline: constructing equivalent dict manually."""
    items = list(range(size))

    def raw() -> dict[str, object]:
        return {
            "items": items,
            "total": 10000,
            "page": 1,
            "limit": size,
            "has_next": True,
            "has_previous": False,
            "pages": 500,
        }

    benchmark(raw)


# ================================================================
# Group 2: model_dump_json (JSON string)
# ================================================================


@pytest.mark.benchmark(group="serialize-json")
@pytest.mark.parametrize("size", _SIZES)
def test_offset_page_model_dump_json(benchmark: Any, size: int) -> None:
    """OffsetPage.model_dump_json() with N items."""
    page = OffsetPage(
        items=list(range(size)),
        total=10000,
        page=1,
        limit=size,
        has_next=True,
        has_previous=False,
    )
    benchmark(page.model_dump_json)


@pytest.mark.benchmark(group="serialize-json")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_json_dumps(benchmark: Any, size: int) -> None:
    """Baseline: json.dumps of equivalent dict."""
    data = {
        "items": list(range(size)),
        "total": 10000,
        "page": 1,
        "limit": size,
        "has_next": True,
        "has_previous": False,
        "pages": 500,
    }
    benchmark(json.dumps, data)


# ================================================================
# Group 3: CursorPage serialization
# ================================================================


@pytest.mark.benchmark(group="serialize-cursor")
@pytest.mark.parametrize("size", _SIZES)
def test_cursor_page_model_dump(benchmark: Any, size: int) -> None:
    """CursorPage.model_dump() with N items."""
    page = CursorPage(
        items=list(range(size)),
        limit=size,
        has_next=True,
        has_previous=False,
        next_cursor="abc123",
        previous_cursor=None,
    )
    benchmark(page.model_dump)


# ================================================================
# Group 4: Page construction (how fast to create OffsetPage)
# ================================================================


@pytest.mark.benchmark(group="page-construction")
@pytest.mark.parametrize("size", _SIZES)
def test_offset_page_create(benchmark: Any, size: int) -> None:
    """OffsetPage.create() factory method with N items."""
    items = list(range(size))
    params = OffsetParams(page=1, limit=size)
    benchmark(OffsetPage.create, items, 10000, params)


@pytest.mark.benchmark(group="page-construction")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_dict_construction(benchmark: Any, size: int) -> None:
    """Baseline: constructing equivalent dict manually."""
    items = list(range(size))

    def raw() -> dict[str, object]:
        return {
            "items": items,
            "total": 10000,
            "page": 1,
            "limit": size,
        }

    benchmark(raw)


# ================================================================
# Group 5: serialize-filtered-result (realistic dict items)
# ================================================================

_FILTER_DATA = make_users(10_000)
_FILTER_SPECS = [FilterSpec(field="age", operator="gte", value=30)]
_FILTER_PARAMS = OffsetParams(page=1, limit=20)
_FILTER_PIPELINE = _build_pipeline(_FILTER_DATA)
_FILTERED_PAGE = _FILTER_PIPELINE.execute(
    _FILTER_DATA,
    _FILTER_PARAMS,
    filters=_FILTER_SPECS,
)


@pytest.mark.benchmark(group="serialize-filtered-result")
@pytest.mark.parametrize("size", _SIZES)
def test_filtered_page_model_dump_json(
    benchmark: Any,
    size: int,
) -> None:
    """Serialize OffsetPage after filtering (realistic dicts)."""
    users = make_users(size)
    page = OffsetPage(
        items=users,
        total=size * 10,
        page=1,
        limit=size,
        has_next=True,
        has_previous=False,
    )
    benchmark(page.model_dump_json)


@pytest.mark.benchmark(group="serialize-filtered-result")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_filtered_json_dumps(benchmark: Any, size: int) -> None:
    """Baseline: json.dumps of filtered dict items."""
    users = make_users(size)
    data = {
        "items": users,
        "total": size * 10,
        "page": 1,
        "limit": size,
        "has_next": True,
        "has_previous": False,
    }
    benchmark(json.dumps, data)


@_SKIP_FP
@pytest.mark.benchmark(group="serialize-filtered-result")
@pytest.mark.parametrize("size", _SIZES)
def test_fp_filtered_page_serialize(
    benchmark: Any,
    size: int,
) -> None:
    """fastapi-pagination Page serialization of filtered dicts."""
    users = make_users(size)
    fp_size = min(size, 100)  # fp Params caps at 100
    page = fp_paginate(users, Params(size=fp_size))  # type: ignore[arg-type]
    benchmark(page.model_dump_json)


# ================================================================
# Group 6: serialize-sorted-result (realistic dict items)
# ================================================================

_SORT_SPECS = [SortSpec(field="age", direction=SortDirection.ASC)]
_SORTED_PAGE = _FILTER_PIPELINE.execute(
    _FILTER_DATA,
    _FILTER_PARAMS,
    sorting=_SORT_SPECS,
)


@pytest.mark.benchmark(group="serialize-sorted-result")
@pytest.mark.parametrize("size", _SIZES)
def test_sorted_page_model_dump_json(
    benchmark: Any,
    size: int,
) -> None:
    """Serialize OffsetPage after sorting (realistic dicts)."""
    users = make_users(size)
    page = OffsetPage(
        items=sorted(users, key=lambda u: u["age"]),
        total=size * 10,
        page=1,
        limit=size,
        has_next=True,
        has_previous=False,
    )
    benchmark(page.model_dump_json)


@pytest.mark.benchmark(group="serialize-sorted-result")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_sorted_json_dumps(benchmark: Any, size: int) -> None:
    """Baseline: json.dumps of sorted dict items."""
    users = make_users(size)
    data = {
        "items": sorted(users, key=lambda u: u["age"]),
        "total": size * 10,
        "page": 1,
        "limit": size,
        "has_next": True,
        "has_previous": False,
    }
    benchmark(json.dumps, data)


# ================================================================
# Group 7: serialize-searched-result (realistic dict items)
# ================================================================


@pytest.mark.benchmark(group="serialize-searched-result")
@pytest.mark.parametrize("size", _SIZES)
def test_searched_page_model_dump_json(
    benchmark: Any,
    size: int,
) -> None:
    """Serialize OffsetPage after search (realistic dicts)."""
    users = make_users(size)
    page = OffsetPage(
        items=users[:20],
        total=size,
        page=1,
        limit=20,
        has_next=True,
        has_previous=False,
    )
    benchmark(page.model_dump_json)


@pytest.mark.benchmark(group="serialize-searched-result")
@pytest.mark.parametrize("size", _SIZES)
def test_raw_searched_json_dumps(
    benchmark: Any,
    size: int,
) -> None:
    """Baseline: json.dumps of search result dicts."""
    users = make_users(size)
    data = {
        "items": users[:20],
        "total": size,
        "page": 1,
        "limit": 20,
        "has_next": True,
        "has_previous": False,
    }
    benchmark(json.dumps, data)


# ================================================================
# Group 8: serialize-pipeline-result (filter+sort+paginate)
# ================================================================

_PIPELINE_PAGE = _FILTER_PIPELINE.execute(
    _FILTER_DATA,
    _FILTER_PARAMS,
    filters=_FILTER_SPECS,
    sorting=_SORT_SPECS,
)


@pytest.mark.benchmark(group="serialize-pipeline-result")
def test_pipeline_page_model_dump_json(benchmark: Any) -> None:
    """Serialize OffsetPage from full pipeline."""
    benchmark(_PIPELINE_PAGE.model_dump_json)


@pytest.mark.benchmark(group="serialize-pipeline-result")
def test_pipeline_page_model_dump(benchmark: Any) -> None:
    """model_dump() from full pipeline result."""
    benchmark(_PIPELINE_PAGE.model_dump)


@pytest.mark.benchmark(group="serialize-pipeline-result")
def test_raw_pipeline_json_dumps(benchmark: Any) -> None:
    """Baseline: json.dumps of pipeline result dict."""
    data = _PIPELINE_PAGE.model_dump()
    benchmark(json.dumps, data)
