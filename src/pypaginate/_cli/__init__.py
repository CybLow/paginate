"""CLI entry point for pypaginate development commands.

This module provides development utilities accessible via ``uv run pypaginate <cmd>``.
For production use, prefer direct tool invocation or UV scripts.

Usage:
    uv run pypaginate lint          # Check code with ruff
    uv run pypaginate lint --fix    # Auto-fix linting issues
    uv run pypaginate format        # Format code with ruff
    uv run pypaginate typecheck     # Run mypy type checking
    uv run pypaginate test          # Run test suite
    uv run pypaginate test -x       # Run tests, stop on first failure
    uv run pypaginate quality       # Run all quality checks
    uv run pypaginate build         # Build distribution packages
    uv run pypaginate clean         # Remove build artifacts
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import NoReturn, cast

from pypaginate._cli.commands import (
    cmd_build,
    cmd_clean,
    cmd_format,
    cmd_lint,
    cmd_quality,
    cmd_quality_strict,
    cmd_test,
    cmd_test_cov,
    cmd_typecheck,
)
from pypaginate._cli.output import _colorize, _print_error, _show_help


__all__ = [
    "cmd_build",
    "cmd_clean",
    "cmd_format",
    "cmd_lint",
    "cmd_quality",
    "cmd_quality_strict",
    "cmd_test",
    "cmd_test_cov",
    "cmd_typecheck",
    "main",
]

_COMMANDS = {
    "format": cmd_format,
    "fmt": cmd_format,
    "lint": cmd_lint,
    "typecheck": cmd_typecheck,
    "tc": cmd_typecheck,
    "test": cmd_test,
    "test-cov": cmd_test_cov,
    "quality": cmd_quality,
    "qa": cmd_quality,
    "quality-strict": cmd_quality_strict,
    "qas": cmd_quality_strict,
    "build": cmd_build,
    "clean": cmd_clean,
    "help": lambda _: _show_help(),
    "--help": lambda _: _show_help(),
    "-h": lambda _: _show_help(),
}


def _parse_args() -> tuple[str, list[str] | None]:
    """Parse command-line arguments.

    Returns:
        Tuple of (command, extra_args).
    """
    if len(sys.argv) < 2:
        _show_help()
    command = sys.argv[1].lower()
    extra_args = sys.argv[2:] if len(sys.argv) > 2 else None
    return command, extra_args


def main() -> NoReturn:
    """Entry point for the pypaginate CLI."""
    command, extra_args = _parse_args()
    if command not in _COMMANDS:
        _print_error(f"Unknown command: {command}")
        print(f"Run '{_colorize('uv run pypaginate --help', 'cyan')}' for available commands.")
        raise SystemExit(1)
    exit_code = cast("Callable[[list[str] | None], int]", _COMMANDS[command])(extra_args)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
