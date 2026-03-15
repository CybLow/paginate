"""Tests for pypaginate public API exports."""

from __future__ import annotations

import pypaginate


class TestAllExports:
    def test_all_exports_importable(self) -> None:
        for name in pypaginate.__all__:
            assert hasattr(pypaginate, name), f"{name} in __all__ but not importable"


class TestVersion:
    def test_version_defined(self) -> None:
        assert isinstance(pypaginate.__version__, str)
        assert pypaginate.__version__ == "0.2.0"
