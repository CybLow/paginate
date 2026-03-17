"""Completeness E2E tests — no lost items, no duplicates, clean JSON."""

from __future__ import annotations

from pypaginate import OffsetParams
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_no_items_lost_across_pages(backend_env: BackendEnv) -> None:
    """Every item appears when iterating all pages."""
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


async def test_no_duplicates(backend_env: BackendEnv) -> None:
    """No item appears more than once across all pages."""
    env = backend_env
    limit = 3
    seen_names: list[str] = []
    page_num = 1

    while True:
        page = await run(env.do_paginate(env.query, OffsetParams(page=page_num, limit=limit)))
        for item in page.items:
            name = str(env.get_field(item, "name"))
            seen_names.append(name)
        if not page.has_next:
            break
        page_num += 1

    assert len(seen_names) == len(set(seen_names))


async def test_serialization_clean(backend_env: BackendEnv) -> None:
    """OffsetPage JSON has no null cursor fields (offset-only)."""
    env = backend_env
    page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=5)))
    data = page.model_dump()

    # OffsetPage must have these fields
    assert "total" in data
    assert "page" in data
    assert "items" in data
    assert "has_next" in data
    assert "has_previous" in data
    assert "limit" in data
    assert "pages" in data

    # OffsetPage must NOT have cursor fields
    assert "next_cursor" not in data
    assert "previous_cursor" not in data
