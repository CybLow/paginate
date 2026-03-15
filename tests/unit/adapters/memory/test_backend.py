"""Tests for MemoryBackend."""

from __future__ import annotations

import pytest

from pypaginate.adapters.memory.backend import MemoryBackend


@pytest.fixture()
def backend() -> MemoryBackend:
    """Shared MemoryBackend instance."""
    return MemoryBackend()


class TestMemoryBackendCount:
    def test_count_list_returns_length(
        self,
        backend: MemoryBackend,
    ) -> None:
        result = backend.count([1, 2, 3])

        assert result == 3

    def test_count_empty_list_returns_zero(
        self,
        backend: MemoryBackend,
    ) -> None:
        result = backend.count([])

        assert result == 0

    def test_count_tuple_returns_length(
        self,
        backend: MemoryBackend,
    ) -> None:
        result = backend.count((1, 2, 3, 4))

        assert result == 4


class TestMemoryBackendFetch:
    def test_fetch_middle_slice(self, backend: MemoryBackend) -> None:
        data = [10, 20, 30, 40, 50]

        result = backend.fetch(data, offset=1, limit=2)

        assert result == [20, 30]

    def test_fetch_from_start(self, backend: MemoryBackend) -> None:
        data = [1, 2, 3, 4, 5]

        result = backend.fetch(data, offset=0, limit=3)

        assert result == [1, 2, 3]

    def test_fetch_beyond_length_returns_empty(
        self,
        backend: MemoryBackend,
    ) -> None:
        result = backend.fetch([1, 2, 3], offset=10, limit=5)

        assert result == []

    def test_fetch_empty_list_returns_empty(
        self,
        backend: MemoryBackend,
    ) -> None:
        result = backend.fetch([], offset=0, limit=5)

        assert result == []


class TestMemoryBackendValidation:
    @pytest.mark.parametrize(
        ("invalid_input", "type_name"),
        [
            (42, "int"),
            ("hello", "str"),
            (b"bytes", "bytes"),
            ({"key": "value"}, "dict"),
        ],
        ids=["int", "str", "bytes", "dict"],
    )
    def test_non_sequence_raises_type_error(
        self,
        backend: MemoryBackend,
        invalid_input: object,
        type_name: str,
    ) -> None:
        with pytest.raises(TypeError, match=f"got {type_name}"):
            backend.count(invalid_input)
