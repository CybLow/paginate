"""Tests for the SQL filter adapter module.

This module tests the SqlFilterAdapter class which converts filter operators
into SQLAlchemy filter conditions.
"""

from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from pypaginate.filters.sql_adapter import SqlFilterAdapter


# Test model
class Base(DeclarativeBase):
    """Base class for test models."""

    pass


class Product(Base):
    """Sample product model for testing SQL filters."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    category = Column(String(50))
    price = Column(Integer)


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def session(engine):
    """Create a database session with test data."""
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)
    session = session_local()

    # Insert test data
    products = [
        Product(id=1, name="Laptop", category="Electronics", price=1000),
        Product(id=2, name="Mouse", category="Electronics", price=25),
        Product(id=3, name="Keyboard", category="Electronics", price=75),
        Product(id=4, name="Chair", category="Furniture", price=200),
        Product(id=5, name="Desk", category="Furniture", price=500),
    ]
    session.add_all(products)
    session.commit()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


class TestSqlFilterAdapterBuildCondition:
    """Tests for SqlFilterAdapter.build_condition method."""

    def test_equals_operator(self, session: Session) -> None:
        """Test equality (eq/equals) operator."""
        condition = SqlFilterAdapter.build_condition(Product.category, "eq", "Electronics")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3
        assert all(p.category == "Electronics" for p in results)

        # Test 'equals' alias
        condition = SqlFilterAdapter.build_condition(Product.category, "equals", "Furniture")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2

    def test_not_equals_operator(self, session: Session) -> None:
        """Test not equal (ne/not_equals) operator."""
        condition = SqlFilterAdapter.build_condition(Product.category, "ne", "Electronics")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2
        assert all(p.category != "Electronics" for p in results)

        # Test 'not_equals' alias
        condition = SqlFilterAdapter.build_condition(Product.category, "not_equals", "Furniture")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3

    def test_greater_than_operator(self, session: Session) -> None:
        """Test greater than (gt/greater_than) operator."""
        condition = SqlFilterAdapter.build_condition(Product.price, "gt", 100)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3
        assert all(p.price > 100 for p in results)

        # Test 'greater_than' alias
        condition = SqlFilterAdapter.build_condition(Product.price, "greater_than", 500)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].price == 1000

    def test_greater_than_or_equal_operator(self, session: Session) -> None:
        """Test greater than or equal (gte/greater_than_or_equal) operator."""
        condition = SqlFilterAdapter.build_condition(Product.price, "gte", 200)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3
        assert all(p.price >= 200 for p in results)

        # Test 'greater_than_or_equal' alias
        condition = SqlFilterAdapter.build_condition(Product.price, "greater_than_or_equal", 500)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2

    def test_less_than_operator(self, session: Session) -> None:
        """Test less than (lt/less_than) operator."""
        condition = SqlFilterAdapter.build_condition(Product.price, "lt", 100)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2
        assert all(p.price < 100 for p in results)

        # Test 'less_than' alias
        condition = SqlFilterAdapter.build_condition(Product.price, "less_than", 200)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2  # Mouse (25) and Keyboard (75)

    def test_less_than_or_equal_operator(self, session: Session) -> None:
        """Test less than or equal (lte/less_than_or_equal) operator."""
        condition = SqlFilterAdapter.build_condition(Product.price, "lte", 75)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2
        assert all(p.price <= 75 for p in results)

        # Test 'less_than_or_equal' alias
        condition = SqlFilterAdapter.build_condition(Product.price, "less_than_or_equal", 200)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3  # Mouse (25), Keyboard (75), Chair (200)

    def test_in_operator_with_list(self, session: Session) -> None:
        """Test IN operator with a list of values."""
        condition = SqlFilterAdapter.build_condition(
            Product.category, "in", ["Electronics", "Furniture"]
        )
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 5

        condition = SqlFilterAdapter.build_condition(Product.id, "in", [1, 3, 5])
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3
        assert {p.id for p in results} == {1, 3, 5}

    def test_in_operator_with_tuple(self, session: Session) -> None:
        """Test IN operator with a tuple of values."""
        condition = SqlFilterAdapter.build_condition(Product.id, "in", (2, 4))
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2
        assert {p.id for p in results} == {2, 4}

    def test_in_operator_with_set(self, session: Session) -> None:
        """Test IN operator with a set of values."""
        condition = SqlFilterAdapter.build_condition(Product.category, "in", {"Electronics"})
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3

    def test_in_operator_with_single_value(self, session: Session) -> None:
        """Test IN operator with a single value (falls back to equality)."""
        condition = SqlFilterAdapter.build_condition(Product.category, "in", "Electronics")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3

    def test_not_in_operator_with_list(self, session: Session) -> None:
        """Test NOT IN operator with a list of values."""
        condition = SqlFilterAdapter.build_condition(Product.id, "not_in", [1, 2])
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3
        assert {p.id for p in results} == {3, 4, 5}

    def test_not_in_operator_with_tuple(self, session: Session) -> None:
        """Test NOT IN operator with a tuple of values."""
        condition = SqlFilterAdapter.build_condition(Product.category, "not_in", ("Electronics",))
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2
        assert all(p.category == "Furniture" for p in results)

    def test_not_in_operator_with_single_value(self, session: Session) -> None:
        """Test NOT IN operator with a single value (falls back to not equal)."""
        condition = SqlFilterAdapter.build_condition(Product.category, "not_in", "Electronics")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 2

    def test_like_operator(self, session: Session) -> None:
        """Test LIKE operator for pattern matching."""
        condition = SqlFilterAdapter.build_condition(Product.name, "like", "K%")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].name == "Keyboard"

        condition = SqlFilterAdapter.build_condition(Product.name, "like", "%top")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].name == "Laptop"

    def test_ilike_operator(self, session: Session) -> None:
        """Test ILIKE operator for case-insensitive pattern matching."""
        condition = SqlFilterAdapter.build_condition(Product.name, "ilike", "laptop")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].name == "Laptop"

        condition = SqlFilterAdapter.build_condition(Product.name, "ilike", "%CHAIR%")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1

    def test_is_null_operator_true(self, session: Session) -> None:
        """Test IS NULL operator when value is True."""
        # Add a product with null category
        product = Product(id=6, name="Unknown", category=None, price=0)
        session.add(product)
        session.commit()

        condition = SqlFilterAdapter.build_condition(Product.category, "is_null", True)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].category is None

    def test_is_null_operator_false(self, session: Session) -> None:
        """Test IS NOT NULL operator when value is False."""
        condition = SqlFilterAdapter.build_condition(Product.category, "is_null", False)
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 5
        assert all(p.category is not None for p in results)

    def test_contains_operator(self, session: Session) -> None:
        """Test CONTAINS operator."""
        condition = SqlFilterAdapter.build_condition(Product.name, "contains", "top")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert "top" in results[0].name

    def test_startswith_operator(self, session: Session) -> None:
        """Test STARTSWITH operator."""
        condition = SqlFilterAdapter.build_condition(Product.name, "startswith", "K")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].name.startswith("K")

        condition = SqlFilterAdapter.build_condition(Product.category, "startswith", "Ele")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 3

    def test_endswith_operator(self, session: Session) -> None:
        """Test ENDSWITH operator."""
        condition = SqlFilterAdapter.build_condition(Product.name, "endswith", "top")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].name.endswith("top")

        condition = SqlFilterAdapter.build_condition(Product.name, "endswith", "sk")
        results = session.execute(select(Product).where(condition)).scalars().all()
        assert len(results) == 1
        assert results[0].name == "Desk"

    def test_unsupported_operator(self) -> None:
        """Test that unsupported operators raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported filter operator: invalid_op"):
            SqlFilterAdapter.build_condition(Product.name, "invalid_op", "value")


class TestSqlFilterAdapterCombineConditions:
    """Tests for SqlFilterAdapter.combine_conditions method."""

    def test_combine_with_and_logic(self, session: Session) -> None:
        """Test combining multiple conditions with AND logic."""
        cond1 = SqlFilterAdapter.build_condition(Product.category, "eq", "Electronics")
        cond2 = SqlFilterAdapter.build_condition(Product.price, "lt", 100)

        combined = SqlFilterAdapter.combine_conditions([cond1, cond2], logic="and")
        results = session.execute(select(Product).where(combined)).scalars().all()

        assert len(results) == 2
        assert all(p.category == "Electronics" and p.price < 100 for p in results)

    def test_combine_with_or_logic(self, session: Session) -> None:
        """Test combining multiple conditions with OR logic."""
        cond1 = SqlFilterAdapter.build_condition(Product.category, "eq", "Furniture")
        cond2 = SqlFilterAdapter.build_condition(Product.price, "lt", 50)

        combined = SqlFilterAdapter.combine_conditions([cond1, cond2], logic="or")
        results = session.execute(select(Product).where(combined)).scalars().all()

        assert len(results) == 3  # 2 Furniture + 1 Mouse (price=25)
        assert all(p.category == "Furniture" or p.price < 50 for p in results)

    def test_combine_single_condition(self, session: Session) -> None:
        """Test that a single condition is returned as-is."""
        cond1 = SqlFilterAdapter.build_condition(Product.category, "eq", "Electronics")

        combined = SqlFilterAdapter.combine_conditions([cond1])
        results = session.execute(select(Product).where(combined)).scalars().all()

        assert len(results) == 3

    def test_combine_three_conditions_with_and(self, session: Session) -> None:
        """Test combining three conditions with AND logic."""
        cond1 = SqlFilterAdapter.build_condition(Product.category, "eq", "Electronics")
        cond2 = SqlFilterAdapter.build_condition(Product.price, "gte", 50)
        cond3 = SqlFilterAdapter.build_condition(Product.price, "lte", 100)

        combined = SqlFilterAdapter.combine_conditions([cond1, cond2, cond3], logic="and")
        results = session.execute(select(Product).where(combined)).scalars().all()

        assert len(results) == 1
        assert results[0].name == "Keyboard"

    def test_combine_empty_list_raises_error(self) -> None:
        """Test that combining empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot combine empty list of conditions"):
            SqlFilterAdapter.combine_conditions([])

    def test_combine_complex_and_or_conditions(self, session: Session) -> None:
        """Test complex combination of AND/OR conditions."""
        # (category = 'Electronics' AND price < 100) OR (category = 'Furniture')
        cond1 = SqlFilterAdapter.build_condition(Product.category, "eq", "Electronics")
        cond2 = SqlFilterAdapter.build_condition(Product.price, "lt", 100)
        electronics_cheap = SqlFilterAdapter.combine_conditions([cond1, cond2], logic="and")

        cond3 = SqlFilterAdapter.build_condition(Product.category, "eq", "Furniture")

        combined = SqlFilterAdapter.combine_conditions([electronics_cheap, cond3], logic="or")
        results = session.execute(select(Product).where(combined)).scalars().all()

        assert len(results) == 4  # 2 cheap electronics + 2 furniture

    def test_combine_with_in_operator(self, session: Session) -> None:
        """Test combining IN operator with other conditions."""
        cond1 = SqlFilterAdapter.build_condition(Product.id, "in", [1, 2, 3])
        cond2 = SqlFilterAdapter.build_condition(Product.price, "gte", 75)

        combined = SqlFilterAdapter.combine_conditions([cond1, cond2], logic="and")
        results = session.execute(select(Product).where(combined)).scalars().all()

        assert len(results) == 2  # Laptop and Keyboard
        assert {p.id for p in results} == {1, 3}

    def test_combine_default_logic_is_and(self, session: Session) -> None:
        """Test that default logic is AND when not specified."""
        cond1 = SqlFilterAdapter.build_condition(Product.category, "eq", "Electronics")
        cond2 = SqlFilterAdapter.build_condition(Product.price, "gt", 50)

        # Not specifying logic parameter - should default to 'and'
        combined = SqlFilterAdapter.combine_conditions([cond1, cond2])
        results = session.execute(select(Product).where(combined)).scalars().all()

        assert len(results) == 2
        assert all(p.category == "Electronics" and p.price > 50 for p in results)
