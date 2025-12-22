"""Utilities to provision UTF-8 aware database collations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from sqlalchemy import text

if TYPE_CHECKING:  # pragma: no cover - typing only
    from sqlalchemy.ext.asyncio import AsyncEngine


class _AsyncConnection(Protocol):
    async def execute(self, statement: object, /) -> object: ...


class _AsyncBegin(Protocol):
    async def __aenter__(self) -> _AsyncConnection: ...

    async def __aexit__(self, *_: object) -> bool | None: ...


class _HasDialect(Protocol):
    class _Dialect(Protocol):  # pragma: no cover - structural typing helper
        name: str

    dialect: _Dialect

    def begin(self) -> _AsyncBegin: ...


@dataclass(frozen=True)
class CollationPlan:
    """Describe the SQL statements and notes required for a dialect.

    Attributes:
        statements: SQL commands to provision collation capabilities.
        notes: Informational notes associated with the plan.
    """

    statements: tuple[str, ...]
    notes: tuple[str, ...] = ()


_POSTGRES_PLAN = CollationPlan(
    statements=(
        "CREATE EXTENSION IF NOT EXISTS unaccent",
        "CREATE EXTENSION IF NOT EXISTS pg_trgm",
    ),
    notes=(
        "Requires superuser rights the first time the extensions are installed.",
        "Add GIN trigram indexes on searchable columns for best performance.",
    ),
)
_SQLITE_PLAN = CollationPlan(
    statements=(),
    notes=(
        "Use FTS5 virtual tables with tokenize=unicode61 and remove_diacritics=2.",
        "Attach triggers to mirror changes into the FTS table if needed.",
    ),
)


def recommend_collation_plan(dialect_name: str) -> CollationPlan | None:
    """Return the recommended collation plan for a given dialect.

    Args:
        dialect_name: Name of the SQLAlchemy dialect (e.g. "postgresql").

    Returns:
        The matching CollationPlan or None if unsupported.
    """

    mapping = {"postgresql": _POSTGRES_PLAN, "sqlite": _SQLITE_PLAN}
    return mapping.get(dialect_name)


async def ensure_database_collations(
    engine: AsyncEngine | _HasDialect,
) -> CollationPlan | None:
    """Apply the recommended collation plan to the target database.

    Args:
        engine: Async engine or engine-like object exposing dialect.

    Returns:
        The plan that was applied, or None when no plan exists.
    """

    plan = recommend_collation_plan(engine.dialect.name)
    if plan is None:
        return None
    await _apply_plan(engine, plan)
    return plan


async def _execute_statements(
    engine: AsyncEngine | _HasDialect, statements: tuple[str, ...]
) -> None:
    """Execute SQL statements within a transactional context.

    Args:
        engine: Async engine to execute with.
        statements: SQL statements to execute.
    """
    async with engine.begin() as connection:
        for statement in statements:
            await connection.execute(text(statement))


async def _apply_plan(engine: AsyncEngine | _HasDialect, plan: CollationPlan) -> None:
    """Apply the given collation plan and log associated notes.

    Args:
        engine: Async engine to apply plan to.
        plan: Collation plan to apply.
    """
    if plan.statements:
        await _execute_statements(engine, plan.statements)
    _log_notes(plan.notes)


def _log_notes(notes: tuple[str, ...]) -> None:
    """Emit debug logs for each note in the collation plan.

    Args:
        notes: Notes to log.
    """
    if not notes:
        return
    logger = logging.getLogger(__name__)
    for note in notes:
        logger.debug("collation plan note: %s", note)


__all__ = ["CollationPlan", "ensure_database_collations", "recommend_collation_plan"]

