"""Pagination integration tests — all backends via backend_env."""

from __future__ import annotations

import math

from pypaginate import OffsetParams, OverflowStrategy
from tests.fixtures.backends import BackendEnv, setup_with_size
from tests.fixtures.helpers import run


async def test_count_matches_total(backend_env: BackendEnv) -> None:
    """Total in page equals seed data count."""
    env = backend_env
    page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=100)))
    assert page.total == env.total


async def test_first_page_correct_items(backend_env: BackendEnv) -> None:
    """First page contains the expected number of items."""
    env = backend_env
    limit = 3
    page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=limit)))
    assert len(page.items) == limit
    assert page.page == 1
    assert page.has_previous is False


async def test_last_page_has_next_false(backend_env: BackendEnv) -> None:
    """Last page has has_next=False."""
    env = backend_env
    limit = 3
    last_page_num = math.ceil(env.total / limit)
    page = await run(env.do_paginate(env.query, OffsetParams(page=last_page_num, limit=limit)))
    assert page.has_next is False


async def test_all_pages_collect_all_items(backend_env: BackendEnv) -> None:
    """Iterating every page collects exactly total items."""
    env = backend_env
    limit = 3
    collected: list[object] = []
    page_num = 1

    while True:
        page = await run(env.do_paginate(env.query, OffsetParams(page=page_num, limit=limit)))
        collected.extend(page.items)
        if not page.has_next:
            break
        page_num += 1

    assert len(collected) == env.total


async def test_overflow_clamp(backend_env: BackendEnv) -> None:
    """Overflow CLAMP returns last page instead of empty."""
    env = backend_env
    limit = 3
    page = await run(
        env.do_paginate(
            env.query, OffsetParams(page=999, limit=limit), overflow=OverflowStrategy.CLAMP
        )
    )
    assert len(page.items) > 0
    assert page.page == math.ceil(env.total / limit)


async def test_overflow_empty(backend_env: BackendEnv) -> None:
    """Overflow EMPTY returns empty items for out-of-range page."""
    env = backend_env
    page = await run(
        env.do_paginate(env.query, OffsetParams(page=999, limit=3), overflow=OverflowStrategy.EMPTY)
    )
    assert len(page.items) == 0
    assert page.total == env.total


async def test_empty_dataset() -> None:
    """Empty dataset produces total=0 and no items."""
    env = await setup_with_size("memory", 0)
    page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=10)))
    assert page.total == 0
    assert len(page.items) == 0
    assert page.has_next is False


async def test_single_item() -> None:
    """Single-item dataset produces one page with one item."""
    env = await setup_with_size("memory", 1)
    page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=10)))
    assert page.total == 1
    assert len(page.items) == 1
    assert page.has_next is False
    assert page.has_previous is False
