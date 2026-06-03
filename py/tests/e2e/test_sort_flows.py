"""Sort E2E flows — all backends via backend_env."""

from __future__ import annotations

from pypaginate import OffsetParams, SortDirection, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_global_sort_order_across_pages(backend_env: BackendEnv) -> None:
    """Ascending sort is preserved when iterating all pages."""
    env = backend_env
    limit = 3
    all_names: list[str] = []
    page_num = 1

    while True:
        page = await run(
            env.do_pipeline(
                env.query,
                OffsetParams(page=page_num, limit=limit),
                sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
            )
        )
        all_names.extend(str(env.get_field(item, "name")) for item in page.items)
        if not page.has_next:
            break
        page_num += 1

    assert all_names == sorted(all_names)
    assert len(all_names) == env.total


async def test_sort_desc_across_pages(backend_env: BackendEnv) -> None:
    """Descending sort is preserved when iterating all pages."""
    env = backend_env
    limit = 3
    all_names: list[str] = []
    page_num = 1

    while True:
        page = await run(
            env.do_pipeline(
                env.query,
                OffsetParams(page=page_num, limit=limit),
                sorting=[SortSpec(field="name", direction=SortDirection.DESC)],
            )
        )
        all_names.extend(str(env.get_field(item, "name")) for item in page.items)
        if not page.has_next:
            break
        page_num += 1

    assert all_names == sorted(all_names, reverse=True)
    assert len(all_names) == env.total
