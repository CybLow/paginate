"""Property-based pagination invariants.

Uses Hypothesis on the memory backend to verify algebraic
properties that must hold for any valid paginator.
"""

from __future__ import annotations

import math

from hypothesis import given

from pypaginate.domain.models import OffsetParams
from tests.property.conftest import setup_memory_sync
from tests.property.strategies import datasets, offset_params


@given(data=datasets(min_size=1, max_size=200), params=offset_params())
def test_total_equals_data_length(
    data: list[dict[str, object]],
    params: OffsetParams,
) -> None:
    """Total always equals input data length."""
    env = setup_memory_sync(data)
    page = env.do_paginate(env.query, params)
    assert page.total == len(data)


@given(data=datasets(min_size=1, max_size=200), params=offset_params())
def test_page_size_le_limit(
    data: list[dict[str, object]],
    params: OffsetParams,
) -> None:
    """Page never has more items than the limit."""
    env = setup_memory_sync(data)
    page = env.do_paginate(env.query, params)
    assert len(page.items) <= params.limit


@given(data=datasets(min_size=1, max_size=100))
def test_all_pages_sum_to_total(
    data: list[dict[str, object]],
) -> None:
    """Sum of items across all pages equals total."""
    env = setup_memory_sync(data)
    limit = 7
    collected = 0
    page_num = 1
    total_pages = math.ceil(len(data) / limit)
    for page_num in range(1, total_pages + 1):
        page = env.do_paginate(env.query, OffsetParams(page=page_num, limit=limit))
        collected += len(page.items)
    assert collected == len(data)


@given(data=datasets(min_size=1, max_size=200), params=offset_params())
def test_has_next_correct(
    data: list[dict[str, object]],
    params: OffsetParams,
) -> None:
    """has_next is True iff there are more pages."""
    env = setup_memory_sync(data)
    page = env.do_paginate(env.query, params)
    expected_pages = math.ceil(len(data) / params.limit)
    if params.page < expected_pages:
        assert page.has_next is True
    elif params.page >= expected_pages:
        assert page.has_next is False


@given(data=datasets(min_size=1, max_size=200), params=offset_params())
def test_has_previous_correct(
    data: list[dict[str, object]],
    params: OffsetParams,
) -> None:
    """has_previous is True iff page > 1."""
    env = setup_memory_sync(data)
    page = env.do_paginate(env.query, params)
    if params.page > 1:
        assert page.has_previous is True
    else:
        assert page.has_previous is False


@given(data=datasets(min_size=0, max_size=50))
def test_empty_dataset_empty_page(
    data: list[dict[str, object]],
) -> None:
    """Empty dataset always yields empty page."""
    if len(data) == 0:
        env = setup_memory_sync(data)
        page = env.do_paginate(env.query, OffsetParams(page=1, limit=10))
        assert page.total == 0
        assert len(page.items) == 0
