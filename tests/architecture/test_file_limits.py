"""Architecture tests verifying CLAUDE.md file size constraints.

Ensures no source file in src/pypaginate/ (excluding _cli/) exceeds
the 200-line hard limit defined in the project standards.
"""

from __future__ import annotations

from pathlib import Path

import pytest


SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "pypaginate"
MAX_LINES = 200


def _source_files() -> list[Path]:
    """Collect all .py files in src/pypaginate/ excluding _cli/."""
    files = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        if "/_cli/" in str(path) or path.parent.name == "_cli":
            continue
        files.append(path)
    return files


def _count_lines(filepath: Path) -> int:
    """Count non-empty lines in a file."""
    return len(filepath.read_text(encoding="utf-8").splitlines())


def _file_label(filepath: Path) -> str:
    """Create a short label relative to src root."""
    return str(filepath.relative_to(SRC_ROOT.parent.parent))


@pytest.mark.parametrize(
    "filepath",
    _source_files(),
    ids=lambda p: _file_label(p),
)
def test_file_does_not_exceed_line_limit(filepath):
    """Source file must not exceed 200 lines."""
    line_count = _count_lines(filepath)
    assert line_count <= MAX_LINES, (
        f"{filepath.name} has {line_count} lines, exceeding the {MAX_LINES}-line limit"
    )
