"""Architecture tests: the public API surface of ``pypaginate``.

Asserts that the package's declared ``__all__`` is coherent (every name is
actually importable) and that the load-bearing names the README and adapters
rely on are present: the ``paginate`` entry point, the ``Dataset`` pipeline,
the params/page containers, the spec dataclasses, the query/spec builders, and
the full error hierarchy.
"""

from __future__ import annotations

import importlib

import pytest

import pypaginate


KEY_NAMES = (
    "paginate",
    "Dataset",
    "OffsetParams",
    "CursorParams",
    "OffsetPage",
    "CursorPage",
    "FilterSpec",
    "SortSpec",
    "SearchSpec",
    "And",
    "Or",
    "filter",
    "sort",
    "search",
    "PaginateError",
    "PaginationError",
    "FilterError",
    "FilterValidationError",
    "SearchError",
    "SearchQueryError",
    "SortError",
    "ConfigurationError",
    "ValidationError",
)

CALLABLE_NAMES = ("paginate", "filter", "sort", "search", "And", "Or", "search_spec")

ERROR_NAMES = (
    "PaginationError",
    "FilterError",
    "FilterValidationError",
    "SearchError",
    "SearchQueryError",
    "SortError",
    "ConfigurationError",
    "ValidationError",
)

CORE_SUBMODULES = (
    "pypaginate",
    "pypaginate.params",
    "pypaginate.pages",
    "pypaginate.specs",
    "pypaginate.errors",
    "pypaginate.query",
    "pypaginate.paginate",
    "pypaginate.dataset",
    "pypaginate._native",
)


@pytest.mark.unit
def test_all_is_non_empty_list() -> None:
    """``__all__`` is a populated list of export names."""
    assert isinstance(pypaginate.__all__, list)
    assert pypaginate.__all__
    assert len(set(pypaginate.__all__)) == len(pypaginate.__all__), "duplicate __all__ entries"


@pytest.mark.unit
@pytest.mark.parametrize("name", sorted(pypaginate.__all__))
def test_all_names_are_importable(name: str) -> None:
    """Every name advertised in ``__all__`` resolves on the package."""
    assert hasattr(pypaginate, name), f"{name} is in __all__ but not importable"


@pytest.mark.unit
@pytest.mark.parametrize("name", KEY_NAMES)
def test_key_name_present(name: str) -> None:
    """Each load-bearing name is both exported and importable."""
    assert name in pypaginate.__all__, f"{name} missing from __all__"
    assert hasattr(pypaginate, name), f"{name} not importable from pypaginate"


@pytest.mark.unit
@pytest.mark.parametrize("name", CALLABLE_NAMES)
def test_builder_is_callable(name: str) -> None:
    """The query/spec entry points are callable."""
    assert callable(getattr(pypaginate, name))


@pytest.mark.unit
@pytest.mark.parametrize("name", ERROR_NAMES)
def test_error_derives_from_base(name: str) -> None:
    """Every concrete error subclasses ``PaginateError``."""
    error_cls = getattr(pypaginate, name)
    assert isinstance(error_cls, type)
    assert issubclass(error_cls, pypaginate.PaginateError)


@pytest.mark.unit
def test_version_is_non_empty_string() -> None:
    """``__version__`` is exported and is a non-empty string."""
    assert "__version__" in pypaginate.__all__
    assert isinstance(pypaginate.__version__, str)
    assert pypaginate.__version__


@pytest.mark.unit
@pytest.mark.parametrize("module_name", CORE_SUBMODULES)
def test_core_module_imports_cleanly(module_name: str) -> None:
    """Each core module imports without circular-import errors."""
    assert importlib.import_module(module_name) is not None
