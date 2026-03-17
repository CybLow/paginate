"""Filter E2E flows — all backends via backend_env."""

from __future__ import annotations

from pypaginate import FilterSpec, OffsetParams
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_filter_narrow_then_paginate(backend_env: BackendEnv) -> None:
    """Filter narrows dataset, then paginate the subset."""
    env = backend_env
    limit = 2

    # Filter to items with "e" in name (Alice, Eve, Grace, Henry)
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=limit),
            filters=[FilterSpec(field="name", operator="contains", value="e")],
        )
    )
    assert page.total <= env.total
    assert len(page.items) <= limit
    for item in page.items:
        name = str(env.get_field(item, "name"))
        assert "e" in name.lower() or "e" in name


async def test_progressive_filtering(backend_env: BackendEnv) -> None:
    """Adding filters narrows results each time."""
    env = backend_env
    params = OffsetParams(page=1, limit=100)

    # No filter
    page_all = await run(env.do_pipeline(env.query, params))

    # One filter
    page_one = await run(
        env.do_pipeline(
            env.query,
            params,
            filters=[FilterSpec(field="name", operator="contains", value="e")],
        )
    )

    # Two filters — stricter
    page_two = await run(
        env.do_pipeline(
            env.query,
            params,
            filters=[
                FilterSpec(field="name", operator="contains", value="e"),
                FilterSpec(field="name", operator="contains", value="li"),
            ],
        )
    )
    assert page_all.total >= page_one.total >= page_two.total


async def test_filter_to_empty(backend_env: BackendEnv) -> None:
    """Filter that matches nothing returns empty page."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="eq", value="XXXX_NONEXISTENT")],
        )
    )
    assert page.total == 0
    assert len(page.items) == 0
