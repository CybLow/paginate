"""Deterministic data factories for the real-condition test lanes.

Every value is derived from the row index and ``seed`` — there is no randomness,
so a given ``(n, seed)`` always yields byte-identical rows. This is what lets the
SQLAlchemy / PostgreSQL / parity lanes compare a native ``Dataset`` against a
pure-Python reference over the *same* rows.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


#: A small pool of first/last names — indexed deterministically, never sampled.
_FIRST = (
    "Alice",
    "Bob",
    "Carol",
    "Dave",
    "Eve",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
)
_LAST = ("Adams", "Brown", "Clark", "Davis", "Evans", "Frost", "Green")

#: Fixed epoch for ISO ``created_at`` strings (UTC, no DST surprises).
_EPOCH = datetime(2020, 1, 1, tzinfo=UTC)


def _name_for(index: int) -> str:
    """A stable ``First Last`` name for ``index`` (cycles the two pools)."""
    first = _FIRST[index % len(_FIRST)]
    last = _LAST[(index // len(_FIRST)) % len(_LAST)]
    return f"{first} {last}"


def _email_for(name: str, user_id: int) -> str:
    """A unique lowercase email derived from the name and id."""
    return f"{name.lower().replace(' ', '.')}{user_id}@example.com"


def _created_at_for(index: int) -> str:
    """An ISO-8601 timestamp that increases monotonically with ``index``."""
    return (_EPOCH + timedelta(days=index, minutes=index * 7)).isoformat()


def make_user(index: int, *, seed: int = 0) -> dict[str, object]:
    """Build one fully deterministic user row for ``index`` under ``seed``."""
    salted = index + seed
    user_id = index + 1
    name = _name_for(salted)
    return {
        "id": user_id,
        "name": name,
        "email": _email_for(name, user_id),
        "age": 18 + (salted * 7) % 60,
        "score": round((salted * 37 % 1000) / 10, 1),
        "active": salted % 3 != 0,
        "created_at": _created_at_for(index),
    }


def make_users(n: int = 50, *, seed: int = 0) -> list[dict[str, object]]:
    """Build ``n`` deterministic user rows (keys: id/name/email/age/score/active/created_at)."""
    return [make_user(index, seed=seed) for index in range(n)]


__all__ = ["make_user", "make_users"]
