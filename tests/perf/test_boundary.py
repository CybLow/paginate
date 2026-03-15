"""Boundary-value perf tests.

Exercises edge-case limits and page values
on the memory backend at moderate scale.
"""

from __future__ import annotations

from typing import Any

import pytest

from pypaginate.domain.enums import OverflowStrategy
from pypaginate.domain.models import OffsetParams
from tests.perf.conftest import _setup_memory_sync


@pytest.fixture()
def env_1k(dataset_1k: list[dict[str, Any]]):
    """Memory env with 1K items."""
    return _setup_memory_sync(dataset_1k)


# -- Boundary limits --------------------------------------------------------


@pytest.mark.parametrize("limit", [1, 20, 100, 1000])
def test_boundary_limit(
    env_1k: Any,
    limit: int,
) -> None:
    """Various limit values produce correct page sizes."""
    page = env_1k.do_paginate(
        env_1k.query,
        OffsetParams(page=1, limit=limit),
    )
    assert len(page.items) == min(limit, 1_000)
    assert page.total == 1_000


def test_limit_1_single_item(env_1k: Any) -> None:
    """limit=1 yields exactly 1 item per page."""
    page = env_1k.do_paginate(
        env_1k.query,
        OffsetParams(page=1, limit=1),
    )
    assert len(page.items) == 1
    assert page.has_next is True


def test_exact_fit(env_1k: Any) -> None:
    """N items with limit=N yields exactly 1 page."""
    page = env_1k.do_paginate(
        env_1k.query,
        OffsetParams(page=1, limit=1000),
    )
    assert len(page.items) == 1_000
    assert page.has_next is False
    assert page.pages == 1


def test_empty_dataset() -> None:
    """0 items yields empty page with total=0."""
    env = _setup_memory_sync([])
    page = env.do_paginate(env.query, OffsetParams(page=1, limit=20))
    assert page.total == 0
    assert len(page.items) == 0
    assert page.has_next is False


def test_overflow_empty(env_1k: Any) -> None:
    """Page beyond range with EMPTY strategy yields no items."""
    from pypaginate._dispatch import paginate

    page = paginate(
        env_1k.query,
        OffsetParams(page=999, limit=20),
        overflow=OverflowStrategy.EMPTY,
    )
    assert len(page.items) == 0
    assert page.total == 1_000


def test_overflow_clamp(env_1k: Any) -> None:
    """Page beyond range with CLAMP yields last page."""
    from pypaginate._dispatch import paginate

    page = paginate(
        env_1k.query,
        OffsetParams(page=999, limit=20),
        overflow=OverflowStrategy.CLAMP,
    )
    assert len(page.items) > 0
    assert page.total == 1_000
