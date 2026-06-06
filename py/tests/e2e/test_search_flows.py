"""End-to-end search flows — ranked, fuzzy, and mode/limit variations.

Drives :func:`pypaginate.search` over the deterministic users: default ranked
``contains`` matching, ``prefix`` / ``exact`` modes, fuzzy and ``token_sort``
strategies that tolerate typos and reordered tokens, plus the ``max_results`` cap
and ``min_length`` gate. Results come back in relevance order.
"""

from __future__ import annotations

import pytest
from tests.fixtures.helpers import names_of

from pypaginate import SearchSpec, search


pytestmark = [pytest.mark.e2e, pytest.mark.search]

Row = dict[str, object]


def test_ranked_contains_match(users: list[Row]) -> None:
    """Default ``contains`` search returns every row containing the query."""
    result = search(users, SearchSpec(query="Alice", fields=["name"]))
    expected = [row for row in users if "Alice" in str(row["name"])]
    assert len(result) == len(expected)
    assert all("alice" in str(row["name"]).lower() for row in result)


def test_ranked_orders_best_match_first(users: list[Row]) -> None:
    """Fuzzy ranking surfaces the closest name ahead of weaker matches."""
    result = search(users, SearchSpec(query="Bob", fields=["name"], fuzzy="fuzzy", threshold=20))
    assert result
    assert str(result[0]["name"]).startswith("Bob")


def test_prefix_mode(users: list[Row]) -> None:
    """Prefix mode matches tokens that begin with the query."""
    result = search(users, SearchSpec(query="ali", fields=["name"], mode="prefix"))
    assert result
    assert all(str(row["name"]).lower().startswith("ali") for row in result)


def test_exact_mode_whole_value(users: list[Row]) -> None:
    """Exact mode matches only the row whose field equals the query."""
    target = str(users[0]["email"])
    result = search(users, SearchSpec(query=target, fields=["email"], mode="exact"))
    assert [row["email"] for row in result] == [target]


def test_fuzzy_tolerates_typo(users: list[Row]) -> None:
    """A fuzzy query missing a character still matches the intended rows."""
    strict = search(users, SearchSpec(query="Alic", fields=["name"]))
    fuzzy = search(users, SearchSpec(query="Alic", fields=["name"], fuzzy="fuzzy", threshold=30))
    assert len(fuzzy) >= len(strict)
    assert fuzzy


def test_token_sort_handles_reordered_tokens(users: list[Row]) -> None:
    """``token_sort`` matches a full name even with its tokens swapped."""
    full = str(users[0]["name"])
    swapped = " ".join(reversed(full.split()))
    result = search(
        users,
        SearchSpec(query=swapped, fields=["name"], fuzzy="token_sort", threshold=60),
    )
    assert full in names_of(result)


def test_max_results_caps_output(users: list[Row]) -> None:
    """``max_results`` truncates the ranked output to the requested size."""
    result = search(users, SearchSpec(query="a", fields=["name"], max_results=3))
    assert len(result) == 3


def test_min_length_gate_returns_all(users: list[Row]) -> None:
    """A query shorter than ``min_length`` skips filtering and returns all rows."""
    result = search(users, SearchSpec(query="a", fields=["name"], min_length=5))
    assert len(result) == len(users)


def test_multi_field_search(users: list[Row]) -> None:
    """Searching multiple fields matches on any of them."""
    result = search(users, SearchSpec(query="example.com", fields=["name", "email"]))
    assert len(result) == len(users)
