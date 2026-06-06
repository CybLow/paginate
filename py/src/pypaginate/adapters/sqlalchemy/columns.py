"""Column resolution for the SQLAlchemy adapter.

Resolves a spec's ``field`` name to a mapped column attribute on a declarative
model via ``getattr`` — the single source of column lookup shared by the filter,
sort, and keyset translators.
"""

from __future__ import annotations

from typing import Any

from pypaginate.errors import ConfigurationError


def resolve_column(model: type, field: str) -> Any:
    """Resolve ``field`` to a mapped column attribute on ``model``.

    Args:
        model: A declarative ORM model class.
        field: The attribute (column) name to resolve.

    Returns:
        The instrumented column attribute for WHERE / ORDER BY clauses.

    Raises:
        ConfigurationError: If ``field`` is not an attribute of ``model``.
    """
    column = getattr(model, field, None)
    if column is None:
        msg = f"Field '{field}' not found on {model.__name__}"
        raise ConfigurationError(msg, details={"field": field, "model": model.__name__})
    return column


__all__ = ["resolve_column"]
