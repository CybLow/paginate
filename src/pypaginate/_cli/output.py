"""Terminal output formatting and color utilities.

Provides ANSI color support, formatted headers, and help text display.
"""

from __future__ import annotations

import sys
from typing import NoReturn


# ANSI color codes for terminal output
_COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
}


def _supports_color() -> bool:
    """Check if the terminal supports ANSI colors."""
    if sys.platform == "win32":
        return "ANSICON" in __import__("os").environ or "WT_SESSION" in __import__("os").environ
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _colorize(text: str, color: str) -> str:
    """Apply ANSI color to text if terminal supports it."""
    if not _supports_color():
        return text
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def _print_header(title: str) -> None:
    """Print a formatted section header."""
    separator = "─" * 50
    print(f"\n{_colorize(separator, 'cyan')}")
    print(f"{_colorize('▶', 'blue')} {_colorize(title, 'bold')}")
    print(f"{_colorize(separator, 'cyan')}\n")


def _print_success(message: str) -> None:
    """Print a success message."""
    print(f"\n{_colorize('✓', 'green')} {_colorize(message, 'green')}")


def _print_error(message: str) -> None:
    """Print an error message."""
    print(f"\n{_colorize('✗', 'red')} {_colorize(message, 'red')}", file=sys.stderr)


_HELP_TEXT = """
{header}pypaginate - Development CLI{reset}

{bold}Usage:{reset}
    uv run pypaginate <command> [options]

{bold}Commands:{reset}
    {cyan}format{reset}          Format code with ruff (alias: fmt)
    {cyan}lint{reset}            Run linting checks (--fix to auto-fix)
    {cyan}typecheck{reset}       Run mypy type checking (alias: tc)
    {cyan}test{reset}            Run test suite
    {cyan}test-cov{reset}        Run tests with coverage
    {cyan}quality{reset}         Run quality checks: format, lint, test (alias: qa)
    {cyan}quality-strict{reset}  Run all checks including mypy (alias: qas)
    {cyan}build{reset}           Build distribution packages
    {cyan}clean{reset}           Remove build artifacts

{bold}Examples:{reset}
    uv run pypaginate lint --fix
    uv run pypaginate test -x -v
    uv run pypaginate qa
    uv run pypaginate qas

{bold}UV Commands:{reset}
    uv sync                      Sync dependencies
    uv sync --group docs         Include docs dependencies
    uv build                     Build package
    uv publish                   Publish to PyPI
"""


def _show_help() -> NoReturn:
    """Display help message and exit."""
    formatted = _HELP_TEXT.format(**_COLORS, header=_COLORS["bold"] + _COLORS["cyan"])
    print(formatted)
    raise SystemExit(0)
