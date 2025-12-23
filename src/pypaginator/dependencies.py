"""FastAPI integration for the pagination module.

This module provides Pydantic models and FastAPI dependencies to easily
integrate pagination into API endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

from .core.pages import Page, PageParams


if TYPE_CHECKING:
    from collections.abc import Sequence


T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    """Pydantic model for paginated responses.

    Wraps the Page dataclass to ensure correct OpenAPI schema generation.
    Usage:
        @app.get("/items", response_model=PagedResponse[ItemSchema])
        async def get_items(): ...
    """

    items: Sequence[T] = Field(description="List of items in the current page")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Number of items per page")

    @classmethod
    def from_page(cls, page_obj: Page[T]) -> PagedResponse[T]:
        """Create a PagedResponse from a Page dataclass."""
        return cls(
            items=page_obj.items,
            total=page_obj.total,
            page=page_obj.page,
            limit=page_obj.limit,
        )


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> PageParams:
    """FastAPI dependency to extract pagination parameters.

    Usage:
        def endpoint(params: PageParams = Depends(get_pagination_params)): ...
    """
    return PageParams(page=page, limit=limit)
