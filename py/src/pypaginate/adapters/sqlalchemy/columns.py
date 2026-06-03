"""Column resolution for SQLAlchemy queries.

Extracts mapped columns from ORM entities referenced in a
SQLAlchemy Select statement, used by filters, sorting, and search.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pypaginate.domain.exceptions import ConfigurationError


if TYPE_CHECKING:
    from sqlalchemy.sql import Select


def resolve_column(query: Select[Any], field: str) -> Any:
    """Resolve a field name to a SQLAlchemy column attribute.

    Inspects the query's column_descriptions to find the ORM entity,
    then resolves the field via ``getattr``.

    Args:
        query: A SQLAlchemy Select statement.
        field: Dotted or simple field name (e.g., ``"name"``).

    Returns:
        The column attribute for use in WHERE/ORDER BY clauses.

    Raises:
        ConfigurationError: If no entity found or field does not exist.
    """
    entity = _extract_entity(query)
    return _get_column_attr(entity, field)


def _extract_entity(query: Select[Any]) -> type:
    """Extract the primary ORM entity from a Select statement.

    Args:
        query: A SQLAlchemy Select statement.

    Returns:
        The ORM entity class.

    Raises:
        ConfigurationError: If no entity is found.
    """
    descriptions = query.column_descriptions
    for desc in descriptions:
        entity: type | None = desc.get("entity")
        if entity is not None:
            return entity
    msg = "No ORM entity found in query column_descriptions"
    raise ConfigurationError(
        msg,
        details={"descriptions": [d.get("name") for d in descriptions]},
    )


def _get_column_attr(entity: type, field: str) -> Any:
    """Get a column attribute from an ORM entity.

    Args:
        entity: The ORM entity class.
        field: The attribute name.

    Returns:
        The column attribute.

    Raises:
        ConfigurationError: If the field does not exist on the entity.
    """
    column = getattr(entity, field, None)
    if column is None:
        msg = f"Field '{field}' not found on {entity.__name__}"
        raise ConfigurationError(
            msg,
            details={"field": field, "entity": entity.__name__},
        )
    return column


__all__ = ["resolve_column"]
