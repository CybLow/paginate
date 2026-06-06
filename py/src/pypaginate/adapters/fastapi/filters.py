"""Declarative filter dependency for FastAPI.

Subclass :class:`FilterDep` and declare fields with :func:`FilterField` to map
query parameters onto :class:`~pypaginate.FilterSpec` conditions::

    from typing import Annotated
    from fastapi import Query


    class UserFilters(FilterDep):
        name: str | None = FilterField(None, operator="contains")
        min_age: int | None = FilterField(None, field="age", operator="gte")


    @app.get("/users")
    def list_users(filters: Annotated[UserFilters, Query()]):
        specs = filters.to_specs()

Only fields whose value is not ``None`` become ``FilterSpec`` conditions.
"""

from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from pypaginate.specs import FilterOperator, FilterSpec


def FilterField(  # noqa: N802
    default: Any = None,
    *,
    operator: str = "eq",
    field: str | None = None,
    **kwargs: Any,
) -> Any:
    """Declare a filter field carrying its operator + target-field metadata.

    Args:
        default: Default value; ``None`` means the filter is not applied.
        operator: Filter operator wire name (``eq``, ``gte``, ``contains``, ...).
        field: Target field path; defaults to the attribute name.
        **kwargs: Extra keyword arguments forwarded to Pydantic's ``FieldInfo``.

    Returns:
        A Pydantic ``FieldInfo`` carrying the filter metadata.
    """
    extra = {"filter_operator": operator, "filter_field": field}
    return FieldInfo(default=default, json_schema_extra=extra, **kwargs)


def _spec_for(name: str, info: FieldInfo, value: Any) -> FilterSpec:
    """Build a ``FilterSpec`` from a field's name, metadata, and value."""
    extra = info.json_schema_extra
    meta = cast("dict[str, Any]", extra if isinstance(extra, dict) else {})
    operator = cast(FilterOperator, str(meta.get("filter_operator", "eq")))
    target = str(meta.get("filter_field") or name)
    return FilterSpec(field=target, operator=operator, value=value)


class FilterDep(BaseModel):
    """Base class for declarative query-parameter filters."""

    model_config = ConfigDict(extra="forbid")

    def to_specs(self) -> list[FilterSpec]:
        """Convert each non-``None`` field into a ``FilterSpec``."""
        specs: list[FilterSpec] = []
        for name, info in type(self).model_fields.items():
            value = getattr(self, name)
            if value is not None:
                specs.append(_spec_for(name, info, value))
        return specs


__all__ = ["FilterDep", "FilterField"]
