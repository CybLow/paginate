"""Root pytest configuration for the real-condition test lanes.

Registers the suite's markers, adds the ``--run-slow`` / ``--run-benchmark`` opt-in
flags, auto-marks tests by their directory, and exposes the shared deterministic
``users`` dataset. Everything here is built against the *new* public API — there
are no engine/backend imports.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING


# Make the ``py/`` root importable so ``tests.factories`` / ``tests.fixtures``
# resolve as packages regardless of pytest's import-mode rootdir insertion.
_PY_ROOT = Path(__file__).resolve().parent.parent
if str(_PY_ROOT) not in sys.path:
    sys.path.insert(0, str(_PY_ROOT))

import pytest
from tests.factories.data import make_users

from pypaginate import Dataset


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.nodes import Item


# Expose the database session fixtures (sqlite sync/async + postgres) suite-wide.
pytest_plugins = ("tests.fixtures.database",)


# -- Hooks ------------------------------------------------------------------- #

_MARKERS: tuple[str, ...] = (
    "unit: fast in-memory unit tests",
    "integration: integration tests (real DB / framework deps)",
    "e2e: end-to-end scenario tests",
    "property: property-based tests",
    "benchmark: performance benchmark tests (opt-in via --run-benchmark)",
    "slow: slow tests (opt-in via --run-slow)",
    "postgres: tests requiring a real PostgreSQL instance",
    "sqlalchemy: tests requiring SQLAlchemy",
    "fastapi: tests requiring FastAPI",
    "keyset: keyset/cursor pagination tests",
    "filters: filtering tests",
    "sorting: sorting tests",
    "search: search tests",
)


def pytest_configure(config: Config) -> None:
    """Register every suite marker so ``--strict-markers`` stays satisfied."""
    for marker in _MARKERS:
        config.addinivalue_line("markers", marker)


def pytest_addoption(parser: Parser) -> None:
    """Add the ``--run-slow`` / ``--run-benchmark`` opt-in flags."""
    parser.addoption("--run-slow", action="store_true", default=False, help="run slow tests")
    parser.addoption(
        "--run-benchmark", action="store_true", default=False, help="run benchmark tests"
    )


_DIR_MARKERS: dict[str, str] = {
    "/unit/": "unit",
    "/integration/": "integration",
    "/e2e/": "e2e",
    "/property/": "property",
    "/perf/": "benchmark",
}


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Auto-mark by directory, then skip benchmark/slow tests unless opted in."""
    for item in items:
        _mark_by_directory(item)
    _skip_unless_opted_in(config, items)


def _mark_by_directory(item: Item) -> None:
    """Apply the directory marker matching the item's file path (if any)."""
    path = str(item.fspath)
    for fragment, name in _DIR_MARKERS.items():
        if fragment in path:
            item.add_marker(getattr(pytest.mark, name))
            return


def _skip_unless_opted_in(config: Config, items: list[Item]) -> None:
    """Skip ``benchmark`` / ``slow`` items unless their opt-in flag is set."""
    gates = (
        ("benchmark", config.getoption("--run-benchmark"), "needs --run-benchmark"),
        ("slow", config.getoption("--run-slow"), "needs --run-slow"),
    )
    for marker, enabled, reason in gates:
        if enabled:
            continue
        skip = pytest.mark.skip(reason=reason)
        for item in items:
            if marker in item.keywords:
                item.add_marker(skip)


# -- Fixtures ---------------------------------------------------------------- #


@pytest.fixture
def users() -> list[dict[str, object]]:
    """A deterministic 50-row user dataset shared across the lanes."""
    return make_users(50)


@pytest.fixture
def dataset(users: list[dict[str, object]]) -> Dataset[dict[str, object]]:
    """A native :class:`Dataset` marshalled over the shared ``users`` rows."""
    return Dataset(users)
