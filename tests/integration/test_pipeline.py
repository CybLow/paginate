"""Pipeline integration tests — all backends via backend_env."""

from __future__ import annotations

from pypaginate import FilterSpec, OffsetParams, SortDirection, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_filter_sort_paginate_combined(backend_env: BackendEnv) -> None:
    """Pipeline with filter + sort + paginate produces correct results."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="contains", value="e")],
            sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
        )
    )
    names = [str(env.get_field(item, "name")) for item in page.items]
    # All names must contain "e" (case-sensitive for memory)
    for name in names:
        assert "e" in name.lower() or "e" in name
    # Names must be sorted
    assert names == sorted(names)


async def test_pipeline_no_specs_plain_paginate(backend_env: BackendEnv) -> None:
    """Pipeline with no specs behaves like plain paginate."""
    env = backend_env
    pipeline_page = await run(env.do_pipeline(env.query, OffsetParams(page=1, limit=100)))
    plain_page = await run(env.do_paginate(env.query, OffsetParams(page=1, limit=100)))
    assert pipeline_page.total == plain_page.total
    assert len(pipeline_page.items) == len(plain_page.items)


async def test_pipeline_completeness(backend_env: BackendEnv) -> None:
    """All items are collected across pipeline pages."""
    env = backend_env
    limit = 3
    collected: list[object] = []
    page_num = 1

    while True:
        page = await run(
            env.do_pipeline(
                env.query,
                OffsetParams(page=page_num, limit=limit),
                sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
            )
        )
        collected.extend(page.items)
        if not page.has_next:
            break
        page_num += 1

    assert len(collected) == env.total
