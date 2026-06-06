"""Cross-language parity: the new Python API agrees with the frozen golden.

The same ``tests/fixtures/parity.json`` golden is asserted by the Rust core
(``crates/core/tests/parity.rs``) and the Node/TS binding (``ts/test/parity.test.mjs``).
All three engines must encode identical cursor bytes and return identical
filter / sort / search results for identical inputs. Here we exercise the
*public* Python surface (:func:`pypaginate.filter` / :func:`~pypaginate.sort` /
:func:`~pypaginate.search` plus the spec dataclasses) and the cursor codec, then
assert both the reconstructed indices and the selected items match the golden
byte-for-byte. If the engine or codec drifts, this fails until the golden is
regenerated and its diff reviewed (see ``tests/fixtures/generate_parity.py``).
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from pypaginate import (
    FilterSpec,
    SearchSpec,
    SortSpec,
    _core,
    filter,
    search,
    sort,
)


pytestmark = pytest.mark.property

# Repo-root fixture shared by the Rust, TS, and Python parity suites.
_FIXTURE = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "parity.json"
_DATA: dict[str, Any] = json.loads(_FIXTURE.read_text())

_TAG_BUILDERS = {
    "datetime": datetime.fromisoformat,
    "date": date.fromisoformat,
    "decimal": Decimal,
    "uuid": UUID,
}


def _rebuild(value: Any) -> Any:
    """Tagged dict -> rich Python object; everything else passes through."""
    if isinstance(value, dict) and "__type__" in value:
        return _TAG_BUILDERS[value["__type__"]](value["v"])
    return value


def _indices_of(returned: list[Any], items: list[Any]) -> list[int]:
    """Map each returned host row back to its index in ``items`` (by identity).

    The public helpers return the *same* object references handed in, so identity
    mapping recovers the engine's index permutation for an exact golden compare.
    """
    positions = {id(item): index for index, item in enumerate(items)}
    return [positions[id(row)] for row in returned]


def _filter_specs(rows: list[list[Any]]) -> list[FilterSpec]:
    return [
        FilterSpec(field=field, operator=operator, value=value, logic=logic)
        for field, operator, value, logic in rows
    ]


def _sort_specs(rows: list[list[Any]]) -> list[SortSpec]:
    return [
        SortSpec(field=field, direction=direction, nulls=nulls) for field, direction, nulls in rows
    ]


# --------------------------------------------------------------------------- #
# Cursor codec — byte-identical encode + lossless round-trip.
# --------------------------------------------------------------------------- #
_CURSOR_CASES = _DATA["cursors"] + _DATA["cursors_typed"]


@pytest.mark.parametrize("case", _CURSOR_CASES)
def test_cursor_encode_matches_golden(case: dict[str, Any]) -> None:
    values = [_rebuild(value) for value in case["values"]]

    encoded = _core.encode_cursor(values)

    assert encoded == case["encoded"]


@pytest.mark.parametrize("case", _CURSOR_CASES)
def test_cursor_round_trip_matches_golden(case: dict[str, Any]) -> None:
    expected = tuple(_rebuild(value) for value in case["values"])

    decoded = tuple(_core.decode_cursor(case["encoded"]))

    assert decoded == expected


# --------------------------------------------------------------------------- #
# Filter — flat specs (each spec carries its own AND/OR logic).
# --------------------------------------------------------------------------- #
@pytest.mark.filters
@pytest.mark.parametrize("case", _DATA["filter"])
def test_filter_matches_golden(case: dict[str, Any]) -> None:
    items = case["items"]
    specs = _filter_specs(case["specs"])

    matched = filter(items, specs)

    assert _indices_of(matched, items) == case["expected"]
    assert matched == [items[index] for index in case["expected"]]


# --------------------------------------------------------------------------- #
# Sort — stable, null-aware ordering.
# --------------------------------------------------------------------------- #
@pytest.mark.sorting
@pytest.mark.parametrize("case", _DATA["sort"])
def test_sort_matches_golden(case: dict[str, Any]) -> None:
    items = case["items"]
    specs = _sort_specs(case["specs"])

    ordered = sort(items, specs)

    assert _indices_of(ordered, items) == case["expected"]
    assert ordered == [items[index] for index in case["expected"]]


# --------------------------------------------------------------------------- #
# Search — ranked relevance order.
# --------------------------------------------------------------------------- #
@pytest.mark.search
@pytest.mark.parametrize("case", _DATA["search"])
def test_search_matches_golden(case: dict[str, Any]) -> None:
    items = case["items"]
    spec = SearchSpec(query=case["query"], fields=case["fields"], mode=case["mode"])

    ranked = search(items, spec)

    assert _indices_of(ranked, items) == case["expected"]
    assert ranked == [items[index] for index in case["expected"]]
