"""Benchmark test configuration.

Provides reusable datasets for benchmark tests.
Benchmarks are skipped unless --benchmark-enable is passed.
"""

from __future__ import annotations

from typing import Any

import pytest


pytestmark = pytest.mark.benchmark


@pytest.fixture(scope="session")
def small_dataset() -> list[dict[str, Any]]:
    """100-item dict dataset for benchmarks."""
    return _build_users(100)


@pytest.fixture(scope="session")
def medium_dataset() -> list[dict[str, Any]]:
    """1,000-item dict dataset for benchmarks."""
    return _build_users(1_000)


@pytest.fixture(scope="session")
def large_dataset() -> list[dict[str, Any]]:
    """10,000-item dict dataset for benchmarks.

    Overrides root conftest large_dataset (1000 items, function-scoped).
    """
    return _build_users(10_000)


def _build_users(count: int) -> list[dict[str, Any]]:
    """Generate user dicts with id, name, age, email."""
    return [
        {
            "id": i,
            "name": f"user_{i}",
            "age": 20 + i % 50,
            "email": f"u{i}@test.com",
        }
        for i in range(count)
    ]
