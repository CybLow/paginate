"""End-to-end FastAPI flows — request query string to paginated JSON.

Wires a real ASGI app with the package's FastAPI adapter dependencies
(``OffsetDep``, ``SortDep``, ``SearchDep`` and a declarative ``FilterDep``
subclass), then drives it with ``TestClient`` to prove the full journey: HTTP
query params parse into specs, run through :meth:`pypaginate.Dataset.page`, and
come back as a paginated JSON body (with HTTP 422 for invalid pagination).

The declarative ``FilterDep`` forbids unknown query params (it is designed to own
the whole query string), so it gets its own route; the combined-pipeline route
builds its filters from plain query args alongside the sort/search deps.
"""

from __future__ import annotations

from typing import Annotated

import pytest
from tests.factories.data import make_users


pytest.importorskip("fastapi")

from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

from pypaginate import (
    MAX_LIMIT,
    Dataset,
    FilterSpec,
    OffsetPage,
    OffsetParams,
)
from pypaginate.adapters.fastapi import (
    FilterDep,
    FilterField,
    OffsetDep,
    SearchDep,
    SortDep,
)


pytestmark = [pytest.mark.e2e, pytest.mark.fastapi]

Row = dict[str, object]
_DATA: list[Row] = make_users(60)
_DATASET: Dataset[Row] = Dataset(_DATA)


class UserFilters(FilterDep):
    """Declarative query-param filters for the standalone ``/declared`` route."""

    name: str | None = FilterField(None, operator="contains")
    active: bool | None = FilterField(None, operator="eq")
    min_age: int | None = FilterField(None, field="age", operator="gte")


def _payload(page: OffsetPage[Row]) -> dict[str, object]:
    """Serialise an offset page into a JSON-safe response body."""
    return {
        "items": list(page.items),
        "total": page.total,
        "page": page.page,
        "pages": page.pages,
        "limit": page.limit,
        "has_next": page.has_next,
        "has_previous": page.has_previous,
    }


def _manual_filters(active: bool | None, age_gte: int | None) -> list[FilterSpec]:
    """Build filter specs from plain query args (skipping the unset ones)."""
    specs: list[FilterSpec] = []
    if active is not None:
        specs.append(FilterSpec(field="active", operator="eq", value=active))
    if age_gte is not None:
        specs.append(FilterSpec(field="age", operator="gte", value=age_gte))
    return specs


def _build_app() -> FastAPI:
    """Wire an app whose routes drive the adapter deps through ``Dataset.page``."""
    app = FastAPI()
    _register_query_routes(app)
    _register_filter_routes(app)
    return app


def _register_query_routes(app: FastAPI) -> None:
    """Offset, sort, and search routes (each on top of ``Dataset.page``)."""

    @app.get("/users")
    def list_users(params: OffsetDep) -> dict[str, object]:
        return _payload(_DATASET.page(params))

    @app.get("/sorted")
    def list_sorted(params: OffsetDep, sort: SortDep) -> dict[str, object]:
        return _payload(_DATASET.page(params, sorting=sort))

    @app.get("/searched")
    def list_searched(params: OffsetDep, search: SearchDep) -> dict[str, object]:
        return _payload(_DATASET.page(params, search=search))


def _register_filter_routes(app: FastAPI) -> None:
    """The declarative-filter route and the full combined-pipeline route."""

    @app.get("/declared")
    def list_declared(filters: Annotated[UserFilters, Query()]) -> dict[str, object]:
        page = _DATASET.page(OffsetParams(limit=MAX_LIMIT), filters=filters.to_specs())
        return _payload(page)

    @app.get("/pipeline")
    def list_pipeline(
        params: OffsetDep,
        sort: SortDep,
        active: bool | None = None,
        age_gte: int | None = None,
    ) -> dict[str, object]:
        filters = _manual_filters(active, age_gte)
        return _payload(_DATASET.page(params, filters=filters, sorting=sort))


@pytest.fixture
def client() -> TestClient:
    """A ``TestClient`` bound to the wired app."""
    return TestClient(_build_app())


def test_offset_walk_collects_all(client: TestClient) -> None:
    """Walking pages over HTTP collects every row exactly once."""
    limit, collected, page_num = 7, [], 1
    while True:
        body = client.get("/users", params={"page": page_num, "limit": limit}).json()
        collected.extend(body["items"])
        if not body["has_next"]:
            break
        page_num += 1
    assert len(collected) == len(_DATA)


def test_offset_metadata(client: TestClient) -> None:
    """The first page reports the correct total/pages/neighbour flags."""
    body = client.get("/users", params={"page": 1, "limit": 10}).json()
    assert body["total"] == len(_DATA)
    assert body["pages"] == 6
    assert body["has_previous"] is False
    assert body["has_next"] is True
    assert len(body["items"]) == 10


def test_page_zero_is_422(client: TestClient) -> None:
    """An out-of-range page number is rejected as HTTP 422."""
    assert client.get("/users", params={"page": 0}).status_code == 422


def test_limit_over_max_is_422(client: TestClient) -> None:
    """A limit above ``MAX_LIMIT`` is rejected as HTTP 422."""
    assert client.get("/users", params={"limit": MAX_LIMIT + 1}).status_code == 422


def test_sort_via_query(client: TestClient) -> None:
    """``?sort=name`` returns rows globally ascending by name."""
    body = client.get("/sorted", params={"sort": "name", "limit": 100}).json()
    names = [row["name"] for row in body["items"]]
    assert names == sorted(names)


def test_sort_descending_via_query(client: TestClient) -> None:
    """``?sort=-age`` returns rows descending by age."""
    body = client.get("/sorted", params={"sort": "-age", "limit": 100}).json()
    ages = [row["age"] for row in body["items"]]
    assert ages == sorted(ages, reverse=True)


def test_search_via_query(client: TestClient) -> None:
    """``?q=Alice`` narrows the page to matching rows only."""
    body = client.get(
        "/searched", params={"q": "Alice", "search_fields": "name", "limit": 100}
    ).json()
    assert body["total"] > 0
    assert all("alice" in str(row["name"]).lower() for row in body["items"])


def test_declared_filter_via_query(client: TestClient) -> None:
    """The declarative ``FilterDep`` route keeps only matching rows."""
    body = client.get("/declared", params={"active": "true", "min_age": 40}).json()
    assert body["total"] > 0
    assert all(row["active"] and row["age"] >= 40 for row in body["items"])


def test_declared_filter_empty_query_returns_all(client: TestClient) -> None:
    """With no filter params the declarative route returns the whole dataset."""
    body = client.get("/declared").json()
    assert body["total"] == len(_DATA)


def test_full_pipeline_via_query(client: TestClient) -> None:
    """Filter + sort + paginate compose in one HTTP request."""
    body = client.get(
        "/pipeline",
        params={"active": "true", "sort": "age", "limit": 100},
    ).json()
    ages = [row["age"] for row in body["items"]]
    assert ages == sorted(ages)
    assert all(row["active"] for row in body["items"])
