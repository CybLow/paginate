"""Django adapter integration tests against in-memory SQLite.

Configures Django with a throwaway ``:memory:`` database, defines a model with an
explicit ``app_label``, creates its table via ``schema_editor``, seeds rows, then
exercises the adapter's public surface: ``build_filter_q`` / ``apply_filters``
(operators + And/Or groups), ``build_order_by`` / ``apply_sorting`` (asc/desc +
nulls), ``paginate_offset``, and a ``paginate_keyset`` round-trip.

There is no registered ``django`` pytest marker, so these tests are marked only
``integration``.
"""

from __future__ import annotations

from collections.abc import Iterator

import django
import pytest
from django.conf import settings


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
    )
    django.setup()


from django.db import connection, models

from pypaginate import CursorParams, OffsetParams
from pypaginate.adapters.django import (
    apply_filters,
    apply_sorting,
    build_filter_q,
    build_order_by,
    paginate_keyset,
    paginate_offset,
)
from pypaginate.specs import And, FilterSpec, Or, SortSpec


pytestmark = pytest.mark.integration


class Widget(models.Model):
    """A minimal model with a nullable ``tag`` for null-aware tests."""

    name = models.CharField(max_length=50)
    price = models.IntegerField()
    tag = models.CharField(max_length=50, null=True)

    class Meta:
        app_label = "pypaginate_django_test"


# name, price, tag
_ROWS: list[tuple[str, int, str | None]] = [
    ("Alpha", 10, "x"),
    ("Beta", 20, None),
    ("Gamma", 30, "y"),
    ("Delta", 40, None),
]


@pytest.fixture(scope="module", autouse=True)
def _schema() -> Iterator[None]:
    """Create the ``Widget`` table and seed rows for the whole module."""
    with connection.schema_editor() as editor:
        editor.create_model(Widget)
    Widget.objects.bulk_create(Widget(name=n, price=p, tag=t) for n, p, t in _ROWS)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(Widget)


def _names(queryset: object) -> list[str]:
    """Names of the rows in a queryset, ordered by name for stable assertions."""
    return list(queryset.order_by("name").values_list("name", flat=True))  # type: ignore[attr-defined]


def test_build_filter_q_eq() -> None:
    condition = build_filter_q([FilterSpec(field="name", operator="eq", value="Alpha")])

    assert _names(Widget.objects.filter(condition)) == ["Alpha"]


def test_build_filter_q_in() -> None:
    condition = build_filter_q([FilterSpec(field="name", operator="in", value=["Alpha", "Beta"])])

    assert _names(Widget.objects.filter(condition)) == ["Alpha", "Beta"]


def test_build_filter_q_not_in() -> None:
    condition = build_filter_q(
        [FilterSpec(field="name", operator="not_in", value=["Alpha", "Beta"])]
    )

    assert _names(Widget.objects.filter(condition)) == ["Delta", "Gamma"]


def test_build_filter_q_between() -> None:
    condition = build_filter_q([FilterSpec(field="price", operator="between", value=[20, 30])])

    assert _names(Widget.objects.filter(condition)) == ["Beta", "Gamma"]


def test_build_filter_q_is_null() -> None:
    condition = build_filter_q([FilterSpec(field="tag", operator="is_null", value=None)])

    assert _names(Widget.objects.filter(condition)) == ["Beta", "Delta"]


def test_build_filter_q_contains() -> None:
    condition = build_filter_q([FilterSpec(field="name", operator="contains", value="lph")])

    assert _names(Widget.objects.filter(condition)) == ["Alpha"]


def test_build_filter_q_unsupported_operator_raises() -> None:
    from pypaginate.errors import FilterError

    with pytest.raises(FilterError):
        build_filter_q([FilterSpec(field="tag", operator="empty", value=None)])


def test_apply_filters_group_and() -> None:
    group = And(
        FilterSpec(field="price", operator="gte", value=20),
        FilterSpec(field="tag", operator="is_not_null", value=None),
    )

    result = apply_filters(Widget.objects.all(), group)

    assert _names(result) == ["Gamma"]


def test_apply_filters_group_or() -> None:
    group = Or(
        FilterSpec(field="name", operator="eq", value="Alpha"),
        FilterSpec(field="name", operator="eq", value="Beta"),
    )

    result = apply_filters(Widget.objects.all(), group)

    assert _names(result) == ["Alpha", "Beta"]


def test_apply_filters_empty_is_noop() -> None:
    result = apply_filters(Widget.objects.all(), [])

    assert result.count() == 4


def test_build_order_by_plain_strings() -> None:
    assert build_order_by([SortSpec(field="price", direction="desc")]) == ["-price"]
    assert build_order_by([SortSpec(field="name", direction="asc")]) == ["name"]


def test_build_order_by_nulls_is_expression() -> None:
    clauses = build_order_by([SortSpec(field="tag", direction="asc", nulls="first")])

    assert len(clauses) == 1
    assert not isinstance(clauses[0], str)


def test_apply_sorting_desc() -> None:
    result = apply_sorting(Widget.objects.all(), [SortSpec(field="price", direction="desc")])

    assert list(result.values_list("name", flat=True)) == ["Delta", "Gamma", "Beta", "Alpha"]


def test_apply_sorting_nulls_first() -> None:
    result = apply_sorting(
        Widget.objects.all(), [SortSpec(field="tag", direction="asc", nulls="first")]
    )

    names = list(result.values_list("name", flat=True))

    assert set(names[:2]) == {"Beta", "Delta"}  # nulls lead
    assert names[2:] == ["Alpha", "Gamma"]  # then "x", "y"


def test_paginate_offset_first_page() -> None:
    queryset = Widget.objects.all().order_by("price")

    page = paginate_offset(queryset, OffsetParams(page=1, limit=2))

    assert [w.name for w in page.items] == ["Alpha", "Beta"]
    assert page.total == 4
    assert page.pages == 2
    assert page.has_next is True
    assert page.has_previous is False


def test_paginate_offset_last_page() -> None:
    queryset = Widget.objects.all().order_by("price")

    page = paginate_offset(queryset, OffsetParams(page=2, limit=2))

    assert [w.name for w in page.items] == ["Gamma", "Delta"]
    assert page.has_next is False
    assert page.has_previous is True


def test_paginate_keyset_round_trip() -> None:
    queryset = Widget.objects.all().order_by("id")

    first = paginate_keyset(queryset, CursorParams(limit=2))
    assert [w.name for w in first.items] == ["Alpha", "Beta"]
    assert first.has_next is True
    assert first.next_cursor is not None

    second = paginate_keyset(queryset, CursorParams(limit=2, after=first.next_cursor))
    assert [w.name for w in second.items] == ["Gamma", "Delta"]
    assert second.previous_cursor is not None

    back = paginate_keyset(queryset, CursorParams(limit=2, before=second.previous_cursor))
    assert [w.name for w in back.items] == ["Alpha", "Beta"]
