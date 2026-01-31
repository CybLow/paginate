"""Unit test configuration.

This conftest is for tests in the unit/ directory.
Unit tests should be fast and not require external dependencies.
"""

from __future__ import annotations

import pytest


# Auto-apply unit marker to all tests in this directory
pytestmark = pytest.mark.unit


# Unit test specific fixtures can be defined here
