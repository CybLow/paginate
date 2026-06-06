"""Local Hypothesis configuration for the property suite.

Registers and loads a profile with the deadline disabled so the native engine's
first-call warm-up cannot trip a per-example timing failure, and a bounded
example count that keeps the suite fast and deterministic. Scoped to this
directory only; sibling test categories are owned by other agents.
"""

from __future__ import annotations

from hypothesis import HealthCheck, settings


settings.register_profile(
    "property",
    deadline=None,
    max_examples=150,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("property")
