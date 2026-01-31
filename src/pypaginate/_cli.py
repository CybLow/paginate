"""CLI entry point for pypaginate development commands.

This module provides development utilities accessible via `uv run pypaginate <cmd>`.
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

import shutil
import subprocess
import sys
from pathlib import Path
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


def _run(
    *args: str,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command with proper error handling.

    Args:
        *args: Command and arguments to run.
        check: If True, raise on non-zero exit code.
        capture: If True, capture stdout/stderr.

    Returns:
        CompletedProcess instance.

    Raises:
        subprocess.CalledProcessError: If command fails and check is True.
    """
    try:
        return subprocess.run(
            args,
            check=check,
            text=True,
            capture_output=capture,
        )
    except FileNotFoundError as e:
        _print_error(f"Command not found: {args[0]}")
        _print_error("Make sure you have installed dev dependencies: uv sync --group dev")
        raise SystemExit(1) from e
    except subprocess.CalledProcessError:
        if check:
            raise
        return subprocess.CompletedProcess(args, returncode=1)


def _get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


# ================================
# COMMAND IMPLEMENTATIONS
# ================================


def cmd_format(extra_args: list[str] | None = None) -> int:
    """Format code with ruff formatter."""
    _print_header("Formatting Code")
    args = ["ruff", "format", "src", "tests"]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("Code formatted successfully!")
    return result.returncode


def cmd_lint(extra_args: list[str] | None = None) -> int:
    """Run linting checks with ruff."""
    _print_header("Running Linter")
    args = ["ruff", "check", "src", "tests"]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("No linting issues found!")
    return result.returncode


def cmd_typecheck(extra_args: list[str] | None = None) -> int:
    """Run type checking with mypy."""
    _print_header("Type Checking")
    args = ["mypy", "src"]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("Type checking passed!")
    return result.returncode


def cmd_test(extra_args: list[str] | None = None) -> int:
    """Run test suite with pytest."""
    _print_header("Running Tests")
    args = ["pytest"]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("All tests passed!")
    return result.returncode


def cmd_test_cov(extra_args: list[str] | None = None) -> int:
    """Run tests with coverage report."""
    _print_header("Running Tests with Coverage")
    args = [
        "pytest",
        "--cov=pypaginate",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=html",
        "--cov-report=xml",
    ]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("Tests passed! Coverage report generated in htmlcov/")
    return result.returncode


def cmd_quality(extra_args: list[str] | None = None) -> int:  # noqa: ARG001
    """Run essential quality checks (format, lint, test)."""
    _print_header("Running Quality Checks")
    checks = [
        ("Formatting check", ["ruff", "format", "--check", "src", "tests"]),
        ("Linting", ["ruff", "check", "src", "tests"]),
        ("Tests", ["pytest", "-q"]),
    ]

    failed = []
    for name, cmd in checks:
        print(f"  {_colorize('→', 'cyan')} {name}...", end=" ", flush=True)
        result = _run(*cmd, check=False, capture=True)
        if result.returncode == 0:
            print(_colorize("✓", "green"))
        else:
            print(_colorize("✗", "red"))
            failed.append((name, result))

    print()
    if failed:
        _print_error(f"{len(failed)} check(s) failed:")
        for name, result in failed:
            print(f"  • {name}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        return 1

    _print_success("All quality checks passed!")
    return 0


def cmd_quality_strict(extra_args: list[str] | None = None) -> int:  # noqa: ARG001
    """Run all quality checks including type checking."""
    _print_header("Running Strict Quality Checks")
    checks = [
        ("Formatting check", ["ruff", "format", "--check", "src", "tests"]),
        ("Linting", ["ruff", "check", "src", "tests"]),
        ("Type checking", ["mypy", "src"]),
        ("Tests", ["pytest", "-q"]),
    ]

    failed = []
    for name, cmd in checks:
        print(f"  {_colorize('→', 'cyan')} {name}...", end=" ", flush=True)
        result = _run(*cmd, check=False, capture=True)
        if result.returncode == 0:
            print(_colorize("✓", "green"))
        else:
            print(_colorize("✗", "red"))
            failed.append((name, result))

    print()
    if failed:
        _print_error(f"{len(failed)} check(s) failed:")
        for name, result in failed:
            print(f"  • {name}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        return 1

    _print_success("All strict quality checks passed!")
    return 0


def cmd_build(extra_args: list[str] | None = None) -> int:
    """Build distribution packages using UV."""
    _print_header("Building Distribution")
    root = _get_project_root()

    # Clean previous builds
    for path in [root / "dist", root / "build"]:
        if path.exists():
            shutil.rmtree(path)
            print(f"  Cleaned {path.name}/")

    args = ["uv", "build"]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("Build completed! Artifacts in dist/")
    return result.returncode


def cmd_clean(extra_args: list[str] | None = None) -> int:  # noqa: ARG001
    """Remove build artifacts and caches."""
    _print_header("Cleaning Build Artifacts")
    root = _get_project_root()

    dirs_to_remove = [
        "build",
        "dist",
        "htmlcov",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".coverage",
        "coverage.xml",
    ]

    patterns_to_remove = ["**/__pycache__", "**/*.egg-info", "**/*.pyc", "**/*.pyo"]

    removed = 0
    for name in dirs_to_remove:
        path = root / name
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"  Removed {name}")
            removed += 1

    for pattern in patterns_to_remove:
        for path in root.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed += 1

    _print_success(f"Cleaned {removed} items.")
    return 0


def _show_help() -> NoReturn:
    """Display help message and exit."""
    help_text = """
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
""".format(**_COLORS, header=_COLORS["bold"] + _COLORS["cyan"])

    print(help_text)
    raise SystemExit(0)


# ================================
# MAIN ENTRY POINT
# ================================

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


def main() -> NoReturn:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        _show_help()

    command = sys.argv[1].lower()
    extra_args = sys.argv[2:] if len(sys.argv) > 2 else None

    if command not in _COMMANDS:
        _print_error(f"Unknown command: {command}")
        print(f"Run '{_colorize('uv run pypaginate --help', 'cyan')}' for available commands.")
        raise SystemExit(1)

    exit_code = _COMMANDS[command](extra_args)  # type: ignore[operator]
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
