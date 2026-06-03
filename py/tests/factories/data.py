"""Dataset generators for test fixtures.

Lightweight factory functions producing typed dicts
for users, products, and generic records.
"""

from __future__ import annotations

from typing import Any


_CATEGORIES = ("electronics", "books", "clothing", "food")


def make_users(count: int = 8) -> list[dict[str, Any]]:
    """Generate diverse user dicts with name, age, email, active."""
    return [
        {
            "id": i,
            "name": f"User_{i}",
            "age": 20 + (i % 50),
            "email": f"user{i}@test.com",
            "active": i % 3 != 0,
        }
        for i in range(count)
    ]


def make_products(count: int = 50) -> list[dict[str, Any]]:
    """Generate product dicts with price and category."""
    return [
        {
            "id": i,
            "name": f"Product_{i}",
            "price": 10.0 + (i * 1.5),
            "category": _CATEGORIES[i % len(_CATEGORIES)],
            "in_stock": i % 5 != 0,
        }
        for i in range(count)
    ]


def make_records(count: int = 100) -> list[dict[str, Any]]:
    """Generic records with mixed types for edge-case testing."""
    return [
        {
            "id": i,
            "value": i if i % 3 else None,
            "label": f"record_{i}" if i % 2 else "",
            "nested": {"score": i * 0.1},
        }
        for i in range(count)
    ]


__all__ = ["make_products", "make_records", "make_users"]
