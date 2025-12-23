"""Predicate-based filtering for pagination."""

from .builder import JsonLogicPredicateBuilder
from .engine import CompiledFilter, FilterEngine, filter_items
from .field_accessor import FieldAccessor
from .registry import FilterPredicate, OperatorFactory, OperatorRegistry


__all__ = [
    "CompiledFilter",
    # Accesseurs
    "FieldAccessor",
    # Engine principal
    "FilterEngine",
    "FilterPredicate",
    # Builders
    "JsonLogicPredicateBuilder",
    "OperatorFactory",
    # Registry
    "OperatorRegistry",
    "filter_items",
]
