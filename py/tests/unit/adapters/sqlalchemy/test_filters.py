"""Tests for SQLAlchemyFilterBackend -- mock-based operator/delegation tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from pypaginate.adapters.sqlalchemy.filters import SQLAlchemyFilterBackend
from pypaginate.domain.enums import FilterLogic
from pypaginate.domain.exceptions import FilterError
from pypaginate.domain.specs import FilterSpec


class _FakeColumn:
    """Mock column supporting comparison operators for filter tests."""

    __hash__ = object.__hash__

    def __eq__(self, _other: object) -> MagicMock:  # type: ignore[override]
        return MagicMock()

    def __ne__(self, _other: object) -> MagicMock:  # type: ignore[override]
        return MagicMock()

    def __gt__(self, _other: object) -> MagicMock:
        return MagicMock()

    def __ge__(self, _other: object) -> MagicMock:
        return MagicMock()

    def __lt__(self, _other: object) -> MagicMock:
        return MagicMock()

    def __le__(self, _other: object) -> MagicMock:
        return MagicMock()

    def __getattr__(self, _name: str) -> MagicMock:
        return MagicMock()


def _sa_column_mock() -> _FakeColumn:
    """Create a mock that supports SQLAlchemy-like comparison operators."""
    return _FakeColumn()


# -- Tests: operator coverage via apply_filters --------------------------------

_EXPECTED_OPS = {
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "not_in",
    "contains",
    "starts_with",
    "ends_with",
    "like",
    "ilike",
    "between",
    "is_null",
    "is_not_null",
    "regex",
}


class TestOperatorMapCoverage:
    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_all_operators_accepted(
        self,
        mock_resolve: MagicMock,
        mock_apply: MagicMock,
    ) -> None:
        col = _sa_column_mock()
        mock_resolve.return_value = col
        mock_apply.return_value = MagicMock()
        backend = SQLAlchemyFilterBackend()
        for op in _EXPECTED_OPS:
            spec = FilterSpec(field="x", operator=op, value=[1, 2] if op == "between" else 1)
            backend.apply_filters(MagicMock(), [spec])

    def test_operator_count_is_17(self) -> None:
        assert len(_EXPECTED_OPS) == 17


class TestSpecialOperators:
    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_between_calls_column_between(
        self,
        mock_resolve: MagicMock,
        _mock_apply: MagicMock,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = FilterSpec(field="x", operator="between", value=[10, 20])

        SQLAlchemyFilterBackend().apply_filters(MagicMock(), [spec])

        col.between.assert_called_once_with(10, 20)

    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_between_with_non_indexable_raises(
        self,
        mock_resolve: MagicMock,
        _mock_apply: MagicMock,
    ) -> None:
        """BETWEEN with a non-sequence value raises FilterError."""
        mock_resolve.return_value = MagicMock()
        spec = FilterSpec(field="x", operator="between", value=42)

        with pytest.raises(FilterError, match="two-element sequence"):
            SQLAlchemyFilterBackend().apply_filters(MagicMock(), [spec])

    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_is_null_calls_is_none(
        self,
        mock_resolve: MagicMock,
        _mock_apply: MagicMock,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = FilterSpec(field="x", operator="is_null")

        SQLAlchemyFilterBackend().apply_filters(MagicMock(), [spec])

        col.is_.assert_called_once_with(None)

    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_is_not_null_calls_is_not_none(
        self,
        mock_resolve: MagicMock,
        _mock_apply: MagicMock,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = FilterSpec(field="x", operator="is_not_null")

        SQLAlchemyFilterBackend().apply_filters(MagicMock(), [spec])

        col.is_not.assert_called_once_with(None)


_METHOD_PARAMS = [
    ("in", [1, 2], "in_"),
    ("not_in", [3], "not_in"),
    ("contains", "abc", "contains"),
    ("starts_with", "pre", "startswith"),
    ("ends_with", "suf", "endswith"),
    ("like", "%x%", "like"),
    ("ilike", "%x%", "ilike"),
    ("regex", "^a", "regexp_match"),
]


class TestMethodOperators:
    @pytest.mark.parametrize(
        ("operator", "value", "method"),
        _METHOD_PARAMS,
        ids=[p[0] for p in _METHOD_PARAMS],
    )
    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_method_operators_call_column_method(
        self,
        mock_resolve: MagicMock,
        _mock_apply: MagicMock,
        operator: str,
        value: object,
        method: str,
    ) -> None:
        col = MagicMock()
        mock_resolve.return_value = col
        spec = FilterSpec(field="x", operator=operator, value=value)

        SQLAlchemyFilterBackend().apply_filters(MagicMock(), [spec])

        getattr(col, method).assert_called_once_with(value)

    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_unsupported_operator_raises(
        self,
        mock_resolve: MagicMock,
        _mock_apply: MagicMock,
    ) -> None:
        mock_resolve.return_value = MagicMock()
        spec = MagicMock(field="x", operator="bad_op", logic=FilterLogic.AND)

        with pytest.raises(FilterError, match="Unsupported"):
            SQLAlchemyFilterBackend().apply_filters(MagicMock(), [spec])


class TestFilterBackendDelegation:
    @patch("pypaginate.adapters.sqlalchemy.filters.resolve_column")
    def test_no_filters_returns_unchanged_query(self, _mock: MagicMock) -> None:
        query = MagicMock()
        result = SQLAlchemyFilterBackend().apply_filters(query, [])
        assert result is query

    @patch("pypaginate.adapters.sqlalchemy.filters._apply_conditions")
    @patch("pypaginate.adapters.sqlalchemy.filters._partition_filters")
    def test_delegates_to_partition_and_apply(
        self,
        mock_part: MagicMock,
        mock_apply: MagicMock,
    ) -> None:
        mock_part.return_value = (["and_cond"], ["or_cond"])
        mock_apply.return_value = MagicMock()
        specs = [FilterSpec(field="a", operator="eq", value=1)]

        SQLAlchemyFilterBackend().apply_filters(MagicMock(), specs)

        mock_part.assert_called_once()
        mock_apply.assert_called_once()
