"""CLI command implementations.

Each cmd_* function implements a specific development command.
"""

from __future__ import annotations

import subprocess
import sys

from pypaginate._cli.build import cmd_build, cmd_clean
from pypaginate._cli.output import _colorize, _print_error, _print_header, _print_success
from pypaginate._cli.runner import _run


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
]


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


_COV_ARGS: list[str] = [
    "pytest",
    "--cov=pypaginate",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
]


def cmd_test_cov(extra_args: list[str] | None = None) -> int:
    """Run tests with coverage report."""
    _print_header("Running Tests with Coverage")
    args = [*_COV_ARGS]
    if extra_args:
        args.extend(extra_args)
    result = _run(*args, check=False)
    if result.returncode == 0:
        _print_success("Tests passed! Coverage report generated in htmlcov/")
    return result.returncode


def _run_checks(
    title: str,
    checks: list[tuple[str, list[str]]],
) -> int:
    """Run a list of quality checks and report results.

    Args:
        title: Header title for the check group.
        checks: List of (name, command) tuples.

    Returns:
        0 if all checks pass, 1 otherwise.
    """
    _print_header(title)
    failed = _execute_checks(checks)
    print()
    if failed:
        return _report_failures(failed)
    _print_success(f"All checks passed! ({title})")
    return 0


def _execute_checks(
    checks: list[tuple[str, list[str]]],
) -> list[tuple[str, subprocess.CompletedProcess[str]]]:
    """Execute checks and return failed ones."""
    failed: list[tuple[str, subprocess.CompletedProcess[str]]] = []
    for name, cmd in checks:
        print(f"  {_colorize('→', 'cyan')} {name}...", end=" ", flush=True)
        result = _run(*cmd, check=False, capture=True)
        if result.returncode == 0:
            print(_colorize("✓", "green"))
        else:
            print(_colorize("✗", "red"))
            failed.append((name, result))
    return failed


def _report_failures(
    failed: list[tuple[str, subprocess.CompletedProcess[str]]],
) -> int:
    """Print failure details and return exit code 1."""
    _print_error(f"{len(failed)} check(s) failed:")
    for name, result in failed:
        print(f"  • {name}")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    return 1


_QUALITY_CHECKS: list[tuple[str, list[str]]] = [
    ("Formatting check", ["ruff", "format", "--check", "src", "tests"]),
    ("Linting", ["ruff", "check", "src", "tests"]),
    ("Tests", ["pytest", "-q"]),
]

_STRICT_QUALITY_CHECKS: list[tuple[str, list[str]]] = [
    ("Formatting check", ["ruff", "format", "--check", "src", "tests"]),
    ("Linting", ["ruff", "check", "src", "tests"]),
    ("Type checking", ["mypy", "src"]),
    ("Tests", ["pytest", "-q"]),
]


def cmd_quality(extra_args: list[str] | None = None) -> int:  # noqa: ARG001
    """Run essential quality checks (format, lint, test)."""
    return _run_checks("Running Quality Checks", _QUALITY_CHECKS)


def cmd_quality_strict(extra_args: list[str] | None = None) -> int:  # noqa: ARG001
    """Run all quality checks including mypy type checking."""
    return _run_checks("Running Strict Quality Checks", _STRICT_QUALITY_CHECKS)
