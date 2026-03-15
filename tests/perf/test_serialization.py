"""Benchmark Page model serialization vs raw dict/JSON.

Groups:
    1. serialize-model-dump   — OffsetPage.model_dump() vs raw dict
    2. serialize-json         — OffsetPage.model_dump_json() vs json.dumps
    3. serialize-cursor       — CursorPage.model_dump()
    4. page-construction      — OffsetPage.create() vs raw dict

Run: uv run pytest tests/perf/test_serialization.py --benchmark-enable -v
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from pypaginate.domain.pages import CursorPage, OffsetPage
from pypaginate.domain.params import OffsetParams


_SIZES = [20, 100, 1000]


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
