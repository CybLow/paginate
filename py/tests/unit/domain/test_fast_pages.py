"""Tests for FastOffsetPage and FastCursorPage (msgspec-backed pages)."""

from __future__ import annotations

import json

import pytest


msgspec = pytest.importorskip("msgspec")

from pypaginate.domain.fast_pages import FastCursorPage, FastOffsetPage
from pypaginate.domain.pages import CursorPage, OffsetPage


# -- FastOffsetPage ----------------------------------------------------------


class TestFastOffsetPageCreation:
    def test_field_access(self) -> None:
        page = FastOffsetPage(
            items=["a", "b"],
            limit=5,
            has_next=True,
            has_previous=False,
            total=10,
            page=1,
            pages=2,
        )

        assert page.items == ["a", "b"]
        assert page.limit == 5
        assert page.has_next is True
        assert page.has_previous is False
        assert page.total == 10
        assert page.page == 1
        assert page.pages == 2

    def test_frozen_prevents_mutation(self) -> None:
        page = FastOffsetPage(
            items=[],
            limit=5,
            has_next=False,
            has_previous=False,
            total=0,
            page=1,
            pages=0,
        )

        with pytest.raises(AttributeError):
            page.total = 99  # type: ignore[misc]


class TestFastOffsetPageModelDump:
    def test_returns_dict_with_all_fields(self) -> None:
        page = FastOffsetPage(
            items=["x"],
            limit=10,
            has_next=False,
            has_previous=True,
            total=5,
            page=2,
            pages=1,
        )

        data = page.model_dump()

        assert isinstance(data, dict)
        assert data["items"] == ["x"]
        assert data["limit"] == 10
        assert data["total"] == 5
        assert data["page"] == 2
        assert data["pages"] == 1
        assert data["has_next"] is False
        assert data["has_previous"] is True


class TestFastOffsetPageModelDumpJson:
    def test_returns_valid_json_bytes(self) -> None:
        page = FastOffsetPage(
            items=[1, 2],
            limit=5,
            has_next=True,
            has_previous=False,
            total=10,
            page=1,
            pages=2,
        )

        raw = page.model_dump_json()

        assert isinstance(raw, bytes)
        parsed = json.loads(raw)
        assert parsed["items"] == [1, 2]
        assert parsed["total"] == 10


class TestFastOffsetPageCollectionProtocol:
    def test_iteration_yields_items(self) -> None:
        page = FastOffsetPage(
            items=["a", "b", "c"],
            limit=5,
            has_next=False,
            has_previous=False,
            total=3,
            page=1,
            pages=1,
        )

        assert list(page) == ["a", "b", "c"]

    def test_len_returns_item_count(self) -> None:
        page = FastOffsetPage(
            items=["a", "b"],
            limit=5,
            has_next=False,
            has_previous=False,
            total=2,
            page=1,
            pages=1,
        )

        assert len(page) == 2

    def test_getitem_returns_item_by_index(self) -> None:
        page = FastOffsetPage(
            items=["x", "y", "z"],
            limit=5,
            has_next=False,
            has_previous=False,
            total=3,
            page=1,
            pages=1,
        )

        assert page[0] == "x"
        assert page[2] == "z"


class TestFastOffsetPageToPydantic:
    def test_converts_to_offset_page(self) -> None:
        page = FastOffsetPage(
            items=["a"],
            limit=5,
            has_next=False,
            has_previous=False,
            total=1,
            page=1,
            pages=1,
        )

        pydantic_page = page.to_pydantic()

        assert isinstance(pydantic_page, OffsetPage)
        assert pydantic_page.items == ["a"]
        assert pydantic_page.total == 1
        assert pydantic_page.page == 1
        assert pydantic_page.pages == 1


# -- FastCursorPage ----------------------------------------------------------


class TestFastCursorPageCreation:
    def test_field_access_with_cursors(self) -> None:
        page = FastCursorPage(
            items=["a", "b"],
            limit=5,
            has_next=True,
            has_previous=True,
            next_cursor="abc",
            previous_cursor="xyz",
        )

        assert page.items == ["a", "b"]
        assert page.limit == 5
        assert page.has_next is True
        assert page.has_previous is True
        assert page.next_cursor == "abc"
        assert page.previous_cursor == "xyz"

    def test_field_access_without_cursors(self) -> None:
        page = FastCursorPage(
            items=[],
            limit=10,
            has_next=False,
            has_previous=False,
            next_cursor=None,
            previous_cursor=None,
        )

        assert page.next_cursor is None
        assert page.previous_cursor is None

    def test_frozen_prevents_mutation(self) -> None:
        page = FastCursorPage(
            items=[],
            limit=5,
            has_next=False,
            has_previous=False,
            next_cursor=None,
            previous_cursor=None,
        )

        with pytest.raises(AttributeError):
            page.limit = 99  # type: ignore[misc]


class TestFastCursorPageModelDump:
    def test_returns_dict_with_all_fields(self) -> None:
        page = FastCursorPage(
            items=["x"],
            limit=10,
            has_next=True,
            has_previous=False,
            next_cursor="cur_next",
            previous_cursor=None,
        )

        data = page.model_dump()

        assert isinstance(data, dict)
        assert data["items"] == ["x"]
        assert data["limit"] == 10
        assert data["has_next"] is True
        assert data["has_previous"] is False
        assert data["next_cursor"] == "cur_next"
        assert data["previous_cursor"] is None


class TestFastCursorPageModelDumpJson:
    def test_returns_valid_json_bytes(self) -> None:
        page = FastCursorPage(
            items=[1, 2, 3],
            limit=5,
            has_next=True,
            has_previous=False,
            next_cursor="nxt",
            previous_cursor=None,
        )

        raw = page.model_dump_json()

        assert isinstance(raw, bytes)
        parsed = json.loads(raw)
        assert parsed["items"] == [1, 2, 3]
        assert parsed["next_cursor"] == "nxt"
        assert parsed["previous_cursor"] is None


class TestFastCursorPageCollectionProtocol:
    def test_iteration_yields_items(self) -> None:
        page = FastCursorPage(
            items=["a", "b"],
            limit=5,
            has_next=False,
            has_previous=False,
            next_cursor=None,
            previous_cursor=None,
        )

        assert list(page) == ["a", "b"]

    def test_len_returns_item_count(self) -> None:
        page = FastCursorPage(
            items=["a", "b", "c"],
            limit=5,
            has_next=False,
            has_previous=False,
            next_cursor=None,
            previous_cursor=None,
        )

        assert len(page) == 3

    def test_getitem_returns_item_by_index(self) -> None:
        page = FastCursorPage(
            items=["x", "y"],
            limit=5,
            has_next=False,
            has_previous=False,
            next_cursor=None,
            previous_cursor=None,
        )

        assert page[0] == "x"
        assert page[1] == "y"


class TestFastCursorPageToPydantic:
    def test_converts_to_cursor_page(self) -> None:
        page = FastCursorPage(
            items=["a"],
            limit=5,
            has_next=True,
            has_previous=False,
            next_cursor="abc",
            previous_cursor=None,
        )

        pydantic_page = page.to_pydantic()

        assert isinstance(pydantic_page, CursorPage)
        assert pydantic_page.items == ["a"]
        assert pydantic_page.next_cursor == "abc"
        assert pydantic_page.has_next is True
