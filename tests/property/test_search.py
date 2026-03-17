"""Property-based search invariants.

Verifies algebraic properties of the search engine:
search never adds, empty query returns all, max_results caps,
min_length short query returns all.
"""

from __future__ import annotations

from hypothesis import given, settings, strategies as st

from pypaginate.domain.specs import SearchSpec
from pypaginate.search.engine import SearchEngine


_engine = SearchEngine()

_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "Nd", "Zs")),
    min_size=1,
    max_size=30,
)


@st.composite
def name_datasets(
    draw: st.DrawFn,
    min_size: int = 0,
    max_size: int = 100,
) -> list[dict[str, str]]:
    """Generate datasets of dicts with string 'name' fields."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    names = draw(st.lists(_name_strategy, min_size=size, max_size=size))
    return [{"name": n} for n in names]


@st.composite
def search_queries(draw: st.DrawFn) -> str:
    """Generate non-empty search query strings."""
    return draw(
        st.text(
            alphabet=st.characters(whitelist_categories=("L", "Nd")),
            min_size=1,
            max_size=20,
        ),
    )


@given(data=name_datasets(min_size=0, max_size=100), query=search_queries())
@settings(max_examples=100, deadline=1000)
def test_search_never_adds(
    data: list[dict[str, str]],
    query: str,
) -> None:
    """Search result is always a subset of the input."""
    spec = SearchSpec(query=query, fields=("name",))
    result = _engine.apply(data, spec)
    assert len(result) <= len(data)


@given(data=name_datasets(min_size=1, max_size=50))
@settings(max_examples=100, deadline=1000)
def test_empty_query_returns_all(
    data: list[dict[str, str]],
) -> None:
    """Empty query string returns all items."""
    spec = SearchSpec(query="", fields=("name",))
    result = _engine.apply(data, spec)
    assert len(result) == len(data)


@given(data=name_datasets(min_size=3, max_size=50), query=search_queries())
@settings(max_examples=100, deadline=1000)
def test_max_results_caps_output(
    data: list[dict[str, str]],
    query: str,
) -> None:
    """max_results always caps the output length."""
    spec = SearchSpec(query=query, fields=("name",), max_results=2)
    result = _engine.apply(data, spec)
    assert len(result) <= 2


@given(data=name_datasets(min_size=1, max_size=50))
@settings(max_examples=100, deadline=1000)
def test_min_length_short_query_returns_all(
    data: list[dict[str, str]],
) -> None:
    """Query shorter than min_length returns all items unfiltered."""
    spec = SearchSpec(query="ab", fields=("name",), min_length=5)
    result = _engine.apply(data, spec)
    assert len(result) == len(data)
