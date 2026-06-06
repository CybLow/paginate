"""E2E-local fixtures.

The shared ``users`` / ``dataset`` fixtures come from the root ``conftest.py``;
this module only adds the few extras the scenario flows need (rows carrying
``None`` for the null-placement sort flows and a larger pool for full page walks).
"""

from __future__ import annotations

import pytest
from tests.factories.data import make_users


@pytest.fixture
def big_users() -> list[dict[str, object]]:
    """A larger deterministic pool (200 rows) for multi-page walk flows."""
    return make_users(200)


@pytest.fixture
def nullable_rows() -> list[dict[str, object]]:
    """Rows whose ``score`` is sometimes ``None`` (for null-placement flows)."""
    return [
        {"id": 1, "score": 30},
        {"id": 2, "score": None},
        {"id": 3, "score": 10},
        {"id": 4, "score": None},
        {"id": 5, "score": 20},
    ]
