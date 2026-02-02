"""E2E test configuration.

This conftest is for tests in the e2e/ directory.
End-to-end tests simulate real usage scenarios.
"""

from __future__ import annotations

import pytest


# Auto-apply e2e marker to all tests in this directory
pytestmark = pytest.mark.e2e
