"""Mock objects and stubs for unit testing.

This module provides mock implementations and stubs for testing
components in isolation without real dependencies.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar


T = TypeVar("T")


@dataclass
class MockAsyncSession:
    """Mock async database session for unit tests.

    This mock records all method calls for verification without
    actually connecting to a database.
    """

    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = field(default_factory=list)
    _results: dict[str, Any] = field(default_factory=dict)

    def set_result(self, method: str, result: Any) -> None:
        """Set the return value for a method.

        Args:
            method: The method name.
            result: The value to return when the method is called.
        """
        self._results[method] = result

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Mock execute method."""
        self.calls.append(("execute", args, kwargs))
        return self._results.get("execute")

    async def commit(self) -> None:
        """Mock commit method."""
        self.calls.append(("commit", (), {}))

    async def rollback(self) -> None:
        """Mock rollback method."""
        self.calls.append(("rollback", (), {}))

    def add(self, instance: Any) -> None:
        """Mock add method."""
        self.calls.append(("add", (instance,), {}))

    def add_all(self, instances: list[Any]) -> None:
        """Mock add_all method."""
        self.calls.append(("add_all", (instances,), {}))


@dataclass
class MockResult(Generic[T]):
    """Mock database result for testing.

    Attributes:
        items: The items to return from the result.
        count: The count to return for count queries.
    """

    items: list[T] = field(default_factory=list)
    count: int = 0

    def scalars(self) -> "MockResult[T]":
        """Return self for chaining."""
        return self

    def unique(self) -> "MockResult[T]":
        """Return self for chaining."""
        return self

    def all(self) -> list[T]:
        """Return the items."""
        return self.items

    def scalar(self) -> int:
        """Return the count."""
        return self.count


@dataclass
class MockPaginator(Generic[T]):
    """Mock paginator for unit testing.

    This allows testing pagination logic without a real engine.
    """

    items: list[T] = field(default_factory=list)
    total: int = 0

    def paginate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Mock paginate method."""
        return {
            "items": self.items,
            "total": self.total,
            "page": kwargs.get("page", 1),
            "limit": kwargs.get("limit", 10),
        }


class MockFieldAccessor:
    """Mock field accessor for testing predicates."""

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """Initialize with optional data.

        Args:
            data: Dictionary of field values to return.
        """
        self._data = data or {}

    def get(self, obj: Any, field: str) -> Any:
        """Get a field value.

        Args:
            obj: The object (ignored, uses internal data).
            field: The field name.

        Returns:
            The field value or None.
        """
        return self._data.get(field)


def create_mock_predicate(return_value: bool) -> Callable[[Any], bool]:
    """Create a mock predicate that always returns the given value.

    Args:
        return_value: The value the predicate should return.

    Returns:
        A predicate function.
    """
    def predicate(item: Any) -> bool:
        return return_value
    return predicate


def create_counting_predicate() -> tuple[Callable[[Any], bool], Callable[[], int]]:
    """Create a predicate that counts how many times it was called.

    Returns:
        A tuple of (predicate, get_count_function).
    """
    count = [0]  # Use list for mutability in closure

    def predicate(item: Any) -> bool:
        count[0] += 1
        return True

    def get_count() -> int:
        return count[0]

    return predicate, get_count


__all__ = [
    "MockAsyncSession",
    "MockFieldAccessor",
    "MockPaginator",
    "MockResult",
    "create_counting_predicate",
    "create_mock_predicate",
]
