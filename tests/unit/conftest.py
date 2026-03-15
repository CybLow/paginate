"""Unit-specific fixtures.

Engine fixtures (filter_engine, sort_engine, search_engine, filter_registry)
are inherited from root ``tests/conftest.py`` — do NOT redefine them here.

This module provides:
- ``sample_users``: 4 named users (Alice, Bob, Charlie, Diana)
- ``search_items``: 4 items with name + email for search tests
"""

from __future__ import annotations

from typing import Any

import pytest


# -- Data fixtures -----------------------------------------------------------


@pytest.fixture()
def sample_users() -> list[dict[str, Any]]:
    """Four users with name, age, email for unit tests.

    Overrides root conftest sample_users (8 users from make_users).
    """
    return [
        {"name": "Alice", "age": 30, "email": "alice@test.com"},
        {"name": "Bob", "age": 25, "email": "bob@test.com"},
        {"name": "Charlie", "age": 35, "email": "charlie@test.com"},
        {"name": "Diana", "age": 28, "email": "diana@test.com"},
    ]


@pytest.fixture()
def search_items() -> list[dict[str, str]]:
    """Four items with name and email for search tests."""
    return [
        {"name": "Alice Johnson", "email": "alice@example.com"},
        {"name": "Bob Smith", "email": "bob@example.com"},
        {"name": "Charlie Brown", "email": "charlie@test.com"},
        {"name": "Diana Prince", "email": "diana@example.com"},
    ]
