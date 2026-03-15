"""Tests for FastAPI pagination dependencies."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pypaginate.adapters.fastapi import CursorDep, OffsetDep
from pypaginate.domain.models import CursorParams, OffsetParams


class TestOffsetDependency:
    def test_creates_valid_offset_params(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: OffsetDep) -> dict[str, int]:
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)
        response = client.get("/test?page=2&limit=50")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 50

    def test_default_page_one(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: OffsetDep) -> dict[str, int]:
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)
        response = client.get("/test")

        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 20

    @pytest.mark.parametrize(
        ("page", "limit"),
        [(1, 10), (5, 100), (1, 1000)],
        ids=["first-page", "mid-page", "max-limit"],
    )
    def test_various_valid_params(self, page: int, limit: int) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: OffsetDep) -> dict[str, int]:
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)
        response = client.get(f"/test?page={page}&limit={limit}")

        data = response.json()
        assert data["page"] == page
        assert data["limit"] == limit

    def test_returns_offset_params_type(self) -> None:
        app = FastAPI()
        captured: list[object] = []

        @app.get("/test")
        def endpoint(params: OffsetDep) -> dict[str, int]:
            captured.append(params)
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)
        client.get("/test?page=3&limit=15")

        assert isinstance(captured[0], OffsetParams)


class TestCursorDependency:
    def test_creates_valid_cursor_params(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: CursorDep) -> dict[str, object]:
            return {"limit": params.limit, "after": params.after, "before": params.before}

        client = TestClient(app)
        response = client.get("/test?limit=30&after=abc")

        data = response.json()
        assert data["after"] == "abc"
        assert data["before"] is None

    def test_no_cursors(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: CursorDep) -> dict[str, object]:
            return {"limit": params.limit, "after": params.after, "before": params.before}

        client = TestClient(app)
        response = client.get("/test?limit=20")

        data = response.json()
        assert data["limit"] == 20
        assert data["after"] is None
        assert data["before"] is None

    def test_before_cursor(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: CursorDep) -> dict[str, object]:
            return {"limit": params.limit, "after": params.after, "before": params.before}

        client = TestClient(app)
        response = client.get("/test?limit=10&before=xyz")

        data = response.json()
        assert data["before"] == "xyz"
        assert data["after"] is None

    def test_custom_limit(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: CursorDep) -> dict[str, object]:
            return {"limit": params.limit}

        client = TestClient(app)
        response = client.get("/test?limit=50")

        assert response.json()["limit"] == 50

    def test_returns_cursor_params_type(self) -> None:
        app = FastAPI()
        captured: list[object] = []

        @app.get("/test")
        def endpoint(params: CursorDep) -> dict[str, object]:
            captured.append(params)
            return {"limit": params.limit}

        client = TestClient(app)
        client.get("/test?limit=25&after=x")

        assert isinstance(captured[0], CursorParams)


class TestAnnotatedTypes:
    def test_offset_dep_is_annotated_type(self) -> None:
        assert hasattr(OffsetDep, "__metadata__")

    def test_cursor_dep_is_annotated_type(self) -> None:
        assert hasattr(CursorDep, "__metadata__")


class TestFastAPIIntegration:
    def test_offset_dep_works_with_fastapi(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: OffsetDep) -> dict[str, int]:
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)
        response = client.get("/test?page=2&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 10

    def test_cursor_dep_works_with_fastapi(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: CursorDep) -> dict[str, object]:
            return {"limit": params.limit, "after": params.after}

        client = TestClient(app)
        response = client.get("/test?limit=15&after=abc123")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 15
        assert data["after"] == "abc123"

    def test_offset_dep_defaults(self) -> None:
        app = FastAPI()

        @app.get("/test")
        def endpoint(params: OffsetDep) -> dict[str, int]:
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 20
