"""Shared fixtures for the core performance benchmarks.

The factory rows and the marshalled :class:`Dataset` are built once per session
and reused across every benchmark, so the timings measure the operation under
test rather than data generation or the one-time marshal. All data comes from the
deterministic ``make_users`` factory.
"""

from __future__ import annotations

import pytest
from tests.factories.data import make_users

from pypaginate import Dataset


@pytest.fixture(scope="session")
def dataset_1k() -> list[dict[str, object]]:
    """1K deterministic user rows."""
    return make_users(1_000)


@pytest.fixture(scope="session")
def dataset_10k() -> list[dict[str, object]]:
    """10K deterministic user rows."""
    return make_users(10_000)


@pytest.fixture(scope="session")
def native_1k(dataset_1k: list[dict[str, object]]) -> Dataset[dict[str, object]]:
    """A :class:`Dataset` marshalled once over the 1K rows."""
    return Dataset(dataset_1k)


@pytest.fixture(scope="session")
def native_10k(dataset_10k: list[dict[str, object]]) -> Dataset[dict[str, object]]:
    """A :class:`Dataset` marshalled once over the 10K rows."""
    return Dataset(dataset_10k)
