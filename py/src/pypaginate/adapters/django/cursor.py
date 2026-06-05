"""Cursor/keyset pagination backend for Django QuerySets (sync).

Reuses the cross-language cursor codec and the core's portable keyset predicate
(``_core.keyset_terms``): the lexicographic WHERE is rendered to Django ``Q``
objects here, so cursors are byte-compatible with the SQLAlchemy backend and the
JS adapters. The QuerySet must carry an explicit ``order_by`` over simple field
names.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pypaginate._core import keyset_terms
from pypaginate.domain.exceptions import ConfigurationError
from pypaginate.engine.cursor_codec import decode_cursor, encode_cursor


ItemT = TypeVar("ItemT")


if TYPE_CHECKING:
    from django.db.models import QuerySet


# -- order extraction --------------------------------------------------------


def _parse_field(field: Any) -> tuple[str, bool]:
    """Parse one ``order_by`` entry into ``(field, is_ascending)``."""
    if not isinstance(field, str):
        msg = "keyset pagination requires string order_by fields"
        raise ConfigurationError(msg)
    if field.startswith("-"):
        return field[1:], False
    return field, True


def _extract_order(qs: Any) -> list[tuple[str, bool]]:
    """Ordered ``(field, is_ascending)`` keys from the QuerySet's ORDER BY."""
    fields = qs.query.order_by or qs.model._meta.ordering
    if not fields:
        msg = "QuerySet has no ordering for keyset pagination"
        raise ConfigurationError(msg)
    return [_parse_field(field) for field in fields]


# -- keyset WHERE (rendered from the core predicate) -------------------------


def _compare_q(field: str, op: str, value: Any) -> Any:
    """Render one ``field OP value`` comparison as a ``Q``."""
    from django.db.models import Q

    if op == "gt":
        return Q(**{f"{field}__gt": value})
    if op == "lt":
        return Q(**{f"{field}__lt": value})
    return Q(**{field: value})


def _keyset_q(order: list[tuple[str, bool]], values: tuple[Any, ...], ascending: list[bool]) -> Any:
    """OR the core's keyset terms into one Django ``Q``."""
    from django.db.models import Q

    combined: Any | None = None
    for term in keyset_terms(ascending):
        term_q = Q()
        for index, op in term:
            term_q &= _compare_q(order[index][0], op, values[index])
        combined = term_q if combined is None else combined | term_q
    return combined if combined is not None else Q()


def _order_strings(order: list[tuple[str, bool]], *, backwards: bool) -> list[str]:
    """ORDER BY field strings, with directions flipped for backward paging."""
    return [field if (asc != backwards) else f"-{field}" for field, asc in order]


def _cursor_values(row: Any, order: list[tuple[str, bool]]) -> tuple[Any, ...]:
    """Extract the ORDER BY column values from a result row."""
    return tuple(getattr(row, field) for field, _ in order)


# -- page assembly -----------------------------------------------------------


def _compute_cursors(
    rows: list[Any],
    order: list[tuple[str, bool]],
    *,
    has_more: bool,
    backwards: bool,
    has_cursor: bool,
) -> tuple[str | None, str | None]:
    """Compute (next, prev) cursor strings from the trimmed result rows."""
    if not rows:
        return None, None
    first = encode_cursor(_cursor_values(rows[0], order))
    last = encode_cursor(_cursor_values(rows[-1], order))
    if backwards:
        return last, (first if has_more else None)
    if has_cursor:
        return (last if has_more else None), first
    return (last if has_more else None), None


def _finalize(
    rows: list[Any],
    order: list[tuple[str, bool]],
    *,
    limit: int,
    backwards: bool,
    has_cursor: bool,
) -> tuple[list[Any], str | None, str | None]:
    """Trim the limit+1 fetch, reverse for backward paging, compute cursors."""
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
    if backwards:
        rows.reverse()
    next_c, prev_c = _compute_cursors(
        rows, order, has_more=has_more, backwards=backwards, has_cursor=has_cursor
    )
    return rows, next_c, prev_c


def _apply_cursor(
    qs: Any, order: list[tuple[str, bool]], cursor: str | None, *, backwards: bool
) -> Any:
    """Filter the QuerySet by the decoded cursor's keyset predicate."""
    if not cursor:
        return qs
    values = decode_cursor(cursor)
    ascending = [asc != backwards for _, asc in order]
    return qs.filter(_keyset_q(order, values, ascending))


class DjangoCursorBackend(Generic[ItemT]):
    """Sync cursor/keyset pagination backend for Django QuerySets."""

    __slots__ = ()

    def fetch_page(
        self,
        query: object,
        *,
        limit: int,
        after: str | None = None,
        before: str | None = None,
    ) -> tuple[list[ItemT], str | None, str | None]:
        """Fetch a keyset page: ``(items, next_cursor, prev_cursor)``."""
        qs: QuerySet[ItemT] = query  # type: ignore[assignment]
        order = _extract_order(qs)
        backwards = before is not None
        cursor = before or after
        qs = _apply_cursor(qs, order, cursor, backwards=backwards)
        qs = qs.order_by(*_order_strings(order, backwards=backwards))
        rows = list(qs[: limit + 1])
        return _finalize(rows, order, limit=limit, backwards=backwards, has_cursor=bool(cursor))


__all__ = ["DjangoCursorBackend"]
