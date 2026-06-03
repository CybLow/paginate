"""Tests for SearchDep."""

from __future__ import annotations

from pypaginate.adapters.fastapi.search import SearchDep


class TestSearchDep:
    def test_valid_query_returns_spec(self) -> None:
        dep = SearchDep(q="alice", search_fields="name")
        spec = dep.to_spec()

        assert spec is not None
        assert spec.query == "alice"

    def test_none_query_returns_none(self) -> None:
        dep = SearchDep(q=None)

        assert dep.to_spec() is None

    def test_comma_separated_fields(self) -> None:
        dep = SearchDep(q="test", search_fields="name,email")
        spec = dep.to_spec()

        assert spec is not None
        assert spec.fields == ("name", "email")

    def test_empty_fields_returns_none(self) -> None:
        dep = SearchDep(q="alice")

        assert dep.to_spec() is None

    def test_explicit_field(self) -> None:
        dep = SearchDep(q="alice", search_fields="email")
        spec = dep.to_spec()

        assert spec is not None
        assert spec.fields == ("email",)
