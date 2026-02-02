"""Test data factories using factory_boy.

This module provides factory classes for generating test data
with realistic fake values.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import factory
from faker import Faker

from tests.fixtures.models import Product, User


if TYPE_CHECKING:
    pass


fake = Faker()
Faker.seed(42)  # Reproducible fake data


class UserFactory(factory.Factory):
    """Factory for User model instances.

    Usage:
        user = UserFactory.build()  # Create without saving
        user = UserFactory.create()  # Create and save (if using SQLAlchemy strategy)
        users = UserFactory.build_batch(10)  # Create multiple
    """

    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))


class ProductFactory(factory.Factory):
    """Factory for Product model instances.

    Usage:
        product = ProductFactory.build()
        product = ProductFactory.build(category="Electronics")  # Override
    """

    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(fake.word)
    description = factory.LazyFunction(fake.sentence)
    price = factory.LazyFunction(
        lambda: Decimal(str(round(fake.pyfloat(min_value=1, max_value=1000), 2)))
    )
    category = factory.LazyFunction(
        lambda: fake.random_element(["Electronics", "Furniture", "Office Supplies", "Books"])
    )
    in_stock = factory.LazyFunction(lambda: fake.boolean(chance_of_getting_true=80))
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))


class UserBatchFactory:
    """Utility class for creating batches of users with specific patterns."""

    @staticmethod
    def create_batch(count: int) -> list[User]:
        """Create a batch of users with unique data.

        Args:
            count: Number of users to create.

        Returns:
            A list of User instances.
        """
        return [UserFactory.build() for _ in range(count)]

    @staticmethod
    def create_with_pattern(pattern: str, count: int) -> list[User]:
        """Create users with names matching a pattern.

        Args:
            pattern: The name prefix pattern.
            count: Number of users to create.

        Returns:
            A list of User instances with patterned names.
        """
        return [
            UserFactory.build(name=f"{pattern}_{i}", email=f"{pattern.lower()}_{i}@example.com")
            for i in range(count)
        ]

    @staticmethod
    def create_alphabetical(count: int = 26) -> list[User]:
        """Create users with alphabetically ordered names.

        Args:
            count: Number of users to create (max 26).

        Returns:
            A list of User instances with names A, B, C, etc.
        """
        count = min(count, 26)
        return [
            UserFactory.build(name=chr(65 + i), email=f"{chr(97 + i)}@example.com")
            for i in range(count)
        ]

    @staticmethod
    def create_with_emails(emails: list[str]) -> list[User]:
        """Create users with specific emails.

        Args:
            emails: List of email addresses.

        Returns:
            A list of User instances with the specified emails.
        """
        return [UserFactory.build(email=email) for email in emails]


class ProductBatchFactory:
    """Utility class for creating batches of products."""

    @staticmethod
    def create_batch(count: int) -> list[Product]:
        """Create a batch of products.

        Args:
            count: Number of products to create.

        Returns:
            A list of Product instances.
        """
        return [ProductFactory.build() for _ in range(count)]

    @staticmethod
    def create_by_category(category: str, count: int) -> list[Product]:
        """Create products in a specific category.

        Args:
            category: The product category.
            count: Number of products to create.

        Returns:
            A list of Product instances in the category.
        """
        return [ProductFactory.build(category=category) for _ in range(count)]

    @staticmethod
    def create_price_range(min_price: Decimal, max_price: Decimal, count: int) -> list[Product]:
        """Create products within a price range.

        Args:
            min_price: Minimum price.
            max_price: Maximum price.
            count: Number of products to create.

        Returns:
            A list of Product instances within the price range.
        """
        products = []
        for i in range(count):
            # Linear distribution across the range
            ratio = i / max(count - 1, 1)
            price = min_price + (max_price - min_price) * Decimal(str(ratio))
            products.append(ProductFactory.build(price=price.quantize(Decimal("0.01"))))
        return products


def create_test_fixture(model: str, count: int = 10, **overrides: Any) -> list[Any]:
    """Generic factory function for creating test fixtures.

    Args:
        model: The model name ("user" or "product").
        count: Number of instances to create.
        **overrides: Field overrides to apply to all instances.

    Returns:
        A list of model instances.

    Raises:
        ValueError: If the model name is unknown.
    """
    factories: dict[str, type[factory.Factory]] = {
        "user": UserFactory,
        "product": ProductFactory,
    }

    if model not in factories:
        msg = f"Unknown model: {model}. Available: {list(factories.keys())}"
        raise ValueError(msg)

    factory_class = factories[model]
    return [factory_class.build(**overrides) for _ in range(count)]


__all__ = [
    "ProductBatchFactory",
    "ProductFactory",
    "UserBatchFactory",
    "UserFactory",
    "create_test_fixture",
]
