"""End-to-end tests for the Django adapter against in-memory sqlite."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest


pytest.importorskip("django")

from django.db import connection, models

from pypaginate.adapters.django import (
    DjangoBackend,
    DjangoCursorBackend,
    DjangoFilterBackend,
    DjangoSearchBackend,
    DjangoSortBackend,
)
from pypaginate.domain.enums import SortDirection
from pypaginate.domain.specs import FilterSpec, SearchSpec, SortSpec


class Article(models.Model):
    """Throwaway model — not part of any installed app."""

    title = models.CharField(max_length=100)
    views = models.IntegerField()

    class Meta:
        app_label = "pypaginate_django_test"


@pytest.fixture(scope="module", autouse=True)
def _seeded() -> Iterator[None]:
    """Create the table once and seed 10 rows (views 1..10)."""
    with connection.schema_editor() as editor:
        editor.create_model(Article)
    Article.objects.bulk_create([Article(title=f"post {i}", views=i) for i in range(1, 11)])
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(Article)


def test_offset_backend_counts_and_slices() -> None:
    backend: DjangoBackend[Any] = DjangoBackend()
    assert backend.count(Article.objects.all()) == 10
    rows = backend.fetch(Article.objects.order_by("views"), 0, 3)
    assert [r.views for r in rows] == [1, 2, 3]


def test_filter_backend_translates_to_q() -> None:
    qs = DjangoFilterBackend.apply_filters(
        Article.objects.all(), [FilterSpec(field="views", operator="gte", value=5)]
    )
    assert qs.count() == 6  # views 5..10


def test_filter_backend_or_logic() -> None:
    from pypaginate.domain.enums import FilterLogic

    specs = [
        FilterSpec(field="views", operator="lt", value=2, logic=FilterLogic.OR),
        FilterSpec(field="views", operator="gt", value=9, logic=FilterLogic.OR),
    ]
    qs = DjangoFilterBackend.apply_filters(Article.objects.all(), specs)
    assert sorted(r.views for r in qs) == [1, 10]


def test_sort_backend_orders_descending() -> None:
    qs = DjangoSortBackend.apply_sorting(
        Article.objects.all(), [SortSpec(field="views", direction=SortDirection.DESC)]
    )
    assert [r.views for r in qs[:3]] == [10, 9, 8]


def test_search_backend_match_filters() -> None:
    qs = DjangoSearchBackend.apply_search(
        Article.objects.all(), SearchSpec(query="post 1", fields=("title",))
    )
    # "post 1" is a substring of "post 1" and "post 10".
    assert sorted(r.views for r in qs) == [1, 10]


def test_cursor_backend_pages_forward() -> None:
    backend: DjangoCursorBackend[Any] = DjangoCursorBackend()
    qs = Article.objects.order_by("views")

    items, next_cursor, prev_cursor = backend.fetch_page(qs, limit=3)
    assert [i.views for i in items] == [1, 2, 3]
    assert next_cursor is not None
    assert prev_cursor is None

    items2, _, prev2 = backend.fetch_page(qs, limit=3, after=next_cursor)
    assert [i.views for i in items2] == [4, 5, 6]
    assert prev2 is not None


def test_cursor_backend_pages_backward() -> None:
    backend: DjangoCursorBackend[Any] = DjangoCursorBackend()
    qs = Article.objects.order_by("views")

    first, next_cursor, _ = backend.fetch_page(qs, limit=3)
    _, _, prev2 = backend.fetch_page(qs, limit=3, after=next_cursor)
    # Navigate back from page 2 -> should return page 1's rows in order.
    back, _, _ = backend.fetch_page(qs, limit=3, before=prev2)
    assert [i.views for i in back] == [i.views for i in first]


def test_cursor_backend_requires_ordering() -> None:
    from pypaginate.domain.exceptions import ConfigurationError

    backend: DjangoCursorBackend[Any] = DjangoCursorBackend()
    with pytest.raises(ConfigurationError):
        backend.fetch_page(Article.objects.all(), limit=3)
