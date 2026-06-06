"""End-to-end sort flows — multi-key ordering and null placement.

Covers :func:`pypaginate.sort` for ascending/descending single keys, tie-broken
multi-key ordering (verified against Python's own stable tuple sort), explicit
``nulls`` placement, and the property that a global sort order survives being
sliced into pages.
"""

from __future__ import annotations

import pytest
from tests.fixtures.helpers import ids_of, names_of

from pypaginate import OffsetParams, SortSpec, paginate, sort


pytestmark = [pytest.mark.e2e, pytest.mark.sorting]

Row = dict[str, object]


def test_single_key_ascending(users: list[Row]) -> None:
    """Ascending sort by name matches Python's default string ordering."""
    names = names_of(sort(users, SortSpec(field="name", direction="asc")))
    assert names == sorted(names)


def test_single_key_descending(users: list[Row]) -> None:
    """Descending sort by name reverses the ascending order."""
    names = names_of(sort(users, [SortSpec(field="name", direction="desc")]))
    assert names == sorted(names, reverse=True)


def test_multi_key_tie_break(users: list[Row]) -> None:
    """Age-asc then name-asc matches a stable Python ``(age, name)`` sort."""
    result = sort(
        users,
        [
            SortSpec(field="age", direction="asc"),
            SortSpec(field="name", direction="asc"),
        ],
    )
    reference = sorted(users, key=lambda r: (int(r["age"]), str(r["name"])))
    assert ids_of(result) == ids_of(reference)


def test_multi_key_mixed_directions(users: list[Row]) -> None:
    """Age-desc then name-asc matches the equivalent Python key."""
    result = sort(
        users,
        [
            SortSpec(field="age", direction="desc"),
            SortSpec(field="name", direction="asc"),
        ],
    )
    reference = sorted(users, key=lambda r: (-int(r["age"]), str(r["name"])))
    assert ids_of(result) == ids_of(reference)


def test_stable_for_equal_keys() -> None:
    """Rows sharing a sort key keep their original relative order."""
    rows = [{"id": i, "group": i % 2} for i in range(10)]
    result = sort(rows, SortSpec(field="group", direction="asc"))
    evens = [r["id"] for r in result if r["group"] == 0]
    assert evens == [0, 2, 4, 6, 8]


def test_nulls_last(nullable_rows: list[Row]) -> None:
    """``nulls='last'`` pushes ``None`` scores after the ranked values."""
    result = sort(nullable_rows, SortSpec(field="score", direction="asc", nulls="last"))
    assert ids_of(result) == [3, 5, 1, 2, 4]


def test_nulls_first(nullable_rows: list[Row]) -> None:
    """``nulls='first'`` pulls ``None`` scores ahead of the ranked values."""
    result = sort(nullable_rows, SortSpec(field="score", direction="asc", nulls="first"))
    assert ids_of(result) == [2, 4, 3, 5, 1]


def test_global_order_survives_pagination(users: list[Row]) -> None:
    """Walking pages of a sorted dataset reconstructs the global order."""
    ordered = sort(users, SortSpec(field="name", direction="asc"))
    limit, collected, page_num = 6, [], 1
    while True:
        page = paginate(ordered, OffsetParams(page=page_num, limit=limit))
        collected.extend(page.items)
        if not page.has_next:
            break
        page_num += 1
    assert names_of(collected) == sorted(names_of(users))
