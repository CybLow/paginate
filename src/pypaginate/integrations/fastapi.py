"""FastAPI integration for pypaginate.

This module provides FastAPI-specific utilities for pagination.
Install with: pip install pypaginate[fastapi]
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar


try:
    from fastapi import Query
    from pydantic import BaseModel, ConfigDict, Field
except ImportError as e:
    raise ImportError(
        "FastAPI integration requires fastapi and pydantic. "
        "Install with: pip install pypaginate[fastapi]"
    ) from e

from ..core.pages import Page, PageParams


if TYPE_CHECKING:
    pass


T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    """Pydantic model for paginated responses.

    Wraps the Page dataclass to ensure correct OpenAPI schema generation.

    Example:
        ```python
        @app.get("/items", response_model=PagedResponse[ItemSchema])
        async def get_items(): ...
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: Any = Field(description="List of items in the current page")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Number of items per page")

    @classmethod
    def from_page(cls, page_obj: Page[T]) -> PagedResponse[T]:
        """Create a PagedResponse from a Page dataclass.

        Args:
            page_obj: Page dataclass to convert.

        Returns:
            PagedResponse instance with the same data.
        """
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

    Example:
        ```python
        @app.get("/items")
        def endpoint(params: PageParams = Depends(get_pagination_params)): ...
        ```

    Args:
        page: Page number from query parameter (default 1).
        limit: Items per page from query parameter (default 20, max 100).

    Returns:
        PageParams instance with the provided values.
    """
    return PageParams(page=page, limit=limit)


__all__ = [
    "PagedResponse",
    "get_pagination_params",
]
