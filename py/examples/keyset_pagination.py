"""Keyset (cursor) pagination example.

Cursor pagination pages by the *ordering values of the last row seen* instead of
an offset, so it stays correct and fast as rows change. It is database-backed:
this example uses the SQLAlchemy adapter over an in-memory SQLite database.

The cursor is an opaque, URL-safe string produced by the shared Rust codec, so it
is byte-compatible with the Django and TypeScript adapters.

Requirements:
    pip install "pypaginate[sqlalchemy]"

Run:
    uv run python examples/keyset_pagination.py
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from pypaginate import CursorParams
from pypaginate.adapters.sqlalchemy import SyncSQLAlchemyCursorBackend


class Base(DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column()


def seed(session: Session, count: int = 50) -> None:
    """Insert sample articles with descending timestamps."""
    base = datetime.now(tz=UTC)
    session.add_all(
        Article(id=i, title=f"Article {i}", created_at=base - timedelta(hours=i))
        for i in range(1, count + 1)
    )
    session.commit()


def main() -> None:
    """Page forward through every article, then step back one page."""
    engine = create_engine("sqlite://")  # in-memory
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed(session, 50)

        # A unique ORDER BY is required — append the primary key as a tiebreaker.
        stmt = select(Article).order_by(Article.created_at.desc(), Article.id.desc())
        backend = SyncSQLAlchemyCursorBackend(session)

        print("=== Paging forward (limit 10) ===")
        cursor: str | None = None
        page_num = 1
        while True:
            page = backend.fetch_page(stmt, CursorParams(limit=10, after=cursor))
            print(f"\n--- Page {page_num} ---")
            print(f"Items: {len(page)}  (first id={page[0].id}, last id={page[-1].id})")
            print(f"has_next={page.has_next}  next_cursor={page.next_cursor!r}")

            if not page.has_next or page.next_cursor is None:
                print("\n\N{CHECK MARK} Reached the last page")
                break
            cursor = page.next_cursor
            page_num += 1

        # Step back one page from the last page using its `previous_cursor`.
        if page.previous_cursor is not None:
            back = backend.fetch_page(stmt, CursorParams(limit=10, before=page.previous_cursor))
            print(f"\n=== Stepping back (before={page.previous_cursor!r}) ===")
            print(f"Items: {len(back)}  (first id={back[0].id}, last id={back[-1].id})")


if __name__ == "__main__":
    main()
