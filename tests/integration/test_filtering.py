"""Filtering integration tests — all backends via backend_env."""

from __future__ import annotations

from pypaginate import FilterSpec, OffsetParams
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_eq_filter_returns_match(backend_env: BackendEnv) -> None:
    """Equality filter returns only matching items."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="eq", value="Alice")],
        )
    )
    assert page.total == 1
    assert len(page.items) == 1
    assert env.get_field(page.items[0], "name") == "Alice"


async def test_contains_filter(backend_env: BackendEnv) -> None:
    """Contains filter matches substring in name."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="contains", value="a")],
        )
    )
    for item in page.items:
        name = str(env.get_field(item, "name"))
        assert "a" in name.lower() or "a" in name


async def test_multiple_and_filters(backend_env: BackendEnv) -> None:
    """Multiple AND filters narrow results progressively."""
    env = backend_env

    # First: single filter
    page_one = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="contains", value="e")],
        )
    )

    # Second: add another filter — results should be equal or fewer
    page_two = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[
                FilterSpec(field="name", operator="contains", value="e"),
                FilterSpec(field="name", operator="contains", value="li"),
            ],
        )
    )
    assert page_two.total <= page_one.total


async def test_no_match_returns_empty(backend_env: BackendEnv) -> None:
    """Filter matching nothing returns empty page."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="eq", value="NoSuchPerson")],
        )
    )
    assert page.total == 0
    assert len(page.items) == 0


async def test_filter_then_paginate(backend_env: BackendEnv) -> None:
    """Filtered results paginate correctly."""
    env = backend_env
    limit = 2

    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=limit),
            filters=[FilterSpec(field="name", operator="contains", value="e")],
        )
    )
    assert len(page.items) <= limit
    if page.total > limit:
        assert page.has_next is True


async def test_gte_filter_memory_only() -> None:
    """GTE filter on age (memory-only, age not in SA User model)."""
    from tests.fixtures.backends import setup_memory

    env = await setup_memory()
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="age", operator="gte", value=30)],
        )
    )
    for item in page.items:
        assert env.get_field(item, "age") >= 30
