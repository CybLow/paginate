"""Query layer for pagination operations.

This module provides high-level query functions. SQLAlchemy support is optional.
"""

from __future__ import annotations

from .async_api import (
    paginate_entities,
    paginate_entities_to_page,
    paginate_rows,
    paginate_rows_to_page,
)


__all__ = [
    "paginate_entities",
    "paginate_entities_to_page",
    "paginate_rows",
    "paginate_rows_to_page",
]
