"""Tests for the FastAPI integration module.

This module tests FastAPI-specific utilities including PagedResponse
and pagination parameter dependencies.
"""

from __future__ import annotations

import pytest


# Skip all tests if FastAPI or httpx are not installed
fastapi = pytest.importorskip("fastapi")
pytest.importorskip("httpx")


from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from pypaginate.core.pages import Page, PageParams
from pypaginate.integrations.fastapi import PagedResponse, get_pagination_params


class ItemSchema(BaseModel):
    """Sample item schema for testing."""

    id: int
    name: str


class TestPagedResponse:
    """Tests for PagedResponse model - basic structure validation."""

    def test_paged_response_has_required_fields(self) -> None:
        """Test that PagedResponse class has the required fields."""
        # Verify the Pydantic model has the expected fields
        fields = PagedResponse.model_fields
        assert "items" in fields
        assert "total" in fields
        assert "page" in fields
        assert "limit" in fields

        # Verify from_page method exists
        assert hasattr(PagedResponse, "from_page")
        assert callable(PagedResponse.from_page)

    def test_page_params_structure(self) -> None:
        """Test PageParams structure (used by get_pagination_params)."""
        params = PageParams(page=1, limit=20)
        assert params.page == 1
        assert params.limit == 20


class TestGetPaginationParams:
    """Tests for get_pagination_params dependency via FastAPI."""

    def test_get_pagination_params_via_fastapi(self) -> None:
        """Test get_pagination_params through FastAPI endpoint."""
        app = FastAPI()

        @app.get("/test")
        def test_endpoint(params: PageParams = Depends(get_pagination_params)):
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)

        # Test default values
        response = client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 20

        # Test custom values
        response = client.get("/test?page=3&limit=50")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 3
        assert data["limit"] == 50

    def test_get_pagination_params_validation(self) -> None:
        """Test that pagination parameters are validated."""
        app = FastAPI()

        @app.get("/test")
        def test_endpoint(params: PageParams = Depends(get_pagination_params)):
            return {"page": params.page, "limit": params.limit}

        client = TestClient(app)

        # Test invalid page (< 1)
        response = client.get("/test?page=0")
        assert response.status_code == 422

        # Test invalid limit (< 1)
        response = client.get("/test?limit=0")
        assert response.status_code == 422

        # Test limit exceeds maximum (> 100)
        response = client.get("/test?limit=101")
        assert response.status_code == 422

    def test_get_pagination_params_returns_page_params(self) -> None:
        """Test that dependency returns PageParams instance."""
        app = FastAPI()

        @app.get("/test")
        def test_endpoint(params: PageParams = Depends(get_pagination_params)):
            return {
                "type": type(params).__name__,
                "page": params.page,
                "limit": params.limit,
            }

        client = TestClient(app)

        response = client.get("/test?page=2&limit=30")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "PageParams"
        assert data["page"] == 2
        assert data["limit"] == 30


class TestFastAPIIntegration:
    """Integration tests with FastAPI application."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Create a test FastAPI application."""
        app = FastAPI()

        @app.get("/items")
        def get_items(
            params: PageParams = Depends(get_pagination_params),
        ):
            """Test endpoint with pagination."""
            # Mock data
            all_items = [{"id": i, "name": f"Item {i}"} for i in range(1, 51)]

            # Calculate pagination
            start = (params.page - 1) * params.limit
            end = start + params.limit
            page_items = all_items[start:end]

            page = Page(
                items=page_items,
                total=len(all_items),
                page=params.page,
                limit=params.limit,
            )

            # Return as dict to avoid Pydantic generic issues
            response = PagedResponse.from_page(page)
            return {
                "items": response.items,
                "total": response.total,
                "page": response.page,
                "limit": response.limit,
            }

        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create a test client."""
        return TestClient(app)

    def test_fastapi_endpoint_default_pagination(self, client: TestClient) -> None:
        """Test FastAPI endpoint with default pagination parameters."""
        response = client.get("/items")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

        assert len(data["items"]) == 20  # Default limit
        assert data["total"] == 50
        assert data["page"] == 1
        assert data["limit"] == 20

    def test_fastapi_endpoint_custom_page(self, client: TestClient) -> None:
        """Test FastAPI endpoint with custom page parameter."""
        response = client.get("/items?page=2")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 2
        assert len(data["items"]) == 20
        assert data["items"][0]["id"] == 21  # Second page starts at item 21

    def test_fastapi_endpoint_custom_limit(self, client: TestClient) -> None:
        """Test FastAPI endpoint with custom limit parameter."""
        response = client.get("/items?limit=10")

        assert response.status_code == 200
        data = response.json()

        assert data["limit"] == 10
        assert len(data["items"]) == 10

    def test_fastapi_endpoint_custom_page_and_limit(self, client: TestClient) -> None:
        """Test FastAPI endpoint with custom page and limit parameters."""
        response = client.get("/items?page=3&limit=5")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 3
        assert data["limit"] == 5
        assert len(data["items"]) == 5
        assert data["items"][0]["id"] == 11  # Page 3, limit 5 starts at item 11

    def test_fastapi_endpoint_last_page(self, client: TestClient) -> None:
        """Test FastAPI endpoint on the last page."""
        response = client.get("/items?page=5&limit=10")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 5
        assert len(data["items"]) == 10
        assert data["items"][-1]["id"] == 50

    def test_fastapi_endpoint_page_beyond_total(self, client: TestClient) -> None:
        """Test FastAPI endpoint with page beyond total items."""
        response = client.get("/items?page=10&limit=20")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 10
        assert len(data["items"]) == 0  # No items on page 10

    def test_fastapi_endpoint_invalid_page_validation(self, client: TestClient) -> None:
        """Test that invalid page parameter is rejected."""
        response = client.get("/items?page=0")

        assert response.status_code == 422  # Validation error

    def test_fastapi_endpoint_invalid_limit_validation(self, client: TestClient) -> None:
        """Test that invalid limit parameter is rejected."""
        response = client.get("/items?limit=0")

        assert response.status_code == 422  # Validation error

    def test_fastapi_endpoint_limit_exceeds_maximum(self, client: TestClient) -> None:
        """Test that limit exceeding maximum is rejected."""
        response = client.get("/items?limit=101")

        assert response.status_code == 422  # Validation error

    def test_fastapi_endpoint_negative_page(self, client: TestClient) -> None:
        """Test that negative page is rejected."""
        response = client.get("/items?page=-1")

        assert response.status_code == 422  # Validation error

    def test_fastapi_endpoint_negative_limit(self, client: TestClient) -> None:
        """Test that negative limit is rejected."""
        response = client.get("/items?limit=-10")

        assert response.status_code == 422  # Validation error

    def test_fastapi_openapi_schema(self, client: TestClient) -> None:
        """Test that OpenAPI schema is correctly generated."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        # Check that the endpoint is documented
        assert "/items" in schema["paths"]
        assert "get" in schema["paths"]["/items"]

        # Check query parameters exist
        parameters = schema["paths"]["/items"]["get"].get("parameters", [])
        param_names = [p["name"] for p in parameters]

        assert "page" in param_names
        assert "limit" in param_names

        # Check page parameter has minimum constraint
        page_params = [p for p in parameters if p["name"] == "page"]
        if page_params:
            page_param = page_params[0]
            assert page_param["schema"]["minimum"] == 1

        # Check limit parameter has constraints
        limit_params = [p for p in parameters if p["name"] == "limit"]
        if limit_params:
            limit_param = limit_params[0]
            assert limit_param["schema"]["minimum"] == 1
            assert limit_param["schema"]["maximum"] == 100


class TestFastAPIImportError:
    """Test handling of missing FastAPI dependencies."""

    def test_module_requires_fastapi(self) -> None:
        """Test that module can be imported when FastAPI is installed."""
        # This test will only run if FastAPI is installed (due to pytest.importorskip)
        from pypaginate.integrations import fastapi

        assert hasattr(fastapi, "PagedResponse")
        assert hasattr(fastapi, "get_pagination_params")
