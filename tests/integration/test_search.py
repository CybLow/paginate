"""Search integration tests — all backends via backend_env."""

from __future__ import annotations

from pypaginate import OffsetParams, SearchSpec
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_search_contains(backend_env: BackendEnv) -> None:
    """Search for substring finds matching items."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            search=SearchSpec(query="ali", fields=("name",)),
        )
    )
    assert page.total >= 1
    for item in page.items:
        name = str(env.get_field(item, "name")).lower()
        assert "ali" in name


async def test_search_no_match(backend_env: BackendEnv) -> None:
    """Search for nonexistent term returns empty page."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            search=SearchSpec(query="zzzzzzz", fields=("name",)),
        )
    )
    assert page.total == 0
    assert len(page.items) == 0


async def test_search_then_paginate(backend_env: BackendEnv) -> None:
    """Search results paginate correctly."""
    env = backend_env
    limit = 2
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=limit),
            search=SearchSpec(query="e", fields=("name", "email")),
        )
    )
    assert len(page.items) <= limit
    # Search for "e" should match multiple items via email
    assert page.total >= 1
