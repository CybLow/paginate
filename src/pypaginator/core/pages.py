"""Public dataclasses for pagination parameters and results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, SupportsInt, TypeVar

from pypaginator.exceptions import PaginationConfigurationError

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

ItemT = TypeVar("ItemT")
"""Generic type variable for paginated item types."""

UpdateValue = int | SupportsInt | str
"""Type alias for values accepted in PageParams.model_copy updates."""


@dataclass(frozen=True, slots=True)
class PageParams:
    """Immutable pagination parameters with validation helpers.

    This is a concrete dataclass, not a Protocol. It provides nominal typing
    guarantees and clear return types for all operations.
    """

    page: int = 1
    limit: int = 20

    def __post_init__(self) -> None:
        """Validate that page and limit are positive integers.

        Raises:
            PaginationConfigurationError: If page or limit < 1.
        """
        _ensure_positive("page", self.page)
        _ensure_positive("limit", self.limit)

    @property
    def offset(self) -> int:
        """Calculate the offset based on page and limit.

        Returns:
            The calculated offset for database queries.
        """
        return (self.page - 1) * self.limit

    def model_copy(
        self,
        *,
        update: Mapping[str, UpdateValue] | None = None,
        deep: bool = False,
    ) -> PageParams:
        """Create a copy with optional field updates.

        Args:
            update: Dictionary of fields to update in the copy.
            deep: Unused parameter kept for compatibility.

        Returns:
            New PageParams instance with updated fields.
        """
        data = {"page": self.page, "limit": self.limit}
        if update:
            data |= _coerce_updates(update)
        _ = deep  # Unused: PageParams has no nested structures requiring deep copy
        return PageParams(**data)


@dataclass(frozen=True, slots=True)
class Page(Generic[ItemT]):
    """Dataclass representing a paginated result set.

    This is a concrete generic dataclass, not a Protocol. It provides
    nominal typing and clear return types.
    """

    items: Sequence[ItemT]
    total: int
    page: int
    limit: int

    @classmethod
    def create(
        cls,
        items: Sequence[ItemT],
        total: int,
        params: PageParams,
    ) -> Page[ItemT]:
        """Factory method to create a Page from items and params.

        Args:
            items: Items for this page.
            total: Total number of items across all pages.
            params: Page parameters used.

        Returns:
            A new Page instance.
        """
        return cls(list(items), total, params.page, params.limit)

    @property
    def pages(self) -> int:
        """Calculate total number of pages.

        Returns:
            Total number of pages.
        """
        if self.limit <= 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @property
    def has_next(self) -> bool:
        """Check if there is a next page.

        Returns:
            True if there are more pages after this one.
        """
        return self.page < self.pages

    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page.

        Returns:
            True if there are pages before this one.
        """
        return self.page > 1


@dataclass(frozen=True, slots=True)
class KeysetPageParams:
    """Parameters for keyset-based pagination using bookmarks."""

    limit: int = 20
    after: str | None = None
    before: str | None = None
    page: str | None = None

    def __post_init__(self) -> None:
        """Validate exclusivity of bookmark selectors and positive limit.

        Raises:
            PaginationConfigurationError: If multiple bookmarks provided
                or limit < 1.
        """
        _ensure_positive("limit", self.limit)
        selectors = [self.after, self.before, self.page]
        if sum(value is not None for value in selectors) > 1:
            raise PaginationConfigurationError(
                "only one of 'after', 'before' or 'page' can be provided",
                details={"after": self.after, "before": self.before, "page": self.page},
            )


def _ensure_positive(name: str, value: int) -> None:
    """Raise when value is not strictly positive.

    Args:
        name: Parameter name for error message.
        value: Value to validate.

    Raises:
        PaginationConfigurationError: If value < 1.
    """
    if value < 1:
        raise PaginationConfigurationError(
            f"{name} must be greater than or equal to 1",
            details={name: value},
        )


def _coerce_updates(update: Mapping[str, UpdateValue]) -> dict[str, int]:
    """Coerce update mapping to integer fields for PageParams.

    Args:
        update: Mapping of field updates.

    Returns:
        Dictionary with integer values.
    """
    coerced: dict[str, int] = {}
    for key, value in update.items():
        coerced[key] = int(value)
    return coerced


__all__ = ["PageParams", "Page", "KeysetPageParams"]
