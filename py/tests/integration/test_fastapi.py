"""FastAPI adapter integration tests through a real ASGI app.

Builds an app wired with the adapter's dependency callables (``OffsetDep``,
``SortDep``, ``SearchDep``) and a declarative ``FilterDep`` subclass, then drives
it with ``fastapi.testclient.TestClient`` to assert query params parse into the
package's params/specs and that out-of-range pagination yields HTTP 422.
"""

from __future__ import annotations

from typing import Annotated

import pytest
from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

from pypaginate import MAX_LIMIT, paginate
from pypaginate.adapters.fastapi import (
    FilterDep,
    FilterField,
    OffsetDep,
    SearchDep,
    SortDep,
)


pytestmark = [pytest.mark.integration, pytest.mark.fastapi]


_DATA: list[dict[str, object]] = [{"id": i, "name": f"user_{i}"} for i in range(1, 26)]


class UserFilters(FilterDep):
    """Declarative query-param filters for the ``/filter`` endpoint."""

    name: str | None = FilterField(None, operator="contains")
    min_age: int | None = FilterField(None, field="age", operator="gte")


def _build_app() -> FastAPI:
    """Wire an app exercising every adapter dependency type."""
    app = FastAPI()

    @app.get("/users")
    def list_users(params: OffsetDep) -> dict[str, object]:
        page = paginate(_DATA, params)
        return {
            "items": list(page.items),
            "total": page.total,
            "pages": page.pages,
            "page": page.page,
            "limit": page.limit,
            "has_next": page.has_next,
            "offset": params.offset,
        }

    @app.get("/sort")
    def read_sort(sort: SortDep) -> dict[str, object]:
        return {"sort": [[s.field, s.direction] for s in sort]}

    @app.get("/search")
    def read_search(search: SearchDep) -> dict[str, object]:
        if search is None:
            return {"search": None}
        return {"query": search.query, "fields": search.fields}

    @app.get("/filter")
    def read_filter(filters: Annotated[UserFilters, Query()]) -> dict[str, object]:
        return {"specs": [[s.field, s.operator, s.value] for s in filters.to_specs()]}

    return app


@pytest.fixture
def client() -> TestClient:
    """A ``TestClient`` bound to the wired app."""
    return TestClient(_build_app())


def test_offset_params_parse_and_paginate(client: TestClient) -> None:
    response = client.get("/users", params={"page": 2, "limit": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == [{"id": i, "name": f"user_{i}"} for i in range(11, 21)]
    assert body["page"] == 2
    assert body["limit"] == 10
    assert body["total"] == 25
    assert body["pages"] == 3
    assert body["has_next"] is True
    assert body["offset"] == 10


def test_offset_params_defaults(client: TestClient) -> None:
    response = client.get("/users")

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 20
    assert len(body["items"]) == 20


def test_offset_page_zero_is_422(client: TestClient) -> None:
    response = client.get("/users", params={"page": 0})

    assert response.status_code == 422


def test_offset_limit_over_max_is_422(client: TestClient) -> None:
    response = client.get("/users", params={"limit": MAX_LIMIT + 1})

    assert response.status_code == 422


def test_sort_params_parse(client: TestClient) -> None:
    response = client.get("/sort", params={"sort": "name,-age,+id"})

    assert response.status_code == 200
    assert response.json()["sort"] == [
        ["name", None],
        ["age", "desc"],
        ["id", None],
    ]


def test_sort_params_absent_is_empty(client: TestClient) -> None:
    response = client.get("/sort")

    assert response.status_code == 200
    assert response.json()["sort"] == []


def test_search_params_parse(client: TestClient) -> None:
    response = client.get("/search", params={"q": "ann", "search_fields": "name, email"})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "ann"
    assert body["fields"] == ["name", "email"]


def test_search_params_absent_is_none(client: TestClient) -> None:
    response = client.get("/search")

    assert response.status_code == 200
    assert response.json()["search"] is None


def test_filter_dep_builds_specs(client: TestClient) -> None:
    response = client.get("/filter", params={"name": "al", "min_age": 30})

    assert response.status_code == 200
    assert response.json()["specs"] == [
        ["name", "contains", "al"],
        ["age", "gte", 30],
    ]


def test_filter_dep_skips_unset_fields(client: TestClient) -> None:
    response = client.get("/filter", params={"min_age": 18})

    assert response.status_code == 200
    assert response.json()["specs"] == [["age", "gte", 18]]


def test_filter_dep_empty_is_no_specs(client: TestClient) -> None:
    response = client.get("/filter")

    assert response.status_code == 200
    assert response.json()["specs"] == []
