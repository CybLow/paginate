"""Smoke tests verifying the BackendEnv registry works."""

from __future__ import annotations

from pypaginate.domain.models import OffsetPage, OffsetParams
from tests.fixtures.backends import BackendEnv
from tests.fixtures.helpers import run


async def test_backend_env_has_correct_total(backend_env: BackendEnv) -> None:
    """Each backend starts with 8 seed items."""
    assert backend_env.total == 8


async def test_paginate_via_env(backend_env: BackendEnv) -> None:
    """Paginate page-1 through the env helper."""
    result = backend_env.do_paginate(backend_env.query, OffsetParams(page=1, limit=3))
    page = await run(result)
    assert isinstance(page, OffsetPage)
    assert page.total == backend_env.total
    assert len(page.items) == 3


async def test_pipeline_via_env(backend_env: BackendEnv) -> None:
    """Pipeline execute returns a valid page."""
    result = backend_env.do_pipeline(
        backend_env.query,
        OffsetParams(page=1, limit=5),
    )
    page = await run(result)
    assert isinstance(page, OffsetPage)
    assert page.total == backend_env.total
    assert len(page.items) == 5
