"""Snapshot dataclasses for pagination results.

This module contains snapshot types for different pagination strategies:
- PaginationSnapshot: Standard offset-based pagination
- KeysetPaginationSnapshot: Cursor-based pagination with bookmarks

This file merges:
- sql/snapshots.py → PaginationSnapshot
- sql/keyset/snapshots.py → KeysetPaginationSnapshot + helpers
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeGuard, TypeVar, cast

from pypaginate.exceptions import PaginationConfigurationError


if TYPE_CHECKING:
    from sqlakeyset import Page as KeysetPage, Paging

    from .pages import KeysetPageParams, PageParams

ItemT = TypeVar("ItemT")
"""Type variable for item types in pagination snapshots."""

ParamsT = TypeVar("ParamsT", bound="PageParams")
"""Type variable for pagination parameter types bounded by PageParams."""

KeysetItemT = TypeVar("KeysetItemT", covariant=True)
"""Covariant type variable for keyset pagination item types."""

BookmarkPayload = tuple[object, ...]
"""Type alias for bookmark payloads."""


def _get_sqlakeyset() -> Any:
    """Lazily import sqlakeyset module.

    Returns:
        The sqlakeyset module.

    Raises:
        ImportError: If sqlakeyset is not installed.
    """
    try:
        import sqlakeyset
    except ImportError as e:
        raise ImportError(
            "sqlakeyset is required for keyset pagination. "
            "Install with: pip install pypaginate[sqlalchemy]"
        ) from e
    return sqlakeyset


@dataclass(frozen=True)
class PaginationSnapshot(Generic[ItemT, ParamsT]):
    """Immutable snapshot returned by the paginator.

    Attributes:
        items: Materialized items for the current page.
        total: Total number of rows matching the base query.
        params: Effective parameters used to compute the page.
    """

    items: list[ItemT]
    total: int
    params: ParamsT


@dataclass(frozen=True)
class KeysetPaginationSnapshot(Generic[KeysetItemT]):
    """Immutable snapshot produced by keyset pagination.

    Stores the materialized items alongside the original parameters and the
    serialized bookmarks required to navigate to adjacent pages.

    Attributes:
        items: Materialized list of payload items for the current page.
        params: Parameters used to compute the current page.
        next: Serialized bookmark to retrieve the next page, if available.
        previous: Serialized bookmark to retrieve the previous page, if available.
        current: Serialized bookmark pointing to the current page position.
    """

    items: list[KeysetItemT]
    params: KeysetPageParams
    next: str | None
    previous: str | None
    current: str | None


def extract_keyset_markers(
    snapshot: KeysetPaginationSnapshot[object],
) -> tuple[str | None, str | None, str | None]:
    """Extract serialized bookmarks from a snapshot.

    Args:
        snapshot: Keyset pagination snapshot.

    Returns:
        Tuple of (next, previous, current) bookmark strings.
    """
    return snapshot.next, snapshot.previous, snapshot.current


def markers_from_paging(
    paging: Paging[object],  # type: ignore[type-var]
) -> tuple[str | None, str | None, str | None]:
    """Extract serialized bookmarks from a sqlakeyset paging object.

    Args:
        paging: Runtime paging metadata produced by sqlakeyset.

    Returns:
        A tuple (next, previous, current) of serialized bookmarks.
    """
    return (
        paging.bookmark_next if paging.has_next else None,
        paging.bookmark_previous if paging.has_previous else None,
        paging.bookmark_current,
    )


def coerce_bookmark(value: str | None) -> BookmarkPayload | None:
    """Deserialize a serialized bookmark string into sqlakeyset payload.

    Args:
        value: Serialized bookmark string, or None when not provided.

    Returns:
        A tuple payload accepted by sqlakeyset, or None when input is None.

    Raises:
        PaginationConfigurationError: When the deserialized structure is invalid.
    """
    if value is None:
        return None
    sqlakeyset = _get_sqlakeyset()
    marker = sqlakeyset.unserialize_bookmark(value)
    payload = getattr(marker, "place", None)
    if not isinstance(payload, tuple):
        raise PaginationConfigurationError(
            "Invalid sqlakeyset bookmark payload",
            details={"bookmark": value},
        )
    return payload


def materialize_keyset_page(
    page: KeysetPage[ItemT],  # type: ignore[type-var]
    *,
    scalars: bool,
) -> list[ItemT]:
    """Materialize items from a sqlakeyset page.

    Args:
        page: Sqlakeyset page object to extract items from.
        scalars: When True, coerce each row to a scalar value if possible.

    Returns:
        A list of items materialized from the page iterator.
    """
    if not scalars:
        return list(page)
    converted = [_coerce_scalar_row(row) for row in page]
    return cast("list[ItemT]", converted)


def _coerce_scalar_row(row: object) -> object:
    """Coerce a row payload to a scalar when a single value is present.

    Args:
        row: Row object produced by sqlakeyset iteration.

    Returns:
        The single element when row represents a one-item sequence; the
        original row payload otherwise.
    """
    sequence = _ensure_sequence(row)
    if len(sequence) == 1:
        return sequence[0]
    return tuple(sequence)


def _ensure_sequence(row: object) -> Sequence[object]:
    """Ensure the provided row is a sequence-like object.

    Args:
        row: Row payload to validate.

    Returns:
        The row cast to a Sequence[object] when valid.

    Raises:
        PaginationConfigurationError: If the row is not a sequence.
    """
    if _is_sequence(row):
        return row
    raise PaginationConfigurationError(
        "Invalid sqlakeyset row payload",
        details={"row": repr(row)},
    )


def _is_sequence(row: object) -> TypeGuard[Sequence[object]]:
    """Return True if row is a collections.abc.Sequence.

    Args:
        row: Object to check.

    Returns:
        True if row is a sequence.
    """
    return isinstance(row, Sequence)


__all__ = [
    "BookmarkPayload",
    "KeysetPaginationSnapshot",
    "PaginationSnapshot",
    "coerce_bookmark",
    "extract_keyset_markers",
    "markers_from_paging",
    "materialize_keyset_page",
]
