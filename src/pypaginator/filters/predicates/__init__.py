"""Predicate-based filtering for pagination."""

from .builder import JsonLogicPredicateBuilder
from .engine import CompiledFilter, FilterEngine, filter_items
from .field_accessor import FieldAccessor
from .registry import FilterPredicate, OperatorFactory, OperatorRegistry

__all__ = [
    # Engine principal
    "FilterEngine",
    "filter_items",
    "CompiledFilter",
    # Accesseurs
    "FieldAccessor",
    # Builders
    "JsonLogicPredicateBuilder",
    # Registry
    "OperatorRegistry",
    "FilterPredicate",
    "OperatorFactory",
]
