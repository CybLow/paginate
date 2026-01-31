"""Sample test data for fixtures.

This module provides sample data and helper functions for creating
test data across the test suite.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from tests.fixtures.models import Order, Product, User


if TYPE_CHECKING:
    pass


# Sample user data
TEST_USERS_DATA = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"},
    {"name": "David", "email": "david@example.com"},
    {"name": "Eve", "email": "eve@example.com"},
    {"name": "Frank", "email": "frank@example.com"},
    {"name": "Grace", "email": "grace@example.com"},
    {"name": "Henry", "email": "henry@example.com"},
    {"name": "Ivy", "email": "ivy@example.com"},
    {"name": "Jack", "email": "jack@example.com"},
]

# Sample product data
TEST_PRODUCTS_DATA = [
    {"name": "Laptop", "price": Decimal("999.99"), "category": "Electronics"},
    {"name": "Mouse", "price": Decimal("29.99"), "category": "Electronics"},
    {"name": "Keyboard", "price": Decimal("79.99"), "category": "Electronics"},
    {"name": "Monitor", "price": Decimal("299.99"), "category": "Electronics"},
    {"name": "Desk Chair", "price": Decimal("199.99"), "category": "Furniture"},
    {"name": "Standing Desk", "price": Decimal("499.99"), "category": "Furniture"},
    {"name": "Notebook", "price": Decimal("4.99"), "category": "Office Supplies"},
    {"name": "Pen Set", "price": Decimal("12.99"), "category": "Office Supplies"},
]


def create_test_users(count: int | None = None) -> list[User]:
    """Create test User instances.

    Args:
        count: Number of users to create. Defaults to all available.

    Returns:
        A list of User instances.
    """
    data = TEST_USERS_DATA if count is None else TEST_USERS_DATA[:count]
    return [User(**user_data) for user_data in data]


def create_test_products(count: int | None = None) -> list[Product]:
    """Create test Product instances.

    Args:
        count: Number of products to create. Defaults to all available.

    Returns:
        A list of Product instances.
    """
    data = TEST_PRODUCTS_DATA if count is None else TEST_PRODUCTS_DATA[:count]
    return [Product(**product_data) for product_data in data]


def create_test_orders(users: list[User], products_per_user: int = 2) -> list[Order]:
    """Create test Order instances for the given users.

    Args:
        users: List of users to create orders for.
        products_per_user: Number of orders per user.

    Returns:
        A list of Order instances.
    """
    orders = []
    for user in users:
        for i in range(products_per_user):
            order = Order(
                user_id=user.id,
                total=Decimal(f"{(i + 1) * 50}.00"),
                status="completed" if i % 2 == 0 else "pending",
                created_at=datetime.now(UTC),
            )
            orders.append(order)
    return orders


def create_large_dataset(count: int) -> list[dict[str, str]]:
    """Create a large dataset for performance testing.

    Args:
        count: Number of items to create.

    Returns:
        A list of dictionaries with name and email.
    """
    return [
        {"name": f"User_{i:05d}", "email": f"user_{i:05d}@example.com"}
        for i in range(count)
    ]


__all__ = [
    "TEST_PRODUCTS_DATA",
    "TEST_USERS_DATA",
    "create_large_dataset",
    "create_test_orders",
    "create_test_products",
    "create_test_users",
]
