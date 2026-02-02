"""Integration test configuration.

This conftest is for tests in the integration/ directory.
Integration tests may use real databases and external services.
"""

from __future__ import annotations

import pytest


# Auto-apply integration marker to all tests in this directory
pytestmark = pytest.mark.integration


# Integration test specific fixtures can be defined here
