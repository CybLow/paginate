"""Root pytest configuration with hooks and shared fixtures.

Provides auto-markers by directory, custom CLI options,
and fixtures available to all test categories.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

import pytest

from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import OperatorRegistry, create_default_registry
from pypaginate.search.engine import SearchEngine
from pypaginate.sorting.engine import SortEngine
from tests.factories.data import make_users
from tests.fixtures.backends import BACKEND_REGISTRY, BackendEnv


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.nodes import Item


# -- Hooks -------------------------------------------------------------------


def pytest_configure(config: Config) -> None:
    """Register custom markers for IDE and --strict-markers."""
    markers = [
        "unit: Unit tests",
        "integration: Integration tests",
        "e2e: End-to-end tests",
        "property: Property-based tests",
        "stress: Stress tests",
        "benchmark: Performance benchmarks",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add --run-slow and --run-benchmark CLI options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )
    parser.addoption(
        "--run-benchmark",
        action="store_true",
        default=False,
        help="Run benchmark tests",
    )


_MARKER_MAP: dict[str, str] = {
    "/unit/": "unit",
    "/integration/": "integration",
    "/e2e/": "e2e",
    "/property/": "property",
    "/benchmarks/": "benchmark",
    "/perf/": "benchmark",
}


def pytest_collection_modifyitems(
    config: Config,
    items: list[Item],
) -> None:
    """Auto-apply markers by directory and skip slow/benchmark."""
    _skip_by_option(config, items)
    _apply_directory_markers(items)


def _skip_by_option(config: Config, items: list[Item]) -> None:
    """Skip slow and benchmark tests unless opted in."""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="use --run-slow")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

    run_bench = config.getoption("--run-benchmark", default=False)
    bench_on = (
        config.getoption("--benchmark-enable", default=False)
        if hasattr(config.option, "benchmark_enable")
        else False
    )
    if not run_bench and not bench_on:
        skip_bench = pytest.mark.skip(reason="use --run-benchmark")
        for item in items:
            if "benchmark" in item.keywords:
                item.add_marker(skip_bench)


def _apply_directory_markers(items: list[Item]) -> None:
    """Add markers based on test file path."""
    for item in items:
        path = str(item.fspath)
        for fragment, name in _MARKER_MAP.items():
            if fragment in path:
                item.add_marker(getattr(pytest.mark, name))
                break


# -- Fixtures: backend_env --------------------------------------------------


@pytest.fixture(params=list(BACKEND_REGISTRY.keys()))
async def backend_env(
    request: pytest.FixtureRequest,
) -> AsyncGenerator[BackendEnv, None]:
    """Yield a BackendEnv for every registered backend (8 items)."""
    setup_fn = BACKEND_REGISTRY[request.param]
    env = await setup_fn()
    yield env
    if env.cleanup:
        await env.cleanup()


# -- Fixtures: engines -------------------------------------------------------


@pytest.fixture()
def filter_registry() -> OperatorRegistry:
    """Default operator registry with all built-in operators."""
    return create_default_registry()


@pytest.fixture()
def filter_engine(filter_registry: OperatorRegistry) -> FilterEngine:
    """FilterEngine backed by the default registry."""
    return FilterEngine(filter_registry)


@pytest.fixture()
def sort_engine() -> SortEngine:
    """Stateless SortEngine instance."""
    return SortEngine()


@pytest.fixture()
def search_engine() -> SearchEngine:
    """SearchEngine with default TokenParser."""
    return SearchEngine()


# -- Fixtures: data ----------------------------------------------------------


@pytest.fixture()
def sample_users() -> list[dict[str, Any]]:
    """Eight diverse users with name, age, email, active."""
    return make_users()


@pytest.fixture()
def large_dataset() -> list[dict[str, Any]]:
    """1000 user dicts for performance tests.

    Note: overridden in tests/benchmarks/conftest.py (session-scoped, 10k)
    and tests/e2e/conftest.py (100 items with more fields).
    """
    return [
        {"id": i, "name": f"User_{i}", "age": 20 + i % 50, "email": f"u{i}@test.com"}
        for i in range(1_000)
    ]
