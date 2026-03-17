"""Offset pagination E2E flows — all backends via backend_env."""

from __future__ import annotations

import math

from pypaginate import OffsetParams, OverflowStrategy
from tests.fixtures.backends import BackendEnv, setup_with_size
from tests.fixtures.helpers import run


async def test_paginate_all_pages_completeness(backend_env: BackendEnv) -> None:
    """Iterate ALL pages, collect every item, verify count equals total."""
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


async def test_paginate_single_item() -> None:
    """Dataset of 1 item produces exactly one page."""
    env = await setup_with_size("memory", 1)
    page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=10)))
    assert page.total == 1
    assert len(page.items) == 1
    assert page.has_next is False
    assert page.has_previous is False
    assert page.pages == 1


async def test_paginate_exact_limit_match() -> None:
    """N items with limit=N produces exactly 1 page."""
    count = 5
    env = await setup_with_size("memory", count)
    page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=count)))
    assert page.total == count
    assert len(page.items) == count
    assert page.has_next is False
    assert page.pages == 1


async def test_paginate_with_clamp(backend_env: BackendEnv) -> None:
    """CLAMP overflow returns last valid page."""
    env = backend_env
    limit = 3
    expected_last = math.ceil(env.total / limit)

    page = await run(
        env.do_paginate(
            env.query,
            OffsetParams(page=999, limit=limit),
            overflow=OverflowStrategy.CLAMP,
        )
    )
    assert page.page == expected_last
    assert len(page.items) > 0
    assert page.has_next is False
