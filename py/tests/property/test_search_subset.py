"""Property-based search invariant: results are a subset of the input.

Search ranks by relevance (so order is not preserved), but it may never invent
rows: every returned item must come from the input, with no duplicates. Each row
carries a unique positional ``id`` so membership and uniqueness are checkable
regardless of ranking.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from pypaginate import SearchSpec, search as search_items


pytestmark = pytest.mark.property


_words = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=8,
)


@st.composite
def _rows(draw: st.DrawFn) -> list[dict[str, object]]:
    """Rows with a unique positional ``id`` and a short lowercase ``name``."""
    names = draw(st.lists(_words, max_size=50))
    return [{"id": i, "name": name} for i, name in enumerate(names)]


@given(rows=_rows(), query=_words, mode=st.sampled_from(("contains", "prefix", "exact")))
def test_results_are_unique_input_rows(
    rows: list[dict[str, object]], query: str, mode: str
) -> None:
    # Act
    result = search_items(rows, SearchSpec(fields=["name"], query=query, mode=mode))

    # Assert
    ids = [row["id"] for row in result]
    assert len(ids) == len(set(ids))
    assert all(row is rows[row["id"]] for row in result)  # type: ignore[index]


@given(rows=_rows(), query=_words, cap=st.integers(min_value=0, max_value=10))
def test_max_results_caps_the_count(rows: list[dict[str, object]], query: str, cap: int) -> None:
    # Act
    result = search_items(
        rows, SearchSpec(fields=["name"], query=query, mode="contains", max_results=cap)
    )

    # Assert
    assert len(result) <= cap


@given(rows=_rows())
def test_empty_query_returns_every_row(rows: list[dict[str, object]]) -> None:
    # Act
    result = search_items(rows, SearchSpec(fields=["name"], query=""))

    # Assert
    assert {row["id"] for row in result} == set(range(len(rows)))
