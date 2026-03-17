"""Universal filtering -- backend-agnostic predicate evaluation."""

from __future__ import annotations

from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import OperatorRegistry, create_default_registry


__all__ = ["FilterEngine", "OperatorRegistry", "create_default_registry"]
