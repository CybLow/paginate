"""Combined E2E flows — filter + sort + search + paginate."""

from __future__ import annotations

from pypaginate import FilterSpec, OffsetParams, SearchSpec, SortDirection, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_full_pipeline_all_specs(backend_env: BackendEnv) -> None:
    """Filter + sort + search + paginate in one pipeline call."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="contains", value="e")],
            sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
            search=SearchSpec(query="e", fields=("name",)),
        )
    )
    names = [str(env.get_field(item, "name")) for item in page.items]
    # Should be sorted
    assert names == sorted(names)
    # All items should match both filter and search
    for name in names:
        assert "e" in name.lower() or "e" in name


async def test_iterate_filtered_sorted_paginated(backend_env: BackendEnv) -> None:
    """Iterate all pages of filtered+sorted results, verify completeness."""
    env = backend_env
    limit = 2
    collected: list[object] = []
    page_num = 1

    while True:
        page = await run(
            env.do_pipeline(
                env.query,
                OffsetParams(page=page_num, limit=limit),
                filters=[FilterSpec(field="name", operator="contains", value="e")],
                sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
            )
        )
        collected.extend(page.items)
        if not page.has_next:
            break
        page_num += 1

    # Total collected must equal filtered total
    first_page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[FilterSpec(field="name", operator="contains", value="e")],
        )
    )
    assert len(collected) == first_page.total


async def test_pipeline_idempotent(backend_env: BackendEnv) -> None:
    """Running the same pipeline twice produces identical results."""
    env = backend_env
    params = OffsetParams(page=1, limit=100)
    kwargs = {
        "sorting": [SortSpec(field="name", direction=SortDirection.ASC)],
    }

    page1 = await run(env.do_pipeline(env.query, params, **kwargs))
    page2 = await run(env.do_pipeline(env.query, params, **kwargs))

    assert page1.total == page2.total
    assert len(page1.items) == len(page2.items)
    for a, b in zip(page1.items, page2.items, strict=True):
        assert env.get_field(a, "name") == env.get_field(b, "name")
