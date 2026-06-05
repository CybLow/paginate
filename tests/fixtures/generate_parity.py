"""Generate the frozen cross-language parity fixture (``parity.json``).

The fixture is the single source of truth for *cross-language agreement*: the
Rust core, the Python binding, and the Node/TS binding must all produce the
**same** cursor bytes and the **same** filter/sort/search indices for the same
inputs. The expected values are computed once from the built ``pypaginate._core``
engine and frozen into ``parity.json`` (committed to git). A later change to the
codec or an engine that breaks byte-identity makes at least one language diverge
from the frozen golden, so every consumer test fails until the fixture is
deliberately regenerated and its diff reviewed.

Regenerate with::

    cd py && uv run python ../tests/fixtures/generate_parity.py

Typed scalars (datetime/date/decimal/uuid) are written in the tagged wire form
``{"__type__": "<tag>", "v": "<iso>"}``. Each consumer feeds them to the core in
its idiomatic way (Python rebuilds real ``datetime``/``Decimal``/``UUID`` objects;
JS passes the tagged object as-is; Rust builds the typed ``Value`` variant) — all
three encode to identical bytes because the tagged map *is* the wire form.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from pypaginate import _core


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


# -- Hand-authored input cases (outputs are computed below) ------------------

# Plain scalar cursors: byte-identity AND decode round-trip hold in all three
# languages (no host type loss).
CURSOR_PLAIN: list[list[Any]] = [
    [1, "a"],
    [True, None, 3.5],
    ["café"],  # non-ASCII -> ensure_ascii \uXXXX escaping
    ['a"b\\c\n'],  # JSON string escaping
    [],  # empty ordering tuple
    [-42, 1000000],  # negative + large (JS-safe; i64 extremes are unit-tested)
]

# Typed-scalar cursors: cross-language *encode* byte-identity is the guarantee
# (decode is host-specific: JS yields strings, Python rebuilds rich types).
CURSOR_TYPED: list[list[Any]] = [
    [{"__type__": "datetime", "v": "2021-06-01T12:30:00"}, 42],
    [{"__type__": "date", "v": "2021-06-01"}],
    [{"__type__": "decimal", "v": "3.14159"}],
    [{"__type__": "uuid", "v": "12345678-1234-5678-1234-567812345678"}],
]

_PEOPLE = [
    {"age": 15, "name": "alice"},
    {"age": 20, "name": "bob"},
    {"age": 30, "name": "cyril"},
    {"age": 20, "name": "alicia"},
]

FILTER_CASES = [
    {"items": _PEOPLE, "specs": [["age", "gte", 18, "and"]]},  # -> 1,2,3
    {"items": _PEOPLE, "specs": [["name", "contains", "ali", "and"]]},  # -> 0,3
    {
        "items": _PEOPLE,
        "specs": [["age", "eq", 20, "and"], ["name", "starts_with", "a", "and"]],
    },  # -> 3
]

SORT_CASES = [
    {"items": _PEOPLE, "specs": [["age", "desc", "last"]]},
    {"items": _PEOPLE, "specs": [["age", "asc", "last"], ["name", "asc", "last"]]},
]

SEARCH_CASES = [
    {"items": _PEOPLE, "query": "ali", "fields": ["name"], "mode": "contains"},
    {"items": _PEOPLE, "query": "bob", "fields": ["name"], "mode": "exact"},
]


def _cursor_entry(values: list[Any]) -> dict[str, Any]:
    rebuilt = [_rebuild(v) for v in values]
    return {"values": values, "encoded": _core.encode_cursor(rebuilt)}


def _filter_entry(case: dict[str, Any]) -> dict[str, Any]:
    specs = [tuple(s) for s in case["specs"]]
    expected = _core.filter_indices(case["items"], specs)
    return {**case, "expected": list(expected)}


def _sort_entry(case: dict[str, Any]) -> dict[str, Any]:
    specs = [tuple(s) for s in case["specs"]]
    expected = _core.sort_indices(case["items"], specs)
    return {**case, "expected": list(expected)}


def _search_entry(case: dict[str, Any]) -> dict[str, Any]:
    expected = _core.search_indices(case["items"], case["query"], case["fields"], mode=case["mode"])
    return {**case, "expected": list(expected)}


def build() -> dict[str, Any]:
    return {
        "_comment": "FROZEN golden — regenerate with tests/fixtures/generate_parity.py",
        "cursors": [_cursor_entry(v) for v in CURSOR_PLAIN],
        "cursors_typed": [_cursor_entry(v) for v in CURSOR_TYPED],
        "filter": [_filter_entry(c) for c in FILTER_CASES],
        "sort": [_sort_entry(c) for c in SORT_CASES],
        "search": [_search_entry(c) for c in SEARCH_CASES],
    }


def main() -> None:
    out = Path(__file__).resolve().parent / "parity.json"
    out.write_text(json.dumps(build(), indent=2, ensure_ascii=True) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
