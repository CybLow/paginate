"""Property-based test configuration.

This conftest is for tests in the property/ directory using Hypothesis.
"""

from __future__ import annotations

import pytest

try:
    from hypothesis import settings, Phase
    
    # Configure Hypothesis for property tests
    settings.register_profile("ci", max_examples=100, phases=[Phase.generate, Phase.reuse, Phase.shrink])
    settings.register_profile("dev", max_examples=20, phases=[Phase.generate, Phase.shrink])
    settings.register_profile("debug", max_examples=10, phases=[Phase.generate])
    
    # Load based on environment
    import os
    profile = os.getenv("HYPOTHESIS_PROFILE", "dev")
    settings.load_profile(profile)
    
except ImportError:
    pass  # Hypothesis not installed


# Auto-apply property marker to all tests in this directory
pytestmark = pytest.mark.property
