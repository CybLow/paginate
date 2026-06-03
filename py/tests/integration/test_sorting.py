"""Sorting integration tests — all backends via backend_env."""

from __future__ import annotations

from pypaginate import OffsetParams, SortDirection, SortSpec
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_sort_asc_by_name(backend_env: BackendEnv) -> None:
    """Ascending sort by name produces alphabetical order."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
        )
    )
    names = [str(env.get_field(item, "name")) for item in page.items]
    assert names == sorted(names)


async def test_sort_desc_by_name(backend_env: BackendEnv) -> None:
    """Descending sort by name produces reverse order."""
    env = backend_env
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            sorting=[SortSpec(field="name", direction=SortDirection.DESC)],
        )
    )
    names = [str(env.get_field(item, "name")) for item in page.items]
    assert names == sorted(names, reverse=True)


async def test_sort_preserved_across_pages(backend_env: BackendEnv) -> None:
    """Sort order is consistent across all pages."""
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


async def test_multi_field_sort_memory_only() -> None:
    """Multi-field sort applies primary then secondary key."""
    from tests.fixtures.backends import setup_memory

    data = [
        {"id": 1, "name": "Alice", "age": 30, "email": "a@test.com"},
        {"id": 2, "name": "Alice", "age": 25, "email": "b@test.com"},
        {"id": 3, "name": "Bob", "age": 30, "email": "c@test.com"},
    ]
    env = await setup_memory(data=data)
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            sorting=[
                SortSpec(field="name", direction=SortDirection.ASC),
                SortSpec(field="age", direction=SortDirection.ASC),
            ],
        )
    )
    names_ages = [(env.get_field(item, "name"), env.get_field(item, "age")) for item in page.items]
    assert names_ages == [("Alice", 25), ("Alice", 30), ("Bob", 30)]
