"""Architecture tests: CLAUDE.md size limits over ``src/pypaginate``.

Every ``.py`` module under ``src/pypaginate`` -- excluding the machine
generated code in ``_generated/`` and ``.pyi`` stub files -- must respect the
project's hard limits:

* at most 250 *code* lines per file, where blank lines, comment lines, and
  docstring lines are not counted;
* at most 15 *body* lines per function, excluding the docstring.

Counting is AST driven, as required: a function's body lines are the distinct
source lines on which its statements begin (nested function/class scopes count
only their ``def``/``class`` line and are checked independently). This means a
single multi-line literal -- e.g. a ``return {...}`` spanning many physical
lines -- counts as one declarative line rather than many.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "pypaginate"
REPO_ROOT = SRC_ROOT.parents[1]
MAX_FILE_CODE_LINES = 250
MAX_FUNCTION_BODY_LINES = 15

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef
ScopeNode = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


def _source_files() -> list[Path]:
    """Return the source files subject to the size limits."""
    return sorted(
        path
        for path in SRC_ROOT.rglob("*.py")
        if path.suffix == ".py" and "_generated" not in path.parts
    )


def _label(path: Path) -> str:
    """Repo-relative label used as a readable parametrize id."""
    return str(path.relative_to(REPO_ROOT))


def _is_docstring(stmt: ast.stmt) -> bool:
    """Whether ``stmt`` is a bare string expression (a docstring-like line)."""
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def _docstring_lines(tree: ast.AST) -> set[int]:
    """Line numbers occupied by docstrings / bare string statements."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if _is_docstring(node):
            end = node.end_lineno or node.lineno
            lines.update(range(node.lineno, end + 1))
    return lines


def _count_code_lines(path: Path) -> int:
    """Count code lines, excluding blanks, comments, and docstrings."""
    source = path.read_text(encoding="utf-8")
    skip = _docstring_lines(ast.parse(source))
    count = 0
    for number, raw in enumerate(source.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or number in skip:
            continue
        count += 1
    return count


def _add_statement_lines(node: ast.AST, lines: set[int]) -> None:
    """Record statement linenos, not descending into nested scopes."""
    if isinstance(node, ScopeNode):
        lines.add(node.lineno)
        return
    if isinstance(node, ast.stmt):
        lines.add(node.lineno)
    for child in ast.iter_child_nodes(node):
        _add_statement_lines(child, lines)


def _function_body_lines(func: FunctionNode) -> int:
    """Distinct statement linenos in ``func``'s body, minus its docstring."""
    body = func.body[1:] if func.body and _is_docstring(func.body[0]) else func.body
    lines: set[int] = set()
    for stmt in body:
        _add_statement_lines(stmt, lines)
    return len(lines)


def _all_functions() -> list[tuple[str, int]]:
    """Every function as a ``(label, body_line_count)`` pair."""
    items: list[tuple[str, int]] = []
    for path in _source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, FunctionNode):
                label = f"{_label(path)}::{node.name}:{node.lineno}"
                items.append((label, _function_body_lines(node)))
    return items


_FUNCTIONS = _all_functions()


@pytest.mark.unit
def test_source_files_are_discovered() -> None:
    """Guard against a broken path silently making the suite vacuous."""
    assert _source_files(), f"no source files found under {SRC_ROOT}"


@pytest.mark.unit
def test_functions_are_discovered() -> None:
    """Guard against the function walk silently finding nothing."""
    assert _FUNCTIONS, "no functions discovered in src/pypaginate"


@pytest.mark.unit
@pytest.mark.parametrize("path", _source_files(), ids=_label)
def test_file_within_code_line_limit(path: Path) -> None:
    """A module must not exceed the 250 code-line hard limit."""
    count = _count_code_lines(path)
    assert count <= MAX_FILE_CODE_LINES, (
        f"{_label(path)} has {count} code lines, over the {MAX_FILE_CODE_LINES} limit"
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("label", "body_lines"),
    _FUNCTIONS,
    ids=[label for label, _ in _FUNCTIONS],
)
def test_function_within_body_line_limit(label: str, body_lines: int) -> None:
    """A function body must not exceed the 15 line hard limit."""
    assert body_lines <= MAX_FUNCTION_BODY_LINES, (
        f"{label} has {body_lines} body lines, over the {MAX_FUNCTION_BODY_LINES} limit"
    )
