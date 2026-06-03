"""Declarative sort dependency for FastAPI.

Parses ``?sort=name,-age`` query parameter into SortSpec list.
Pipeline auto-converts via the ``to_specs`` method.

Example::

    @app.get("/users")
    async def get_users(params: OffsetDep, sort: SortDep):
        return pipeline.execute(data, params, sorting=sort).model_dump()
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pypaginate.domain.enums import SortDirection
from pypaginate.domain.specs import SortSpec


class SortDep(BaseModel):
    """Parse sort query parameter into SortSpec list.

    Format: ``name,-age`` (comma-separated, - prefix = DESC).
    """

    model_config = ConfigDict(extra="forbid")

    sort: str | None = None

    def to_specs(self) -> list[SortSpec]:
        """Convert sort string to SortSpec list."""
        if not self.sort:
            return []
        specs: list[SortSpec] = []
        for raw in self.sort.split(","):
            part = raw.strip()
            if not part:
                continue
            if part.startswith("-"):
                specs.append(SortSpec(field=part[1:], direction=SortDirection.DESC))
            else:
                field = part.lstrip("+")
                specs.append(SortSpec(field=field))
        return specs


__all__ = ["SortDep"]
