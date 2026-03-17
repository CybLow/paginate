"""Declarative search dependency for FastAPI.

Parses ``?q=alice&search_fields=name,email`` into SearchSpec.
Pipeline auto-converts via the ``to_spec`` method.

Example::

    @app.get("/users")
    async def get_users(params: OffsetDep, search: SearchDep):
        return pipeline.execute(data, params, search=search).model_dump()
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pypaginate.domain.specs import SearchSpec


class SearchDep(BaseModel):
    """Parse search query parameters into SearchSpec.

    Query params: ``q`` (search text), ``search_fields`` (comma-separated).
    """

    model_config = ConfigDict(extra="forbid")

    q: str | None = None
    search_fields: str = ""

    def to_spec(self) -> SearchSpec | None:
        """Convert to SearchSpec, or None if no query."""
        if not self.q:
            return None
        fields = tuple(f.strip() for f in self.search_fields.split(",") if f.strip())
        if not fields:
            return None
        return SearchSpec(query=self.q, fields=fields)


__all__ = ["SearchDep"]
