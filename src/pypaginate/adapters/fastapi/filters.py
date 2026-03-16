"""Declarative filter dependencies for FastAPI.

Users define filter parameters as Pydantic models. The pipeline
auto-converts via the FilterInput protocol — no `.to_specs()` call needed.

Example::

    class UserFilters(FilterDep):
        name: str | None = FilterField(None, operator="contains")
        age_min: int | None = FilterField(None, field="age", operator="gte")

    @app.get("/users")
    async def get_users(params: OffsetDep, filters: Annotated[UserFilters, Query()]):
        return pipeline.execute(data, params, filters=filters).model_dump()
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from pypaginate.domain.specs import FilterSpec


def FilterField(  # noqa: N802
    default: Any = None,
    *,
    operator: str = "eq",
    field: str | None = None,
    **kwargs: Any,
) -> Any:
    """Declare a filter field with operator metadata.

    Args:
        default: Default value (None means not applied).
        operator: Filter operator name (eq, gte, contains, etc.).
        field: Target field name (defaults to the attribute name).
    """
    return FieldInfo(
        default=default,
        json_schema_extra={"filter_operator": operator, "filter_field": field},
        **kwargs,
    )


class FilterDep(BaseModel):
    """Base class for declarative filter dependencies.

    Subclass this and define fields with ``FilterField()``.
    Non-None fields are converted to FilterSpec via ``to_specs()``.
    Pipeline auto-detects this via the ``to_specs`` method.
    """

    model_config = ConfigDict(extra="forbid")

    def to_specs(self) -> list[FilterSpec]:
        """Convert non-None fields to FilterSpec list."""
        specs: list[FilterSpec] = []
        for name, info in self.model_fields.items():
            value = getattr(self, name)
            if value is None:
                continue
            meta = (info.json_schema_extra or {}) if isinstance(info.json_schema_extra, dict) else {}
            operator = str(meta.get("filter_operator", "eq"))
            target = str(meta.get("filter_field") or name)
            specs.append(FilterSpec(field=target, operator=operator, value=value))  # type: ignore[arg-type]
        return specs


__all__ = ["FilterDep", "FilterField"]
