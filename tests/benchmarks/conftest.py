"""Benchmark test configuration.

This conftest is for tests in the benchmarks/ directory.
"""

from __future__ import annotations

import pytest


# Auto-apply benchmark marker to all tests in this directory
pytestmark = pytest.mark.benchmark
