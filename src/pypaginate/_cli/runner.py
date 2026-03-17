"""Subprocess execution with error handling.

Provides a safe wrapper around subprocess.run for CLI commands.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NoReturn

from pypaginate._cli.output import _print_error


def _run(
    *args: str,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command with proper error handling."""
    try:
        return _execute(args, check=check, capture=capture)
    except FileNotFoundError as e:
        _abort_missing_command(args[0], e)
    except subprocess.CalledProcessError:
        if check:
            raise
        return subprocess.CompletedProcess(args, returncode=1)


def _execute(
    args: tuple[str, ...],
    *,
    check: bool,
    capture: bool,
) -> subprocess.CompletedProcess[str]:
    """Execute a subprocess command."""
    return subprocess.run(args, check=check, text=True, capture_output=capture)  # noqa: S603


def _abort_missing_command(name: str, cause: Exception) -> NoReturn:
    """Report a missing command and exit."""
    _print_error(f"Command not found: {name}")
    _print_error("Make sure you have installed dev dependencies: uv sync --group dev")
    raise SystemExit(1) from cause


def _get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent.parent.parent
