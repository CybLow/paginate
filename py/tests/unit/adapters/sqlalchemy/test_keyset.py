"""Tests for keyset pagination WHERE clause builder.

Uses real SQLAlchemy Column objects (not mocks) to verify
correct SQL generation for single and multi-column cursors.
"""

from __future__ import annotations

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, select

from pypaginate.adapters.sqlalchemy.keyset import (
    OrderColumn,
    build_keyset_condition,
    extract_order_columns,
)
from pypaginate.domain.exceptions import ConfigurationError


@pytest.fixture()
def table() -> Table:
    """A simple three-column test table."""
    meta = MetaData()
    return Table(
        "t",
        meta,
        Column("id", Integer),
        Column("name", String),
        Column("age", Integer),
    )


def _compile(expr: object) -> str:
    """Compile an expression to SQL with literal binds."""
    return str(expr.compile(compile_kwargs={"literal_binds": True}))  # type: ignore[union-attr]


# -- extract_order_columns ---------------------------------------------------


class TestExtractSingleColumn:
    def test_asc_column(self, table: Table) -> None:
        query = select(table).order_by(table.c.id.asc())

        columns = extract_order_columns(query)

        assert len(columns) == 1
        assert columns[0].is_ascending is True

    def test_desc_column(self, table: Table) -> None:
        query = select(table).order_by(table.c.name.desc())

        columns = extract_order_columns(query)

        assert len(columns) == 1
        assert columns[0].is_ascending is False

    def test_bare_column_defaults_asc(self, table: Table) -> None:
        query = select(table).order_by(table.c.id)

        columns = extract_order_columns(query)

        assert len(columns) == 1
        assert columns[0].is_ascending is True


class TestExtractMultiColumn:
    def test_mixed_directions(self, table: Table) -> None:
        query = select(table).order_by(
            table.c.id.asc(),
            table.c.name.desc(),
        )

        columns = extract_order_columns(query)

        assert len(columns) == 2
        assert columns[0].is_ascending is True
        assert columns[1].is_ascending is False

    def test_three_columns(self, table: Table) -> None:
        query = select(table).order_by(
            table.c.name.asc(),
            table.c.age.desc(),
            table.c.id.asc(),
        )

        columns = extract_order_columns(query)

        assert len(columns) == 3


class TestExtractErrors:
    def test_no_order_by_raises(self, table: Table) -> None:
        query = select(table)

        with pytest.raises(ConfigurationError, match="no ORDER BY"):
            extract_order_columns(query)


# -- build_keyset_condition --------------------------------------------------


class TestBuildSingleColumn:
    def test_asc_produces_greater_than(self, table: Table) -> None:
        col = OrderColumn(table.c.id, is_ascending=True)

        condition = build_keyset_condition([col], (5,))
        sql = _compile(condition)

        assert "t.id > 5" in sql

    def test_desc_produces_less_than(self, table: Table) -> None:
        col = OrderColumn(table.c.id, is_ascending=False)

        condition = build_keyset_condition([col], (10,))
        sql = _compile(condition)

        assert "t.id < 10" in sql


class TestBuildMultiColumn:
    def test_two_column_asc_desc(self, table: Table) -> None:
        cols = [
            OrderColumn(table.c.id, is_ascending=True),
            OrderColumn(table.c.name, is_ascending=False),
        ]

        condition = build_keyset_condition(cols, (5, "alice"))
        sql = _compile(condition)

        assert "t.id > 5" in sql
        assert "t.id = 5" in sql
        assert "t.name < 'alice'" in sql

    def test_three_column_produces_nested_or(self, table: Table) -> None:
        cols = [
            OrderColumn(table.c.id, is_ascending=True),
            OrderColumn(table.c.name, is_ascending=True),
            OrderColumn(table.c.age, is_ascending=False),
        ]

        condition = build_keyset_condition(cols, (1, "bob", 30))
        sql = _compile(condition)

        assert "t.id > 1" in sql
        assert "t.name > 'bob'" in sql
        assert "t.age < 30" in sql


class TestBuildErrors:
    def test_empty_columns_raises(self) -> None:
        with pytest.raises(ConfigurationError, match="No ORDER BY"):
            build_keyset_condition([], ())

    def test_mismatched_count_raises(self, table: Table) -> None:
        col = OrderColumn(table.c.id, is_ascending=True)

        with pytest.raises(ConfigurationError, match="does not match"):
            build_keyset_condition([col], (1, 2))


# -- OrderColumn.reversed ---------------------------------------------------


class TestOrderColumnReversed:
    def test_reversed_flips_direction(self, table: Table) -> None:
        col = OrderColumn(table.c.id, is_ascending=True)

        flipped = col.reversed

        assert flipped.is_ascending is False
        assert flipped.element is col.element

    def test_double_reverse_restores(self, table: Table) -> None:
        col = OrderColumn(table.c.id, is_ascending=False)

        assert col.reversed.reversed.is_ascending is False


# -- Integration: extract + build --------------------------------------------


class TestEndToEnd:
    def test_extract_then_build(self, table: Table) -> None:
        query = select(table).order_by(
            table.c.id.asc(),
            table.c.name.desc(),
        )

        columns = extract_order_columns(query)
        condition = build_keyset_condition(columns, (7, "zoe"))
        sql = _compile(condition)

        assert "t.id > 7" in sql
        assert "t.id = 7" in sql
        assert "t.name < 'zoe'" in sql
