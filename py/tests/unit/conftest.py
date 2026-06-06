"""Local fixtures for the in-memory core unit tests.

Self-contained sample data only — no shared/root conftest is defined here so
that sibling test categories keep ownership of their own fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class Person:
    """A tiny attribute-access record (proves the engine reads objects too)."""

    name: str
    age: int
    city: str | None


@pytest.fixture
def people() -> list[dict[str, object]]:
    """A small list-of-dicts dataset used across the query/dataset tests."""
    return [
        {"name": "Alice", "age": 30, "city": "Paris"},
        {"name": "bob", "age": 25, "city": "Lyon"},
        {"name": "Carol", "age": 40, "city": None},
        {"name": "Dave", "age": 25, "city": "Paris"},
    ]


@pytest.fixture
def person_objects() -> list[Person]:
    """The same dataset as attribute-access objects."""
    return [
        Person(name="Alice", age=30, city="Paris"),
        Person(name="bob", age=25, city="Lyon"),
        Person(name="Carol", age=40, city=None),
    ]
