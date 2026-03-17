"""Tests for page and param model serialization.

Verifies model_dump serialization and model_validate round-trips
for params and page models.
"""

from __future__ import annotations

from pypaginate.domain.pages import CursorPage, OffsetPage
from pypaginate.domain.params import CursorParams, OffsetParams


class TestOffsetParamsDump:
    def test_model_dump_contains_page_and_limit(self) -> None:
        params = OffsetParams(page=2, limit=25)

        data = params.model_dump()

        assert data["page"] == 2
        assert data["limit"] == 25

    def test_model_validate_round_trips(self) -> None:
        params = OffsetParams(page=3, limit=10)

        restored = OffsetParams.model_validate(params.model_dump())

        assert restored.page == params.page
        assert restored.limit == params.limit


class TestCursorParamsDump:
    def test_model_dump_contains_after(self) -> None:
        params = CursorParams(limit=20, after="abc")

        data = params.model_dump()

        assert data["after"] == "abc"
        assert data["before"] is None

    def test_model_validate_round_trips(self) -> None:
        params = CursorParams(limit=15, before="xyz")

        restored = CursorParams.model_validate(params.model_dump())

        assert restored.before == params.before
        assert restored.limit == params.limit


class TestOffsetPageDump:
    def test_model_dump_produces_dict(self) -> None:
        page = OffsetPage.create(items=["a", "b"], total=5, params=OffsetParams(page=1, limit=2))

        data = page.model_dump()

        assert data["total"] == 5
        assert data["items"] == ["a", "b"]
        assert data["pages"] == 3

    def test_model_validate_round_trips(self) -> None:
        page = OffsetPage.create(items=[1], total=1, params=OffsetParams())

        restored = OffsetPage[int].model_validate(page.model_dump())

        assert restored.total == page.total


class TestCursorPageDump:
    def test_model_dump_produces_dict(self) -> None:
        page = CursorPage.create(
            items=["x"],
            params=CursorParams(),
            next_cursor="nxt",
        )

        data = page.model_dump()

        assert data["next_cursor"] == "nxt"
        assert data["has_next"] is True

    def test_model_validate_round_trips(self) -> None:
        page = CursorPage.create(items=[], params=CursorParams())

        restored = CursorPage[str].model_validate(page.model_dump())

        assert restored.has_next is False
        assert restored.items == []
