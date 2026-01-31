"""Tests for dependencies module."""

from __future__ import annotations


class TestDependenciesImport:
    """Test that dependencies module can be imported."""

    def test_get_pagination_params_exists(self) -> None:
        """get_pagination_params should be importable."""
        from pypaginate.dependencies import get_pagination_params

        assert callable(get_pagination_params)

    def test_paged_response_exists(self) -> None:
        """PagedResponse should be importable."""
        from pypaginate.dependencies import PagedResponse

        assert PagedResponse is not None
