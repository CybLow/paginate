"""Tests for SQLAlchemy column resolution."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from pypaginate.adapters.sqlalchemy.columns import resolve_column
from pypaginate.domain.exceptions import ConfigurationError


def _make_query_with_entity(entity: type) -> MagicMock:
    """Create mock Select with column_descriptions."""
    query = MagicMock()
    query.column_descriptions = [{"entity": entity}]
    return query


class TestResolveColumn:
    def test_resolves_existing_attribute(self) -> None:
        entity = MagicMock()
        entity.name = MagicMock()
        query = _make_query_with_entity(entity)

        result = resolve_column(query, "name")

        assert result is entity.name

    def test_missing_field_raises_configuration_error(self) -> None:
        entity = type("User", (), {})
        query = _make_query_with_entity(entity)

        with pytest.raises(ConfigurationError, match="not found on"):
            resolve_column(query, "nonexistent")

    def test_no_entity_raises_configuration_error(self) -> None:
        query = MagicMock()
        query.column_descriptions = [{"entity": None}]

        with pytest.raises(ConfigurationError, match="No ORM entity"):
            resolve_column(query, "name")

    def test_empty_descriptions_raises_configuration_error(
        self,
    ) -> None:
        query = MagicMock()
        query.column_descriptions = []

        with pytest.raises(ConfigurationError, match="No ORM entity"):
            resolve_column(query, "name")
