"""Architecture tests verifying layer boundaries.

Ensures domain modules import nothing from the engine or adapters
layers. Also checks that engine imports nothing from adapters.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest


SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "pypaginate"

DOMAIN_FORBIDDEN = {"engine", "adapters"}
ENGINE_FORBIDDEN = {"adapters"}


def _collect_imports(filepath: Path) -> list[str]:
    """Parse a Python file and return all imported module strings."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def _domain_files() -> list[Path]:
    """Collect all Python files in the domain layer."""
    domain = SRC_ROOT / "domain"
    return sorted(domain.glob("*.py"))


def _engine_files() -> list[Path]:
    """Collect all Python files in the engine layer."""
    engine = SRC_ROOT / "engine"
    return sorted(engine.glob("*.py"))


@pytest.mark.parametrize("filepath", _domain_files(), ids=lambda p: p.name)
def test_domain_imports_no_forbidden_layers(filepath):
    """Domain modules must not import from engine/adapters/etc."""
    imports = _collect_imports(filepath)
    for imp in imports:
        parts = imp.split(".")
        for part in parts:
            assert part not in DOMAIN_FORBIDDEN, (
                f"{filepath.name} imports '{imp}' which references forbidden layer '{part}'"
            )


@pytest.mark.parametrize("filepath", _engine_files(), ids=lambda p: p.name)
def test_engine_imports_no_adapters(filepath):
    """Engine modules must not import from adapters."""
    imports = _collect_imports(filepath)
    for imp in imports:
        parts = imp.split(".")
        for part in parts:
            assert part not in ENGINE_FORBIDDEN, (
                f"{filepath.name} imports '{imp}' which references forbidden layer '{part}'"
            )


def test_no_circular_imports():
    """All public modules can be imported without circular errors."""
    modules = [
        "pypaginate",
        "pypaginate.domain.params",
        "pypaginate.domain.pages",
        "pypaginate.domain.specs",
        "pypaginate.domain.enums",
        "pypaginate.domain.protocols",
        "pypaginate._native",
        "pypaginate.query",
        "pypaginate.adapters.memory.backend",
    ]
    for mod in modules:
        importlib.import_module(mod)
