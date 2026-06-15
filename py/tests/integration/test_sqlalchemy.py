"""SQLAlchemy adapter integration tests against an in-memory SQLite database.

Exercises the adapter's public surface end-to-end over real rows:
``build_filter`` / ``build_filter_group`` (WHERE), ``build_order_by`` (ORDER BY),
``SyncSQLAlchemyBackend`` (offset pages), and ``SyncSQLAlchemyCursorBackend``
(forward + backward keyset round-trip).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)
from sqlalchemy.pool import StaticPool

from pypaginate import CursorParams, InvalidCursorError, OffsetParams
from pypaginate.adapters.sqlalchemy import (
    SyncSQLAlchemyBackend,
    SyncSQLAlchemyCursorBackend,
    build_filter,
    build_filter_group,
    build_order_by,
)
from pypaginate.specs import And, FilterSpec, Or, SortSpec


pytestmark = [pytest.mark.integration, pytest.mark.sqlalchemy]


class Base(DeclarativeBase):
    """Declarative base for the test model."""


class User(Base):
    """A minimal user row with a nullable ``nickname`` for null-aware tests."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column()
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)


# id, name, age, nickname
_ROWS: list[tuple[int, str, int, str | None]] = [
    (1, "Alice", 30, "Al"),
    (2, "Bob", 25, None),
    (3, "Carol", 35, "Caz"),
    (4, "Dave", 40, None),
    (5, "Eve", 28, "Evie"),
]


@pytest.fixture
def session() -> Iterator[Session]:
    """A fresh in-memory SQLite session seeded with ``_ROWS``."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(User(id=i, name=n, age=a, nickname=nick) for i, n, a, nick in _ROWS)
        session.commit()
        yield session
    engine.dispose()


def _ids_where(session: Session, condition: object) -> list[int]:
    """IDs (ascending) of the users matching ``condition``."""
    stmt = select(User.id).where(condition).order_by(User.id)
    return list(session.scalars(stmt))


def test_build_filter_eq(session: Session) -> None:
    condition = build_filter(User, [FilterSpec(field="name", operator="eq", value="Alice")])

    assert _ids_where(session, condition) == [1]


def test_build_filter_in(session: Session) -> None:
    condition = build_filter(User, [FilterSpec(field="age", operator="in", value=[25, 30])])

    assert _ids_where(session, condition) == [1, 2]


def test_build_filter_not_in(session: Session) -> None:
    condition = build_filter(User, [FilterSpec(field="age", operator="not_in", value=[25, 30])])

    assert _ids_where(session, condition) == [3, 4, 5]


def test_build_filter_between(session: Session) -> None:
    condition = build_filter(User, [FilterSpec(field="age", operator="between", value=[28, 35])])

    assert _ids_where(session, condition) == [1, 3, 5]


def test_build_filter_contains(session: Session) -> None:
    condition = build_filter(User, [FilterSpec(field="name", operator="contains", value="o")])

    assert _ids_where(session, condition) == [2, 3]


def test_build_filter_is_null(session: Session) -> None:
    condition = build_filter(User, [FilterSpec(field="nickname", operator="is_null", value=None)])

    assert _ids_where(session, condition) == [2, 4]


def test_build_filter_empty_returns_none() -> None:
    assert build_filter(User, []) is None


def test_build_filter_group_and(session: Session) -> None:
    group = And(
        FilterSpec(field="age", operator="gte", value=30),
        FilterSpec(field="nickname", operator="is_not_null", value=None),
    )

    condition = build_filter_group(User, group)

    assert _ids_where(session, condition) == [1, 3]


def test_build_filter_group_or(session: Session) -> None:
    group = Or(
        FilterSpec(field="name", operator="eq", value="Alice"),
        FilterSpec(field="name", operator="eq", value="Bob"),
    )

    condition = build_filter_group(User, group)

    assert _ids_where(session, condition) == [1, 2]


def test_build_filter_group_nested(session: Session) -> None:
    group = And(
        FilterSpec(field="age", operator="gte", value=28),
        Or(
            FilterSpec(field="name", operator="eq", value="Alice"),
            FilterSpec(field="name", operator="eq", value="Eve"),
        ),
    )

    condition = build_filter_group(User, group)

    assert _ids_where(session, condition) == [1, 5]


def _ordered_ids(session: Session, clauses: list[object]) -> list[int]:
    """IDs of all users in the order produced by ``clauses``."""
    stmt = select(User.id).order_by(*clauses)
    return list(session.scalars(stmt))


def test_build_order_by_asc(session: Session) -> None:
    clauses = build_order_by(User, [SortSpec(field="age", direction="asc")])

    assert _ordered_ids(session, clauses) == [2, 5, 1, 3, 4]


def test_build_order_by_desc(session: Session) -> None:
    clauses = build_order_by(User, [SortSpec(field="age", direction="desc")])

    assert _ordered_ids(session, clauses) == [4, 3, 1, 5, 2]


def test_build_order_by_nulls_first(session: Session) -> None:
    clauses = build_order_by(User, [SortSpec(field="nickname", direction="asc", nulls="first")])

    ids = _ordered_ids(session, clauses)

    assert ids[:2] == [2, 4]  # the two null nicknames lead
    assert ids[2:] == [1, 3, 5]  # then Al, Caz, Evie


def test_build_order_by_nulls_last(session: Session) -> None:
    clauses = build_order_by(User, [SortSpec(field="nickname", direction="asc", nulls="last")])

    ids = _ordered_ids(session, clauses)

    assert ids[:3] == [1, 3, 5]
    assert ids[3:] == [2, 4]


def test_offset_backend_first_page(session: Session) -> None:
    backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(session)
    query = select(User).order_by(User.id)

    page = backend.paginate(query, OffsetParams(page=1, limit=2))

    assert [u.id for u in page.items] == [1, 2]
    assert page.total == 5
    assert page.pages == 3
    assert page.has_next is True
    assert page.has_previous is False


def test_offset_backend_middle_page(session: Session) -> None:
    backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(session)
    query = select(User).order_by(User.id)

    page = backend.paginate(query, OffsetParams(page=2, limit=2))

    assert [u.id for u in page.items] == [3, 4]
    assert page.has_next is True
    assert page.has_previous is True


def test_offset_backend_last_page(session: Session) -> None:
    backend: SyncSQLAlchemyBackend[User] = SyncSQLAlchemyBackend(session)
    query = select(User).order_by(User.id)

    page = backend.paginate(query, OffsetParams(page=3, limit=2))

    assert [u.id for u in page.items] == [5]
    assert page.has_next is False
    assert page.has_previous is True


def test_keyset_malformed_cursor_raises_invalid_cursor(session: Session) -> None:
    backend: SyncSQLAlchemyCursorBackend[User] = SyncSQLAlchemyCursorBackend(session)
    query = select(User).order_by(User.id)

    with pytest.raises(InvalidCursorError):
        backend.fetch_page(query, CursorParams(limit=2, after="not-a-cursor!!"))


def test_keyset_forward_round_trip(session: Session) -> None:
    backend: SyncSQLAlchemyCursorBackend[User] = SyncSQLAlchemyCursorBackend(session)
    query = select(User).order_by(User.id)

    first = backend.fetch_page(query, CursorParams(limit=2))

    assert [u.id for u in first.items] == [1, 2]
    assert first.has_next is True
    assert first.has_previous is False
    assert first.next_cursor is not None

    second = backend.fetch_page(query, CursorParams(limit=2, after=first.next_cursor))

    assert [u.id for u in second.items] == [3, 4]
    assert second.has_next is True
    assert second.has_previous is True


def test_keyset_backward_returns_previous_page(session: Session) -> None:
    backend: SyncSQLAlchemyCursorBackend[User] = SyncSQLAlchemyCursorBackend(session)
    query = select(User).order_by(User.id)

    first = backend.fetch_page(query, CursorParams(limit=2))
    second = backend.fetch_page(query, CursorParams(limit=2, after=first.next_cursor))
    assert second.previous_cursor is not None

    back = backend.fetch_page(query, CursorParams(limit=2, before=second.previous_cursor))

    assert [u.id for u in back.items] == [1, 2]
    assert back.has_next is True


def test_keyset_exhausts_forward(session: Session) -> None:
    backend: SyncSQLAlchemyCursorBackend[User] = SyncSQLAlchemyCursorBackend(session)
    query = select(User).order_by(User.id)

    first = backend.fetch_page(query, CursorParams(limit=2))
    second = backend.fetch_page(query, CursorParams(limit=2, after=first.next_cursor))
    third = backend.fetch_page(query, CursorParams(limit=2, after=second.next_cursor))

    assert [u.id for u in third.items] == [5]
    assert third.has_next is False
