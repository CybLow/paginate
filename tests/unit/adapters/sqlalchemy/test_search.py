"""Tests for SQLAlchemySearchBackend.

Mock tests verify pattern building and delegation.
Real DB tests verify ILIKE search against async SQLite.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import Executable, select
from sqlalchemy.ext.asyncio import AsyncSession

from pypaginate.adapters.sqlalchemy.search import SQLAlchemySearchBackend
from pypaginate.domain.enums import SearchFieldMode
from pypaginate.domain.specs import SearchSpec
from tests.fixtures.models import User


@pytest.fixture()
def search_backend() -> SQLAlchemySearchBackend:
    """Search backend instance."""
    return SQLAlchemySearchBackend()


# -- Mock tests: patterns via apply_search -----------------------------------


class TestBuildPatternViaApplySearch:
    @pytest.mark.parametrize(
        "mode",
        [SearchFieldMode.CONTAINS, SearchFieldMode.PREFIX, SearchFieldMode.EXACT],
        ids=["contains", "prefix", "exact"],
    )
    @patch("pypaginate.adapters.sqlalchemy.search._apply_token_conditions")
    def test_mode_passed_through_to_token_conditions(
        self,
        mock_apply: MagicMock,
        mode: SearchFieldMode,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        mock_apply.return_value = MagicMock()
        spec = SearchSpec(query="hello", fields=("name",), mode=mode)

        search_backend.apply_search(MagicMock(), spec)

        mock_apply.assert_called_once()
        call_args = mock_apply.call_args[0]
        assert call_args[1] == ["hello"]
        assert call_args[2].mode is mode


class TestFieldMatchViaApplySearch:
    @patch("pypaginate.adapters.sqlalchemy.search._apply_token_conditions")
    def test_non_empty_query_invokes_token_conditions(
        self,
        mock_apply: MagicMock,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        mock_apply.return_value = MagicMock()
        spec = SearchSpec(query="test", fields=("name",), mode=SearchFieldMode.CONTAINS)

        search_backend.apply_search(MagicMock(), spec)

        mock_apply.assert_called_once()
        tokens = mock_apply.call_args[0][1]
        assert tokens == ["test"]

    @patch("pypaginate.adapters.sqlalchemy.search._apply_token_conditions")
    def test_prefix_mode_passes_through(
        self,
        mock_apply: MagicMock,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        mock_apply.return_value = MagicMock()
        spec = SearchSpec(query="pre", fields=("name",), mode=SearchFieldMode.PREFIX)

        search_backend.apply_search(MagicMock(), spec)

        passed_spec = mock_apply.call_args[0][2]
        assert passed_spec.mode is SearchFieldMode.PREFIX

    @patch("pypaginate.adapters.sqlalchemy.search._apply_token_conditions")
    def test_exact_mode_passes_through(
        self,
        mock_apply: MagicMock,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        mock_apply.return_value = MagicMock()
        spec = SearchSpec(query="val", fields=("name",), mode=SearchFieldMode.EXACT)

        search_backend.apply_search(MagicMock(), spec)

        passed_spec = mock_apply.call_args[0][2]
        assert passed_spec.mode is SearchFieldMode.EXACT


class TestSearchBackendDelegation:
    def test_empty_query_returns_unchanged(
        self,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        query = MagicMock()
        spec = SearchSpec(query="", fields=("name",))

        result = search_backend.apply_search(query, spec)

        assert result is query

    def test_whitespace_query_returns_unchanged(
        self,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        query = MagicMock()
        spec = SearchSpec(query="   ", fields=("name",))

        result = search_backend.apply_search(query, spec)

        assert result is query

    @patch("pypaginate.adapters.sqlalchemy.search._apply_token_conditions")
    def test_non_empty_query_delegates(
        self,
        mock_apply: MagicMock,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        mock_apply.return_value = MagicMock()
        spec = SearchSpec(query="hello", fields=("name",))

        search_backend.apply_search(MagicMock(), spec)

        mock_apply.assert_called_once()

    @patch("pypaginate.adapters.sqlalchemy.search._apply_token_conditions")
    def test_multi_word_query_passes_tokens(
        self,
        mock_apply: MagicMock,
        search_backend: SQLAlchemySearchBackend,
    ) -> None:
        mock_apply.return_value = MagicMock()
        spec = SearchSpec(query="hello world", fields=("name",))

        search_backend.apply_search(MagicMock(), spec)

        tokens = mock_apply.call_args[0][1]
        assert tokens == ["hello", "world"]


# -- Real DB tests -----------------------------------------------------------


async def _fetch_searched(
    session: AsyncSession,
    spec: SearchSpec,
) -> list[User]:
    """Apply search and execute, returning User results."""
    backend = SQLAlchemySearchBackend()
    stmt: Executable = backend.apply_search(select(User), spec)  # type: ignore[assignment]
    result = await session.execute(stmt)
    return list(result.scalars().all())


class TestSearchContainsRealDB:
    @pytest.mark.asyncio()
    async def test_search_contains_alice(self, seeded_session: AsyncSession) -> None:
        spec = SearchSpec(query="ali", fields=("name",))

        rows = await _fetch_searched(seeded_session, spec)

        assert len(rows) == 1
        assert rows[0].name == "Alice"


class TestSearchPrefixRealDB:
    @pytest.mark.asyncio()
    async def test_search_prefix_bo(self, seeded_session: AsyncSession) -> None:
        spec = SearchSpec(query="Bo", fields=("name",), mode=SearchFieldMode.PREFIX)

        rows = await _fetch_searched(seeded_session, spec)

        assert len(rows) == 1
        assert rows[0].name == "Bob"


class TestSearchMultipleFieldsRealDB:
    @pytest.mark.asyncio()
    async def test_search_in_name_and_email(self, seeded_session: AsyncSession) -> None:
        spec = SearchSpec(query="alice", fields=("name", "email"))

        rows = await _fetch_searched(seeded_session, spec)

        assert len(rows) == 1
        assert rows[0].email == "alice@example.com"


class TestSearchNoMatchRealDB:
    @pytest.mark.asyncio()
    async def test_search_no_match(self, seeded_session: AsyncSession) -> None:
        spec = SearchSpec(query="zzz", fields=("name",))

        rows = await _fetch_searched(seeded_session, spec)

        assert rows == []
