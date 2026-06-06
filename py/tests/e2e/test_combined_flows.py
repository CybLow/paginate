"""End-to-end combined pipeline flows via :meth:`pypaginate.Dataset.page`.

Runs filter -> search -> sort -> offset-paginate in a single native call and
checks the whole pipeline holds together: predicates are honoured, the surviving
rows are globally ordered, walking the pages reaches the reported total, and the
call is deterministic across repeated runs.
"""

from __future__ import annotations

import pytest
from tests.fixtures.helpers import ids_of, names_of

from pypaginate import (
    Dataset,
    FilterSpec,
    OffsetParams,
    SearchSpec,
    SortSpec,
)


pytestmark = pytest.mark.e2e

Row = dict[str, object]


def test_full_pipeline_one_call(dataset: Dataset[Row], users: list[Row]) -> None:
    """Filter + search + sort + paginate resolve together in one page call."""
    page = dataset.page(
        OffsetParams(page=1, limit=5),
        filters=[FilterSpec(field="active", operator="eq", value=True)],
        sorting=[SortSpec(field="age", direction="asc")],
        search=SearchSpec(query="a", fields=["name"]),
    )
    ages = [int(row["age"]) for row in page.items]
    assert ages == sorted(ages)
    assert all(row["active"] for row in page.items)
    assert all("a" in str(row["name"]).lower() for row in page.items)


def test_filter_then_sort_global_order(dataset: Dataset[Row]) -> None:
    """The filtered subset is globally name-sorted before being paged."""
    page = dataset.page(
        OffsetParams(page=1, limit=100),
        filters=[FilterSpec(field="active", operator="eq", value=True)],
        sorting=[SortSpec(field="name", direction="asc")],
    )
    names = names_of(page.items)
    assert names == sorted(names)
    assert all(row["active"] for row in page.items)


def test_walk_filtered_pages_reaches_total(dataset: Dataset[Row]) -> None:
    """Walking every page of a filtered query collects exactly ``total`` rows."""
    filters = [FilterSpec(field="active", operator="eq", value=True)]
    limit, collected, page_num = 4, [], 1
    while True:
        page = dataset.page(OffsetParams(page=page_num, limit=limit), filters=filters)
        collected.extend(page.items)
        total = page.total
        if not page.has_next:
            break
        page_num += 1
    assert len(collected) == total


def test_pipeline_matches_standalone_helpers(dataset: Dataset[Row], users: list[Row]) -> None:
    """``Dataset.page`` agrees with composing the standalone query helpers."""
    from pypaginate import filter as filter_rows, sort as sort_rows

    page = dataset.page(
        OffsetParams(page=1, limit=10),
        filters=[FilterSpec(field="age", operator="gte", value=40)],
        sorting=[SortSpec(field="age", direction="asc"), SortSpec(field="name", direction="asc")],
    )
    reference = sort_rows(
        filter_rows(users, FilterSpec(field="age", operator="gte", value=40)),
        [SortSpec(field="age", direction="asc"), SortSpec(field="name", direction="asc")],
    )
    assert ids_of(page.items) == ids_of(reference)[:10]


def test_pipeline_is_deterministic(dataset: Dataset[Row]) -> None:
    """Running the same pipeline twice yields byte-identical pages."""
    params = OffsetParams(page=2, limit=7)
    kwargs = {
        "filters": [FilterSpec(field="active", operator="eq", value=True)],
        "sorting": [SortSpec(field="name", direction="asc")],
    }
    first = dataset.page(params, **kwargs)
    second = dataset.page(params, **kwargs)
    assert ids_of(first.items) == ids_of(second.items)
    assert (first.total, first.pages) == (second.total, second.pages)


def test_pipeline_to_empty(dataset: Dataset[Row]) -> None:
    """A filter matching nothing yields an empty, zero-total page."""
    page = dataset.page(
        OffsetParams(page=1, limit=10),
        filters=[FilterSpec(field="name", operator="eq", value="__nobody__")],
    )
    assert page.total == 0
    assert list(page.items) == []
    assert page.has_next is False
