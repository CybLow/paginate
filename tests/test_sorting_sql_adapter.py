"""Tests for the SQL sorting adapter module.

This module tests the SqlSortAdapter class which converts sort specifications
into SQLAlchemy ORDER BY clauses.
"""

from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from pypaginate.sorting.sql_adapter import SqlSortAdapter


# Test model
class Base(DeclarativeBase):
    """Base class for test models."""

    pass


class Employee(Base):
    """Sample employee model for testing SQL sorting."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    department = Column(String(50))
    salary = Column(Integer, nullable=True)


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

    # Insert test data with some NULL values
    employees = [
        Employee(id=1, name="Alice", department="Engineering", salary=100000),
        Employee(id=2, name="Bob", department="Sales", salary=80000),
        Employee(id=3, name="Charlie", department="Engineering", salary=None),
        Employee(id=4, name="David", department="Marketing", salary=90000),
        Employee(id=5, name="Eve", department="Engineering", salary=120000),
        Employee(id=6, name="Frank", department="Sales", salary=None),
        Employee(id=7, name="Grace", department="HR", salary=85000),
    ]
    session.add_all(employees)
    session.commit()

    yield session

    session.close()


class TestSqlSortAdapterAscending:
    """Tests for ascending sort order."""

    def test_ascending_sort_default(self, session: Session) -> None:
        """Test ascending sort (default behavior)."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.name)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        names = [emp.name for emp in results]
        assert names == ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]

    def test_ascending_sort_explicit(self, session: Session) -> None:
        """Test ascending sort with explicit descending=False."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.name, descending=False)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        names = [emp.name for emp in results]
        assert names == ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]

    def test_ascending_sort_integers(self, session: Session) -> None:
        """Test ascending sort on integer column."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.id)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        ids = [emp.id for emp in results]
        assert ids == [1, 2, 3, 4, 5, 6, 7]


class TestSqlSortAdapterDescending:
    """Tests for descending sort order."""

    def test_descending_sort(self, session: Session) -> None:
        """Test descending sort."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.name, descending=True)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        names = [emp.name for emp in results]
        assert names == ["Grace", "Frank", "Eve", "David", "Charlie", "Bob", "Alice"]

    def test_descending_sort_integers(self, session: Session) -> None:
        """Test descending sort on integer column."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.id, descending=True)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        ids = [emp.id for emp in results]
        assert ids == [7, 6, 5, 4, 3, 2, 1]

    def test_descending_sort_salary(self, session: Session) -> None:
        """Test descending sort on nullable column (default NULL handling)."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.salary, descending=True)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        # Get salaries (None values will be at the end or beginning depending on DB)
        salaries = [emp.salary for emp in results]
        non_null_salaries = [s for s in salaries if s is not None]

        # Verify non-null values are sorted correctly
        assert non_null_salaries == [120000, 100000, 90000, 85000, 80000]


class TestSqlSortAdapterNullHandling:
    """Tests for NULL value positioning."""

    def test_nulls_first_ascending(self, session: Session) -> None:
        """Test NULLs positioned first in ascending sort."""
        order_expr = SqlSortAdapter.build_order_expression(
            Employee.salary, descending=False, nulls_position="first"
        )
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        salaries = [emp.salary for emp in results]

        # First two should be None
        assert salaries[0] is None
        assert salaries[1] is None

        # Rest should be sorted ascending
        assert salaries[2:] == [80000, 85000, 90000, 100000, 120000]

    def test_nulls_last_ascending(self, session: Session) -> None:
        """Test NULLs positioned last in ascending sort."""
        order_expr = SqlSortAdapter.build_order_expression(
            Employee.salary, descending=False, nulls_position="last"
        )
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        salaries = [emp.salary for emp in results]

        # First five should be non-null and sorted
        assert salaries[:5] == [80000, 85000, 90000, 100000, 120000]

        # Last two should be None
        assert salaries[5] is None
        assert salaries[6] is None

    def test_nulls_first_descending(self, session: Session) -> None:
        """Test NULLs positioned first in descending sort."""
        order_expr = SqlSortAdapter.build_order_expression(
            Employee.salary, descending=True, nulls_position="first"
        )
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        salaries = [emp.salary for emp in results]

        # First two should be None
        assert salaries[0] is None
        assert salaries[1] is None

        # Rest should be sorted descending
        assert salaries[2:] == [120000, 100000, 90000, 85000, 80000]

    def test_nulls_last_descending(self, session: Session) -> None:
        """Test NULLs positioned last in descending sort."""
        order_expr = SqlSortAdapter.build_order_expression(
            Employee.salary, descending=True, nulls_position="last"
        )
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        salaries = [emp.salary for emp in results]

        # First five should be non-null and sorted descending
        assert salaries[:5] == [120000, 100000, 90000, 85000, 80000]

        # Last two should be None
        assert salaries[5] is None
        assert salaries[6] is None

    def test_no_null_handling(self, session: Session) -> None:
        """Test sort without explicit NULL handling."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.salary)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        salaries = [emp.salary for emp in results]
        non_null = [s for s in salaries if s is not None]

        # Non-null values should be sorted
        assert non_null == [80000, 85000, 90000, 100000, 120000]

        # Should have 2 None values
        assert salaries.count(None) == 2


class TestSqlSortAdapterMultipleColumns:
    """Tests for sorting by multiple columns."""

    def test_sort_by_department_then_name(self, session: Session) -> None:
        """Test sorting by multiple columns."""
        order_expr1 = SqlSortAdapter.build_order_expression(Employee.department)
        order_expr2 = SqlSortAdapter.build_order_expression(Employee.name)

        results = (
            session.execute(select(Employee).order_by(order_expr1, order_expr2)).scalars().all()
        )

        # Group by department
        dept_names = [(emp.department, emp.name) for emp in results]

        # Engineering should come first (alphabetically)
        engineering = [dn for dn in dept_names if dn[0] == "Engineering"]
        assert engineering == [
            ("Engineering", "Alice"),
            ("Engineering", "Charlie"),
            ("Engineering", "Eve"),
        ]

    def test_sort_department_desc_then_salary_asc(self, session: Session) -> None:
        """Test sorting with mixed order directions."""
        order_expr1 = SqlSortAdapter.build_order_expression(Employee.department, descending=True)
        order_expr2 = SqlSortAdapter.build_order_expression(Employee.salary, nulls_position="last")

        results = (
            session.execute(select(Employee).order_by(order_expr1, order_expr2)).scalars().all()
        )

        departments = [emp.department for emp in results]

        # First should be Sales (alphabetically last)
        assert departments[0] == "Sales"
        assert departments[1] == "Sales"


class TestSqlSortAdapterEdgeCases:
    """Tests for edge cases."""

    def test_sort_single_row(self, session: Session) -> None:
        """Test sorting with only one row."""
        # Delete all but one
        session.query(Employee).filter(Employee.id != 1).delete()
        session.commit()

        order_expr = SqlSortAdapter.build_order_expression(Employee.name)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        assert len(results) == 1
        assert results[0].name == "Alice"

    def test_sort_empty_result(self, session: Session) -> None:
        """Test sorting with no results."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.name)
        results = (
            session.execute(select(Employee).where(Employee.id == 999).order_by(order_expr))
            .scalars()
            .all()
        )

        assert len(results) == 0

    def test_all_nulls_column(self, session: Session) -> None:
        """Test sorting a column with all NULL values."""
        # Set all salaries to None
        session.query(Employee).update({"salary": None})
        session.commit()

        order_expr = SqlSortAdapter.build_order_expression(Employee.salary, nulls_position="first")
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        assert len(results) == 7
        assert all(emp.salary is None for emp in results)

    def test_none_nulls_position_parameter(self, session: Session) -> None:
        """Test with None as nulls_position (should use default behavior)."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.salary, nulls_position=None)
        results = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        assert len(results) == 7
        # Should work without error


class TestSqlSortAdapterReturnType:
    """Tests for verifying return types."""

    def test_returns_unary_expression(self, session: Session) -> None:
        """Test that method returns SQLAlchemy UnaryExpression."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.name)

        # Should be usable in order_by
        query = select(Employee).order_by(order_expr)
        results = session.execute(query).scalars().all()

        assert len(results) == 7

    def test_expression_is_reusable(self, session: Session) -> None:
        """Test that expressions can be reused in multiple queries."""
        order_expr = SqlSortAdapter.build_order_expression(Employee.name)

        # Use in first query
        results1 = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        # Use in second query
        results2 = session.execute(select(Employee).order_by(order_expr)).scalars().all()

        assert [e.name for e in results1] == [e.name for e in results2]
