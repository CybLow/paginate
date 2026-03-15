"""E2E test configuration and shared fixtures.

Provides reusable datasets for end-to-end pagination scenarios.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def large_dataset() -> list[dict[str, object]]:
    """100 items with name, age, email, active fields.

    Overrides root conftest large_dataset (1000 simpler dicts).
    """
    return [
        {
            "id": i,
            "name": f"User_{i}",
            "age": 20 + (i % 50),
            "email": f"user{i}@test.com",
            "active": i % 3 != 0,
        }
        for i in range(100)
    ]
