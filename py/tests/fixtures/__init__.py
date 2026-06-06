"""Shared test fixtures: the SQLAlchemy model, DB sessions, and assert helpers."""

from __future__ import annotations

from tests.fixtures.helpers import ids_of, names_of
from tests.fixtures.models import Base, User


__all__ = ["Base", "User", "ids_of", "names_of"]
