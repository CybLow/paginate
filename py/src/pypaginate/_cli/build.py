"""Build and clean commands for the CLI.

Handles building distribution packages and removing build artifacts.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pypaginate._cli.output import _print_header, _print_success
from pypaginate._cli.runner import _get_project_root, _run


def cmd_build(extra_args: list[str] | None = None) -> int:
    """Build distribution packages using UV."""
    _print_header("Building Distribution")
    _clean_build_dirs()
    args = ["uv", "build"]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("Build completed! Artifacts in dist/")
    return result.returncode


def _clean_build_dirs() -> None:
    """Remove previous build and dist directories."""
    root = _get_project_root()
    for path in [root / "dist", root / "build"]:
        if path.exists():
            shutil.rmtree(path)
            print(f"  Cleaned {path.name}/")


def cmd_clean(extra_args: list[str] | None = None) -> int:  # noqa: ARG001
    """Remove build artifacts and caches."""
    _print_header("Cleaning Build Artifacts")
    root = _get_project_root()
    removed = _remove_named_artifacts(root)
    removed += _remove_glob_artifacts(root)
    _print_success(f"Cleaned {removed} items.")
    return 0


_ARTIFACT_NAMES: tuple[str, ...] = (
    "build",
    "dist",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "coverage.xml",
)


def _remove_named_artifacts(root: Path) -> int:
    """Remove known build artifact directories and files."""
    removed = 0
    for name in _ARTIFACT_NAMES:
        path = root / name
        if not path.exists():
            continue
        _remove_path(path, name)
        removed += 1
    return removed


def _remove_path(path: Path, label: str) -> None:
    """Remove a single file or directory and print status."""
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    print(f"  Removed {label}")


def _remove_glob_artifacts(root: Path) -> int:
    """Remove glob-matched build artifact files and directories."""
    patterns = [
        "**/__pycache__",
        "**/*.egg-info",
        "**/*.pyc",
        "**/*.pyo",
    ]
    removed = 0
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed += 1
    return removed
