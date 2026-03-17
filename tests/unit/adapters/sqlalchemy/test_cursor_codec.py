"""Tests for cursor codec — encode/decode without sqlakeyset."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from pypaginate.domain.exceptions import ValidationError
from pypaginate.engine.cursor_codec import (
    decode_cursor,
    encode_cursor,
)


# -- Round-trip tests --------------------------------------------------------


class TestRoundTrip:
    """Encode then decode should return original values."""

    def test_int(self) -> None:
        values = (42,)
        assert decode_cursor(encode_cursor(values)) == values

    def test_float(self) -> None:
        values = (3.14,)
        assert decode_cursor(encode_cursor(values)) == values

    def test_str(self) -> None:
        values = ("hello world",)
        assert decode_cursor(encode_cursor(values)) == values

    def test_none(self) -> None:
        values = (None,)
        assert decode_cursor(encode_cursor(values)) == values

    def test_bool(self) -> None:
        values = (True, False)
        assert decode_cursor(encode_cursor(values)) == values

    def test_datetime(self) -> None:
        dt = datetime(2025, 6, 15, 12, 30, 45, tzinfo=UTC)
        values = (dt,)
        assert decode_cursor(encode_cursor(values)) == values

    def test_date(self) -> None:
        d = date(2025, 6, 15)
        values = (d,)
        assert decode_cursor(encode_cursor(values)) == values

    def test_decimal(self) -> None:
        values = (Decimal("99.95"),)
        assert decode_cursor(encode_cursor(values)) == values

    def test_uuid(self) -> None:
        uid = UUID("12345678-1234-5678-1234-567812345678")
        values = (uid,)
        assert decode_cursor(encode_cursor(values)) == values


# -- Tuple shape tests -------------------------------------------------------


class TestTupleShape:
    """Multiple values and empty tuples."""

    def test_multiple_values(self) -> None:
        values = (42, "alice", datetime(2025, 1, 1, tzinfo=UTC), None)
        assert decode_cursor(encode_cursor(values)) == values

    def test_empty_tuple(self) -> None:
        values: tuple[(), ...] = ()
        assert decode_cursor(encode_cursor(values)) == values


# -- Tamper resistance -------------------------------------------------------


class TestInvalidCursor:
    """Invalid or tampered cursors raise ValidationError."""

    def test_garbage_string(self) -> None:
        with pytest.raises(ValidationError, match="Invalid cursor"):
            decode_cursor("not-a-valid-cursor!!!")

    def test_empty_string(self) -> None:
        with pytest.raises(ValidationError, match="Invalid cursor"):
            decode_cursor("")

    def test_non_list_payload(self) -> None:
        """A valid base64 string that decodes to a dict, not a list."""
        import base64
        import json

        payload = json.dumps({"key": "value"})
        cursor = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
        with pytest.raises(ValidationError, match="Invalid cursor"):
            decode_cursor(cursor)

    def test_unknown_type_tag(self) -> None:
        """A list with an unknown __type__ tag."""
        import base64
        import json

        payload = json.dumps([{"__type__": "unknown", "v": "x"}])
        cursor = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
        with pytest.raises(ValidationError, match="Invalid cursor"):
            decode_cursor(cursor)

    def test_bad_datetime_value(self) -> None:
        """A datetime tag with a non-ISO value."""
        import base64
        import json

        payload = json.dumps([{"__type__": "datetime", "v": "nope"}])
        cursor = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
        with pytest.raises(ValidationError, match="Invalid cursor"):
            decode_cursor(cursor)
