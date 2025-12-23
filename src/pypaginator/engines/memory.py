"""In-memory pagination engine.

This module provides pagination for in-memory data with support for:
- Sequence slicing for efficient pagination
- Streaming iterables with filtering
- Predicate-based filtering

Classes
-------
MemoryPaginator
    Paginate sequences or iterables while preserving streaming semantics.

Functions
---------
filter_iter
    Yield items that satisfy an optional predicate.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import tee
from typing import Generic, TypeVar

from ..core import Page, PageParams, clamp_page_params


T = TypeVar("T")
"""Generic type variable for item types in memory pagination."""


def filter_iter(
    items: Iterable[T], predicate: Callable[[T], bool] | None
) -> Iterator[T]:
    """Yield items that satisfy an optional predicate.

    Args:
        items: Iterable of items to iterate over.
        predicate: Optional predicate applied to each item.

    Returns:
        An iterator yielding items for which ``predicate(item)`` is ``True``.
        When ``predicate`` is ``None``, yields all items.
    """
    for item in items:
        if predicate is None or predicate(item):
            yield item


@dataclass(frozen=True)
class SliceBounds:
    """Represent the half-open slice collected for a page.

    Attributes:
        start: Starting offset for the slice.
        end: Ending offset for the slice (exclusive).
    """

    start: int
    end: int


def compute_bounds(params: PageParams) -> SliceBounds:
    """Compute the start/end offsets for the requested page.

    Args:
        params: Page parameters with page number and limit.

    Returns:
        SliceBounds with start and end offsets.
    """
    start = params.offset
    return SliceBounds(start=start, end=start + params.limit)


def collect_window(items: Iterator[T], bounds: SliceBounds) -> tuple[list[T], int]:
    """Collect items falling within the provided bounds and return the total size.

    Args:
        items: Iterator of items to collect from.
        bounds: Slice bounds defining the window.

    Returns:
        Tuple of (collected_items, total_count).
    """
    collected: list[T] = []
    total = 0
    for element in items:
        if bounds.start <= total < bounds.end:
            collected.append(element)
        total += 1
    return collected, total


class MemoryPaginator(Generic[T]):
    """Paginate sequences or iterables while preserving streaming semantics."""

    def __init__(self, *, clamp: bool = False) -> None:
        """Initialize the memory paginator.

        Args:
            clamp: Whether to clamp page parameters to valid bounds.
        """
        self._clamp = clamp

    def paginate(
        self,
        items: Iterable[T],
        params: PageParams,
        predicate: Callable[[T], bool] | None = None,
    ) -> Page[T]:
        """Paginate a sequence or iterable.

        Args:
            items: Iterable of items to paginate.
            params: Page parameters.
            predicate: Optional filter predicate.

        Returns:
            A Page object with the requested window.
        """
        if predicate is None and isinstance(items, Sequence):
            return self._paginate_sequence(items, params)
        return self._paginate_stream(items, params, predicate)

    def _paginate_sequence(self, items: Sequence[T], params: PageParams) -> Page[T]:
        """Paginate a sequence using efficient slicing.

        Args:
            items: Sequence to paginate.
            params: Page parameters.

        Returns:
            A Page object.
        """
        total = len(items)
        effective = clamp_page_params(total, params) if self._clamp else params
        bounds = compute_bounds(effective)
        window = list(items[bounds.start : bounds.end])
        return Page.create(window, total, effective)

    def _paginate_stream(
        self,
        items: Iterable[T],
        params: PageParams,
        predicate: Callable[[T], bool] | None,
    ) -> Page[T]:
        """Paginate an iterable stream with optional filtering.

        Args:
            items: Iterable to paginate.
            params: Page parameters.
            predicate: Optional filter predicate.

        Returns:
            A Page object.
        """
        filtered = filter_iter(items, predicate)
        if not self._clamp:
            return self._build_page(filtered, params)
        return self._paginate_clamped(filtered, params)

    @staticmethod
    def _build_page(items: Iterator[T], params: PageParams) -> Page[T]:
        """Build a page from an iterator.

        Args:
            items: Iterator of items.
            params: Page parameters.

        Returns:
            A Page object.
        """
        bounds = compute_bounds(params)
        window, total = collect_window(items, bounds)
        return Page.create(window, total, params)

    def _paginate_clamped(self, items: Iterator[T], params: PageParams) -> Page[T]:
        """Paginate with clamping enabled.

        Args:
            items: Iterator of items.
            params: Page parameters.

        Returns:
            A Page object with clamped parameters.
        """
        first, second = tee(items, 2)
        page = self._build_page(first, params)
        effective = clamp_page_params(page.total, params)
        return page if effective == params else self._build_page(second, effective)


__all__ = [
    "MemoryPaginator",
    "SliceBounds",
    "collect_window",
    "compute_bounds",
    "filter_iter",
]
