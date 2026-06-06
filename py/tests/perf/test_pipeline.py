"""Full-pipeline throughput benchmarks over ``Dataset.page``.

One native call that combines filter + sort (+ search) + offset-paginate over the
resident, marshalled :class:`Dataset`, at 1K and 10K rows from the factory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pypaginate import FilterSpec, OffsetParams, SearchSpec, SortSpec


if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

    from pypaginate import Dataset


_FILTERS = [FilterSpec(field="age", operator="gte", value=30)]
_SORTING = [SortSpec(field="age", direction="asc")]
_SEARCH = SearchSpec(query="a", fields=["name", "email"])
_PARAMS = OffsetParams(page=1, limit=20)


@pytest.mark.benchmark(group="pipeline")
def test_pipeline_1k_filter_sort(
    benchmark: BenchmarkFixture, native_1k: Dataset[dict[str, object]]
) -> None:
    """Filter + sort + paginate over the marshalled 1K rows."""
    result = benchmark(native_1k.page, _PARAMS, filters=_FILTERS, sorting=_SORTING)
    assert result.total > 0


@pytest.mark.benchmark(group="pipeline")
def test_pipeline_10k_filter_sort(
    benchmark: BenchmarkFixture, native_10k: Dataset[dict[str, object]]
) -> None:
    """Filter + sort + paginate over the marshalled 10K rows."""
    result = benchmark(native_10k.page, _PARAMS, filters=_FILTERS, sorting=_SORTING)
    assert result.total > 0


@pytest.mark.benchmark(group="pipeline")
def test_pipeline_10k_full(
    benchmark: BenchmarkFixture, native_10k: Dataset[dict[str, object]]
) -> None:
    """Filter + search + sort + paginate over the marshalled 10K rows."""
    result = benchmark(native_10k.page, _PARAMS, filters=_FILTERS, sorting=_SORTING, search=_SEARCH)
    assert result.total >= 0
