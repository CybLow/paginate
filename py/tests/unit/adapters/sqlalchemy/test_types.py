"""Tests for SQLAlchemy type aliases."""

from __future__ import annotations

from pypaginate.adapters.sqlalchemy import types


class TestTypeAliasesImportable:
    def test_module_exports_expected_names(self) -> None:
        assert "SelectStatement" in types.__all__
        assert "ColumnElement" in types.__all__

    def test_aliases_not_defined_at_runtime(self) -> None:
        assert not hasattr(types, "SelectStatement")
        assert not hasattr(types, "ColumnElement")
