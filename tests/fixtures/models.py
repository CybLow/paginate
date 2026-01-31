"""Test models for integration tests.

This module provides SQLAlchemy models used across integration tests.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


if TYPE_CHECKING:
    pass


class Base(DeclarativeBase):
    """Base class for SQLAlchemy test models."""

    pass


class User(Base):
    """Sample user model for integration tests.

    Attributes:
        id: Primary key.
        name: User's display name.
        email: User's email address.
        created_at: Account creation timestamp.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    # Relationships
    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


class Product(Base):
    """Sample product model for integration tests.

    Attributes:
        id: Primary key.
        name: Product name.
        description: Product description.
        price: Product price.
        category: Product category.
        in_stock: Whether the product is in stock.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(100))
    in_stock: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name!r}, price={self.price})"


class Order(Base):
    """Sample order model for integration tests with relationships.

    Attributes:
        id: Primary key.
        user_id: Foreign key to users.
        total: Order total.
        status: Order status.
        created_at: Order creation timestamp.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")

    def __repr__(self) -> str:
        return f"Order(id={self.id}, user_id={self.user_id}, total={self.total})"


__all__ = [
    "Base",
    "Order",
    "Product",
    "User",
]
