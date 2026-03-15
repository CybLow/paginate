"""Test factories package.

Re-exports dataset generators and domain model factories
for convenient imports across the test suite.
"""

from __future__ import annotations

from tests.factories.data import make_products, make_records, make_users
from tests.factories.domain import (
    make_cursor_page,
    make_cursor_params,
    make_filter_spec,
    make_offset_page,
    make_offset_params,
    make_search_spec,
    make_sort_spec,
)


__all__ = [
    "make_cursor_page",
    "make_cursor_params",
    "make_filter_spec",
    "make_offset_page",
    "make_offset_params",
    "make_products",
    "make_records",
    "make_search_spec",
    "make_sort_spec",
    "make_users",
]
