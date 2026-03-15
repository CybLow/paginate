"""In-memory competitor scaling -- same groups as test_scaling.py.

Side-by-side comparison of pypaginate vs competitors across dataset
sizes.  Uses identical benchmark group names so output merges with
test_scaling.py results.

Run: uv run pytest tests/perf/test_competitor_scaling.py --benchmark-enable -v
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.factories.data import make_users


# -- Competitor imports (guarded) ------------------------------------

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


_SKIP_FP = pytest.mark.skipif(
    not HAS_FP,
    reason="fastapi-pagination not installed",
)
_SKIP_PAGINATE = pytest.mark.skipif(
    not HAS_PAGINATE,
    reason="paginate not installed",
)

_slow = pytest.mark.slow
_MEM_SIZES = [
    pytest.param(1_000, id="1K"),
    pytest.param(10_000, id="10K"),
    pytest.param(100_000, id="100K"),
    pytest.param(500_000, marks=_slow, id="500K"),
    pytest.param(1_000_000, marks=_slow, id="1M"),
]
_PAG_SIZES = [
    pytest.param(1_000, id="1K"),
    pytest.param(10_000, id="10K"),
    pytest.param(100_000, id="100K"),
    pytest.param(500_000, marks=_slow, id="500K"),
    pytest.param(1_000_000, marks=_slow, id="1M"),
]


# ═══════════════════════════════════════════════════════════
# 1. PAGINATE scaling — in-memory competitors
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-paginate-memory")
@pytest.mark.parametrize("size", _PAG_SIZES)
def test_raw_python_paginate_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw list slice across dataset sizes."""
    data = make_users(size)

    def run() -> dict[str, Any]:
        offset = 980 if size > 1_000 else 0
        return {"items": data[offset : offset + 20], "total": len(data)}

    result = benchmark(run)
    assert result["total"] == size


@_SKIP_FP
@pytest.mark.benchmark(group="scale-paginate-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_fp_paginate_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """fastapi-pagination across dataset sizes."""
    data = make_users(size)

    def run() -> Any:
        set_page(Page[dict])  # type: ignore[type-var]
        set_params(Params(page=50, size=20))
        return fp_paginate(data)

    result = benchmark(run)
    assert result.total == size  # type: ignore[union-attr]


@_SKIP_PAGINATE
@pytest.mark.benchmark(group="scale-paginate-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_paginate_lib_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """paginate lib across dataset sizes."""
    data = make_users(size)

    def run() -> Any:
        return paginate_lib.Page(data, page=50, items_per_page=20)

    page = benchmark(run)
    assert page.item_count == size


# ═══════════════════════════════════════════════════════════
# 2. FILTER scaling — in-memory competitors
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-filter-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_raw_python_filter_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw list comprehension filter across dataset sizes."""
    data = make_users(size)

    def run() -> list[dict[str, Any]]:
        return [u for u in data if u["age"] >= 30]

    result = benchmark(run)
    assert len(result) <= size


# ═══════════════════════════════════════════════════════════
# 3. SORT scaling — in-memory competitors
# ═══════════════════════════════════════════════════════════


@pytest.mark.benchmark(group="scale-sort-memory")
@pytest.mark.parametrize("size", _MEM_SIZES)
def test_raw_python_sort_scaling(
    benchmark: Any,
    size: int,
) -> None:
    """Raw sorted() across dataset sizes."""
    data = make_users(size)

    def run() -> list[dict[str, Any]]:
        return sorted(data, key=lambda u: u["age"])

    result = benchmark(run)
    assert len(result) == size
