"""SQLAlchemy 2.0 model for the real-database test lanes.

A single ``User`` table whose columns mirror the deterministic factory rows
(``tests.factories.data.make_users``) one-to-one, so a row dict can be splatted
straight into the constructor. It lives on its own ``DeclarativeBase`` registry,
independent of the inline model in ``tests/integration/test_sqlalchemy.py`` (a
separate metadata — no table/class conflict even on a shared interpreter).
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for the shared fixture model."""


class User(Base):
    """A user row mirroring the factory fields exactly."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    age: Mapped[int] = mapped_column()
    score: Mapped[float] = mapped_column()
    active: Mapped[bool] = mapped_column()
    created_at: Mapped[str] = mapped_column(String(40))

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"


__all__ = ["Base", "User"]
