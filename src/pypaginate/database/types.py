"""Concrete aliases for SQLAlchemy types used by the pagination module.

This module intentionally exposes concrete vendor type aliases and avoids
structural ``Protocol`` definitions for SQLAlchemy interfaces, in accordance
with the facade policy.
"""

from __future__ import annotations

from typing import TypeAlias, TypeVar

from sqlalchemy import Select
from sqlalchemy.engine import Result as SAResult, ScalarResult as SAScalarResult


RowT = TypeVar("RowT", covariant=True)
"""Covariant type variable for row tuple types."""

ItemT = TypeVar("ItemT")
"""Type variable for individual item types."""

SelectStatement: TypeAlias = Select[tuple[object, ...]]
"""Concrete alias for a typed SQLAlchemy Select statement.

Represents the base selectable used across pagination helpers.
"""

CountStatement: TypeAlias = Select[tuple[int]]
"""Concrete alias for a typed count statement returning a single integer."""

Result: TypeAlias = SAResult[ItemT]
"""Concrete alias for SQLAlchemy Result over ItemT payloads."""

ScalarResult: TypeAlias = SAScalarResult[ItemT]
"""Concrete alias for SQLAlchemy ScalarResult over ItemT payloads."""

ResultSequence: TypeAlias = Result[ItemT] | ScalarResult[ItemT]
"""Union of Result and ScalarResult used during materialization."""


__all__ = [
    "CountStatement",
    "Result",
    "ResultSequence",
    "ScalarResult",
    "SelectStatement",
]
