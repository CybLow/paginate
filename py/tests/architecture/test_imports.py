"""Architecture tests: dependency direction and optional-dependency rules.

Two boundaries are enforced by walking each module's import statements with
the ``ast`` module:

* **Pydantic isolation** -- only the FastAPI adapter
  (``src/pypaginate/adapters/fastapi/``) may import ``pydantic``. The core and
  every other adapter must stay Pydantic-free so the package has zero required
  runtime dependencies.
* **Inward dependencies** -- the core modules (``params``, ``pages``, ``specs``,
  ``errors``, ``query``, ``paginate``, ``dataset``, ``_native``) must not import
  anything from ``pypaginate.adapters``; dependencies point inward, never from
  the core out to infrastructure.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "pypaginate"
PACKAGE_ROOT = SRC_ROOT.parent  # the importable root (``src/``)
REPO_ROOT = SRC_ROOT.parents[1]
FASTAPI_DIR = SRC_ROOT / "adapters" / "fastapi"
CORE_MODULES = (
    "params",
    "pages",
    "specs",
    "errors",
    "query",
    "paginate",
    "dataset",
    "_native",
)


def _label(path: Path) -> str:
    """Repo-relative label used as a readable parametrize id."""
    return str(path.relative_to(REPO_ROOT))


def _module_name(path: Path) -> str:
    """Dotted module name for ``path`` (``__init__`` collapses to package)."""
    parts = list(path.relative_to(PACKAGE_ROOT).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _package_of(path: Path) -> str:
    """The package that ``path`` lives in (for resolving relative imports)."""
    name = _module_name(path)
    if path.name == "__init__.py":
        return name
    return name.rsplit(".", 1)[0] if "." in name else ""


def _resolve_relative(node: ast.ImportFrom, package: str) -> str:
    """Resolve a relative ``from`` import to its absolute dotted base."""
    if node.level == 0:
        return node.module or ""
    base = package.split(".") if package else []
    keep = len(base) - (node.level - 1)
    prefix = base[:keep] if keep >= 0 else []
    return ".".join([*prefix, node.module] if node.module else prefix)


def _imported_modules(path: Path) -> set[str]:
    """Absolute dotted names imported by the module at ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    package = _package_of(path)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_relative(node, package)
            modules.add(base)
            modules.update(
                f"{base}.{alias.name}" if base else alias.name
                for alias in node.names
                if alias.name != "*"
            )
    modules.discard("")
    return modules


def _imports_package(modules: set[str], target: str) -> bool:
    """Whether any imported name is ``target`` or a submodule of it."""
    return any(name == target or name.startswith(f"{target}.") for name in modules)


def _is_under_fastapi(path: Path) -> bool:
    """Whether ``path`` belongs to the FastAPI adapter package."""
    return FASTAPI_DIR in path.parents


def _non_fastapi_modules() -> list[Path]:
    """All source modules except the Pydantic-exempt FastAPI adapter."""
    return sorted(p for p in SRC_ROOT.rglob("*.py") if not _is_under_fastapi(p))


def _core_module_paths() -> list[Path]:
    """Filesystem paths of the inward-only core modules."""
    return [SRC_ROOT / f"{name}.py" for name in CORE_MODULES]


@pytest.mark.unit
def test_pydantic_detector_finds_fastapi_usage() -> None:
    """Positive control: the FastAPI adapter does import pydantic."""
    fastapi_files = sorted(FASTAPI_DIR.rglob("*.py"))
    assert fastapi_files, f"no fastapi adapter modules under {FASTAPI_DIR}"
    assert any(_imports_package(_imported_modules(p), "pydantic") for p in fastapi_files), (
        "expected the fastapi adapter to import pydantic; the detector may be broken"
    )


@pytest.mark.unit
@pytest.mark.parametrize("path", _non_fastapi_modules(), ids=_label)
def test_only_fastapi_adapter_imports_pydantic(path: Path) -> None:
    """No module outside ``adapters/fastapi`` may import pydantic."""
    modules = _imported_modules(path)
    assert not _imports_package(modules, "pydantic"), (
        f"{_label(path)} imports pydantic; only adapters/fastapi may"
    )


@pytest.mark.unit
@pytest.mark.parametrize("path", _core_module_paths(), ids=lambda p: p.stem)
def test_core_module_exists(path: Path) -> None:
    """Each named core module is present at the expected flat-layout path."""
    assert path.is_file(), f"expected core module {_label(path)} to exist"


@pytest.mark.unit
@pytest.mark.parametrize("path", _core_module_paths(), ids=lambda p: p.stem)
def test_core_module_does_not_import_adapters(path: Path) -> None:
    """Core modules must not depend on any adapter."""
    modules = _imported_modules(path)
    assert not _imports_package(modules, "pypaginate.adapters"), (
        f"{_label(path)} imports pypaginate.adapters; the core must stay adapter-free"
    )
