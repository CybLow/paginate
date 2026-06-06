"""Property-based cursor-codec invariant: decode reverses encode.

For any list of scalars (int / str / bool / None), decoding an encoded cursor
must recover the original values. The codec returns a tuple, so the recovered
values are compared against ``tuple(values)``.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from pypaginate import _core


pytestmark = pytest.mark.property


_scalars = st.one_of(
    st.integers(min_value=-(10**12), max_value=10**12),
    st.text(max_size=24),
    st.booleans(),
    st.none(),
)
_value_lists = st.lists(_scalars, max_size=8)


@given(values=_value_lists)
def test_decode_reverses_encode(values: list[object]) -> None:
    # Act
    recovered = _core.decode_cursor(_core.encode_cursor(values))

    # Assert
    assert recovered == tuple(values)


@given(values=_value_lists)
def test_encode_is_a_string(values: list[object]) -> None:
    # Act
    encoded = _core.encode_cursor(values)

    # Assert
    assert isinstance(encoded, str)


@given(values=st.lists(st.text(max_size=24), min_size=1, max_size=6))
def test_string_only_cursor_roundtrips(values: list[str]) -> None:
    # Act
    recovered = _core.decode_cursor(_core.encode_cursor(values))

    # Assert
    assert list(recovered) == values
