"""Django pagination backends: offset slicing + keyset cursor.

Offset pagination counts via ``QuerySet.count()`` then slices
(``qs[offset:offset + limit]``), which Django renders to ``LIMIT``/``OFFSET``.
Keyset pagination reuses the cross-language cursor codec and the core's portable
keyset predicate (:func:`pypaginate._core.keyset_terms`), rendering the
lexicographic ``WHERE`` to Django ``Q`` objects so cursors stay byte-compatible
with the SQLAlchemy and TS adapters. The QuerySet must carry an explicit
``order_by`` over simple field names.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar

from pypaginate import _core
from pypaginate._native import build_offset_page
from pypaginate.errors import ConfigurationError, InvalidCursorError
from pypaginate.pages import CursorPage, OffsetPage


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from pypaginate.params import CursorParams, OffsetParams


T = TypeVar("T")


def paginate_offset(queryset: QuerySet[T], params: OffsetParams) -> OffsetPage[T]:
    """Offset-paginate a QuerySet via ``count()`` + a ``LIMIT``/``OFFSET`` slice."""
    total = int(queryset.count())
    offset = params.offset
    items = list(queryset[offset : offset + params.limit])
    return build_offset_page(items, total, params)


@dataclass(frozen=True, slots=True)
class _Paging:
    """Decoded keyset paging context derived from one request."""

    order: list[tuple[str, bool]]
    backwards: bool
    has_cursor: bool


def _parse_field(field: Any) -> tuple[str, bool]:
    """Parse one ``order_by`` entry into ``(field, is_ascending)``."""
    if not isinstance(field, str):
        raise ConfigurationError("keyset pagination requires string order_by fields")
    if field.startswith("-"):
        return field[1:], False
    return field, True


def _extract_order(queryset: Any) -> list[tuple[str, bool]]:
    """Ordered ``(field, is_ascending)`` keys from the QuerySet's ``ORDER BY``."""
    fields = queryset.query.order_by or queryset.model._meta.ordering
    if not fields:
        raise ConfigurationError("QuerySet has no ordering for keyset pagination")
    return [_parse_field(field) for field in fields]


def _compare_q(field: str, op: str, value: Any) -> Any:
    """Render one ``field OP value`` comparison as a ``Q``."""
    from django.db.models import Q

    if op == "gt":
        return Q(**{f"{field}__gt": value})
    if op == "lt":
        return Q(**{f"{field}__lt": value})
    return Q(**{field: value})


def _keyset_q(order: list[tuple[str, bool]], values: tuple[Any, ...], ascending: list[bool]) -> Any:
    """OR the core's lexicographic keyset terms into one Django ``Q``."""
    from django.db.models import Q

    combined: Any = None
    for term in _core.keyset_terms(ascending):
        term_q = Q()
        for index, op in term:
            term_q &= _compare_q(order[index][0], op, values[index])
        combined = term_q if combined is None else combined | term_q
    return combined if combined is not None else Q()


def _order_strings(order: list[tuple[str, bool]], *, backwards: bool) -> list[str]:
    """``ORDER BY`` strings, with directions flipped for backward paging."""
    return [field if (asc != backwards) else f"-{field}" for field, asc in order]


def _cursor_values(row: Any, order: list[tuple[str, bool]]) -> tuple[Any, ...]:
    """Extract the ordered column values from a result row."""
    return tuple(getattr(row, field) for field, _ in order)


def _compute_cursors(
    rows: list[Any], paging: _Paging, *, has_more: bool
) -> tuple[str | None, str | None]:
    """Compute ``(next, previous)`` cursor strings from the trimmed rows."""
    if not rows:
        return None, None
    first = _core.encode_cursor(_cursor_values(rows[0], paging.order))
    last = _core.encode_cursor(_cursor_values(rows[-1], paging.order))
    if paging.backwards:
        return last, (first if has_more else None)
    if paging.has_cursor:
        return (last if has_more else None), first
    return (last if has_more else None), None


def _finalize(rows: list[Any], paging: _Paging, *, limit: int) -> CursorPage[Any]:
    """Trim the ``limit + 1`` fetch, reverse for backward paging, build the page."""
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
    if paging.backwards:
        rows.reverse()
    next_c, prev_c = _compute_cursors(rows, paging, has_more=has_more)
    return CursorPage(
        items=rows,
        limit=limit,
        has_next=next_c is not None,
        has_previous=prev_c is not None,
        next_cursor=next_c,
        previous_cursor=prev_c,
    )


def _apply_cursor(queryset: Any, paging: _Paging, cursor: str | None) -> Any:
    """Filter the QuerySet by the decoded cursor's keyset predicate."""
    if not cursor:
        return queryset
    try:
        values = _core.decode_cursor(cursor)
    except ValueError as exc:
        raise InvalidCursorError(str(exc)) from exc
    ascending = [asc != paging.backwards for _, asc in paging.order]
    return queryset.filter(_keyset_q(paging.order, values, ascending))


def paginate_keyset(queryset: QuerySet[T], params: CursorParams) -> CursorPage[T]:
    """Keyset-paginate an ordered QuerySet into a :class:`CursorPage`."""
    order = _extract_order(queryset)
    backwards = params.before is not None
    cursor = params.before or params.after
    paging = _Paging(order=order, backwards=backwards, has_cursor=bool(cursor))
    filtered = _apply_cursor(queryset, paging, cursor)
    ordered = filtered.order_by(*_order_strings(order, backwards=backwards))
    rows = list(ordered[: params.limit + 1])
    return _finalize(rows, paging, limit=params.limit)


__all__ = ["paginate_keyset", "paginate_offset"]
