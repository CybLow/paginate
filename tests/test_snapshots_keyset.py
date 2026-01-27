"""Tests for keyset pagination snapshot helpers.

Unit tests for bookmark coercion, materialization, and marker extraction.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pypaginator.core.snapshots import (
    KeysetPaginationSnapshot,
    PaginationSnapshot,
    _coerce_scalar_row,
    _ensure_sequence,
    _is_sequence,
    coerce_bookmark,
    extract_keyset_markers,
    markers_from_paging,
    materialize_keyset_page,
)
from pypaginator.core.pages import KeysetPageParams, PageParams
from pypaginator.exceptions import PaginationConfigurationError


pytestmark = pytest.mark.unit


class TestPaginationSnapshot:
    """Test PaginationSnapshot dataclass."""

    def test_creation(self) -> None:
        """Should create snapshot."""
        params = PageParams(page=1, limit=10)
        snapshot: PaginationSnapshot[str, PageParams] = PaginationSnapshot(
            items=["a", "b", "c"],
            total=100,
            params=params,
        )

        assert snapshot.items == ["a", "b", "c"]
        assert snapshot.total == 100
        assert snapshot.params == params

    def test_frozen(self) -> None:
        """Snapshot should be frozen."""
        params = PageParams(page=1, limit=10)
        snapshot: PaginationSnapshot[str, PageParams] = PaginationSnapshot(
            items=["a"],
            total=1,
            params=params,
        )

        with pytest.raises(Exception):
            snapshot.total = 50  # type: ignore[misc]


class TestKeysetPaginationSnapshot:
    """Test KeysetPaginationSnapshot dataclass."""

    def test_creation(self) -> None:
        """Should create keyset snapshot."""
        params = KeysetPageParams(limit=10)
        snapshot: KeysetPaginationSnapshot[str] = KeysetPaginationSnapshot(
            items=["a", "b", "c"],
            params=params,
            next="next_bookmark",
            previous="prev_bookmark",
            current="curr_bookmark",
        )

        assert snapshot.items == ["a", "b", "c"]
        assert snapshot.params == params
        assert snapshot.next == "next_bookmark"
        assert snapshot.previous == "prev_bookmark"
        assert snapshot.current == "curr_bookmark"

    def test_none_bookmarks(self) -> None:
        """Should allow None bookmarks."""
        params = KeysetPageParams(limit=10)
        snapshot: KeysetPaginationSnapshot[str] = KeysetPaginationSnapshot(
            items=[],
            params=params,
            next=None,
            previous=None,
            current=None,
        )

        assert snapshot.next is None
        assert snapshot.previous is None
        assert snapshot.current is None


class TestExtractKeysetMarkers:
    """Test extract_keyset_markers function."""

    def test_extract_all_markers(self) -> None:
        """Should extract all markers from snapshot."""
        params = KeysetPageParams(limit=10)
        snapshot: KeysetPaginationSnapshot[str] = KeysetPaginationSnapshot(
            items=["a"],
            params=params,
            next="next",
            previous="prev",
            current="curr",
        )

        markers = extract_keyset_markers(snapshot)

        assert markers == ("next", "prev", "curr")

    def test_extract_none_markers(self) -> None:
        """Should extract None markers."""
        params = KeysetPageParams(limit=10)
        snapshot: KeysetPaginationSnapshot[str] = KeysetPaginationSnapshot(
            items=[],
            params=params,
            next=None,
            previous=None,
            current=None,
        )

        markers = extract_keyset_markers(snapshot)

        assert markers == (None, None, None)


class TestMarkersFromPaging:
    """Test markers_from_paging function."""

    def test_with_all_markers(self) -> None:
        """Should extract markers when all present."""
        paging = MagicMock()
        paging.has_next = True
        paging.has_previous = True
        paging.bookmark_next = "next_bm"
        paging.bookmark_previous = "prev_bm"
        paging.bookmark_current = "curr_bm"

        markers = markers_from_paging(paging)

        assert markers == ("next_bm", "prev_bm", "curr_bm")

    def test_without_next(self) -> None:
        """Should return None for next when has_next=False."""
        paging = MagicMock()
        paging.has_next = False
        paging.has_previous = True
        paging.bookmark_previous = "prev_bm"
        paging.bookmark_current = "curr_bm"

        markers = markers_from_paging(paging)

        assert markers[0] is None
        assert markers[1] == "prev_bm"
        assert markers[2] == "curr_bm"

    def test_without_previous(self) -> None:
        """Should return None for previous when has_previous=False."""
        paging = MagicMock()
        paging.has_next = True
        paging.has_previous = False
        paging.bookmark_next = "next_bm"
        paging.bookmark_current = "curr_bm"

        markers = markers_from_paging(paging)

        assert markers[0] == "next_bm"
        assert markers[1] is None
        assert markers[2] == "curr_bm"


class TestCoerceBookmark:
    """Test coerce_bookmark function."""

    def test_none_input(self) -> None:
        """Should return None for None input."""
        result = coerce_bookmark(None)
        assert result is None

    def test_valid_bookmark(self) -> None:
        """Should deserialize valid bookmark."""
        # Create a mock for sqlakeyset
        mock_marker = MagicMock()
        mock_marker.place = (1, "value")

        with patch(
            "pypaginator.core.snapshots._get_sqlakeyset"
        ) as mock_get_sqlakeyset:
            mock_sqlakeyset = MagicMock()
            mock_sqlakeyset.unserialize_bookmark.return_value = mock_marker
            mock_get_sqlakeyset.return_value = mock_sqlakeyset

            result = coerce_bookmark("valid_bookmark")

            assert result == (1, "value")
            mock_sqlakeyset.unserialize_bookmark.assert_called_once_with(
                "valid_bookmark"
            )

    def test_invalid_bookmark_raises(self) -> None:
        """Should raise for invalid bookmark payload."""
        mock_marker = MagicMock()
        mock_marker.place = "not_a_tuple"  # Invalid - should be tuple

        with patch(
            "pypaginator.core.snapshots._get_sqlakeyset"
        ) as mock_get_sqlakeyset:
            mock_sqlakeyset = MagicMock()
            mock_sqlakeyset.unserialize_bookmark.return_value = mock_marker
            mock_get_sqlakeyset.return_value = mock_sqlakeyset

            with pytest.raises(PaginationConfigurationError) as exc_info:
                coerce_bookmark("invalid_bookmark")

            assert "Invalid sqlakeyset bookmark" in str(exc_info.value)


class TestMaterializeKeysetPage:
    """Test materialize_keyset_page function."""

    def test_scalars_false(self) -> None:
        """Should return rows as-is when scalars=False."""
        items = [(1, "a"), (2, "b"), (3, "c")]
        mock_page = MagicMock()
        mock_page.__iter__ = lambda self: iter(items)

        result = materialize_keyset_page(mock_page, scalars=False)

        assert result == items

    def test_scalars_true_single_column(self) -> None:
        """Should coerce single-column rows to scalars."""
        items = [(1,), (2,), (3,)]

        mock_page = MagicMock()
        mock_page.__iter__ = lambda self: iter(items)

        result = materialize_keyset_page(mock_page, scalars=True)

        assert result == [1, 2, 3]

    def test_scalars_true_multi_column(self) -> None:
        """Should return tuples for multi-column rows."""
        items = [(1, "a"), (2, "b"), (3, "c")]

        mock_page = MagicMock()
        mock_page.__iter__ = lambda self: iter(items)

        result = materialize_keyset_page(mock_page, scalars=True)

        assert result == [(1, "a"), (2, "b"), (3, "c")]


class TestCoerceScalarRow:
    """Test _coerce_scalar_row function."""

    def test_single_value_tuple(self) -> None:
        """Should extract single value from tuple."""
        result = _coerce_scalar_row((42,))
        assert result == 42

    def test_single_value_list(self) -> None:
        """Should extract single value from list."""
        result = _coerce_scalar_row([42])
        assert result == 42

    def test_multi_value_tuple(self) -> None:
        """Should return tuple for multiple values."""
        result = _coerce_scalar_row((1, 2, 3))
        assert result == (1, 2, 3)

    def test_multi_value_list(self) -> None:
        """Should return tuple for multiple values from list."""
        result = _coerce_scalar_row([1, 2, 3])
        assert result == (1, 2, 3)


class TestEnsureSequence:
    """Test _ensure_sequence function."""

    def test_valid_tuple(self) -> None:
        """Should return tuple as-is."""
        result = _ensure_sequence((1, 2, 3))
        assert result == (1, 2, 3)

    def test_valid_list(self) -> None:
        """Should return list as-is."""
        result = _ensure_sequence([1, 2, 3])
        assert result == [1, 2, 3]

    def test_string_is_sequence(self) -> None:
        """String is technically a sequence."""
        result = _ensure_sequence("abc")
        assert result == "abc"

    def test_invalid_raises(self) -> None:
        """Should raise for non-sequence."""
        with pytest.raises(PaginationConfigurationError) as exc_info:
            _ensure_sequence(42)  # type: ignore[arg-type]

        assert "Invalid sqlakeyset row" in str(exc_info.value)


class TestIsSequence:
    """Test _is_sequence TypeGuard function."""

    def test_tuple_is_sequence(self) -> None:
        """Tuple should be recognized as sequence."""
        assert _is_sequence((1, 2, 3)) is True

    def test_list_is_sequence(self) -> None:
        """List should be recognized as sequence."""
        assert _is_sequence([1, 2, 3]) is True

    def test_string_is_sequence(self) -> None:
        """String should be recognized as sequence."""
        assert _is_sequence("abc") is True

    def test_int_not_sequence(self) -> None:
        """Int should not be recognized as sequence."""
        assert _is_sequence(42) is False

    def test_dict_not_sequence(self) -> None:
        """Dict should not be recognized as sequence."""
        assert _is_sequence({"a": 1}) is False
