"""Core protocols for pagination structural typing.

This module defines Protocol types for external interfaces and duck typing:
- PageParamsProtocol: Protocol for pagination parameters
- PageProtocol: Protocol for pagination results
- SqlClause, SqlStringExpression: Abstract SQLAlchemy types
- SupportsTotalOrdering: Generic comparison protocol

Concrete types (PageParams, Page) are defined in pages.py and implement these protocols.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


@runtime_checkable
class PageParamsProtocol(Protocol):
    """Protocol for pagination parameters.

    Any type implementing this protocol can be used for pagination operations.
    The concrete implementation is PageParams in pages.py.
    """

    page: int
    limit: int

    @property
    def offset(self) -> int:
        """Calculate the offset based on page and limit."""
        ...

    def model_copy(
        self,
        *,
        update: Mapping[str, int] | None = None,
        deep: bool = False,
    ) -> PageParamsProtocol:
        """Create a copy with optional field updates."""
        ...


@runtime_checkable
class PageProtocol(Protocol):
    """Protocol for pagination results.

    Any type implementing this protocol can represent a page of results.
    The concrete implementation is Page in pages.py.
    """

    items: Sequence[object]
    total: int
    page: int
    limit: int


@runtime_checkable
class SupportsTotalOrdering(Protocol):
    """Protocol for types supporting total ordering comparisons.

    Used for generic ordering operators in filtering.
    """

    def __lt__(self, _other: object, /) -> bool:
        """Less than comparison.

        Args:
            _other: Object to compare with.

        Returns:
            True if self is less than other.
        """
        ...

    def __le__(self, _other: object, /) -> bool:
        """Less than or equal comparison.

        Args:
            _other: Object to compare with.

        Returns:
            True if self is less than or equal to other.
        """
        ...

    def __gt__(self, _other: object, /) -> bool:
        """Greater than comparison.

        Args:
            _other: Object to compare with.

        Returns:
            True if self is greater than other.
        """
        ...

    def __ge__(self, _other: object, /) -> bool:
        """Greater than or equal comparison.

        Args:
            _other: Object to compare with.

        Returns:
            True if self is greater than or equal to other.
        """
        ...


@runtime_checkable
class SqlClause(Protocol):
    """Structural protocol abstracting SQLAlchemy boolean expressions.

    This Protocol is legitimate because it abstracts a third-party library
    (SQLAlchemy) without requiring direct dependency in type signatures.
    """

    def __and__(self, other: SqlClause, /) -> SqlClause:
        """Logical AND operation.

        Args:
            other: Clause to combine with.

        Returns:
            Combined clause using AND logic.
        """
        ...

    def __or__(self, other: SqlClause, /) -> SqlClause:
        """Logical OR operation.

        Args:
            other: Clause to combine with.

        Returns:
            Combined clause using OR logic.
        """
        ...


@runtime_checkable
class SqlStringExpression(Protocol):
    """Structural protocol abstracting SQLAlchemy string column operations.

    This Protocol is legitimate because it abstracts a third-party library
    (SQLAlchemy) without requiring direct dependency in type signatures.
    """

    def in_(self, values: Sequence[str], /) -> SqlClause:
        """SQL IN operator for string values.

        Args:
            values: Sequence of string values to check membership.

        Returns:
            SQL clause checking membership.
        """
        ...

    def like(self, pattern: str, /, *, escape: str) -> SqlClause:
        """SQL LIKE operator with escape character.

        Args:
            pattern: LIKE pattern with wildcards.
            escape: Escape character for wildcards.

        Returns:
            SQL clause applying LIKE pattern matching.
        """
        ...


__all__ = [
    "PageParamsProtocol",
    "PageProtocol",
    "SqlClause",
    "SqlStringExpression",
    "SupportsTotalOrdering",
]
