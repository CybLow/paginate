"""Cross-language parity: Python ``_core`` agrees with the frozen golden.

The same ``tests/fixtures/parity.json`` golden is asserted by the Rust core
(``crates/core/tests/parity.rs``) and the Node/TS binding (``ts/test/parity.test.mjs``).
All three must encode identical cursor bytes and return identical filter / sort /
search indices for identical inputs. If the engine or codec drifts, at least one
language diverges from the frozen golden and fails until it is regenerated and
its diff reviewed (see ``tests/fixtures/generate_parity.py``).
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest


_core = pytest.importorskip("pypaginate._core")

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


@pytest.mark.parametrize("case", _DATA["cursors"] + _DATA["cursors_typed"])
def test_cursor_encode_matches_golden(case: dict[str, Any]) -> None:
    values = [_rebuild(v) for v in case["values"]]
    assert _core.encode_cursor(values) == case["encoded"]


@pytest.mark.parametrize("case", _DATA["cursors"] + _DATA["cursors_typed"])
def test_cursor_round_trip(case: dict[str, Any]) -> None:
    values = tuple(_rebuild(v) for v in case["values"])
    assert tuple(_core.decode_cursor(case["encoded"])) == values


@pytest.mark.parametrize("case", _DATA["filter"])
def test_filter_matches_golden(case: dict[str, Any]) -> None:
    specs = [tuple(s) for s in case["specs"]]
    assert list(_core.filter_indices(case["items"], specs)) == case["expected"]


@pytest.mark.parametrize("case", _DATA["sort"])
def test_sort_matches_golden(case: dict[str, Any]) -> None:
    specs = [tuple(s) for s in case["specs"]]
    assert list(_core.sort_indices(case["items"], specs)) == case["expected"]


@pytest.mark.parametrize("case", _DATA["search"])
def test_search_matches_golden(case: dict[str, Any]) -> None:
    got = _core.search_indices(case["items"], case["query"], case["fields"], mode=case["mode"])
    assert list(got) == case["expected"]
