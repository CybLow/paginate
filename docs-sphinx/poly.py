"""Sphinx-polyversion configuration for pypaginate documentation.

This file configures multi-version documentation builds using sphinx-polyversion.
Run with: uv run sphinx-polyversion docs-sphinx/poly.py
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate, refs_by_type
from sphinx_polyversion.pyvenv import Pip, VenvWrapper
from sphinx_polyversion.sphinx import SphinxBuilder

# =============================================================================
# Configuration
# =============================================================================

#: Regex matching the branches to build docs for
BRANCH_REGEX = r"^main$"

#: Regex matching the tags to build docs for (semantic versioning)
TAG_REGEX = r"^v\d+\.\d+\.\d+$"

#: Output dir relative to project root
OUTPUT_DIR = "_build/html"

#: Source directory (where conf.py lives)
SOURCE_DIR = "docs-sphinx"

#: Arguments to pass to `sphinx-build`
SPHINX_ARGS = "-a -v"

#: Arguments to pass to `pip install`
PIP_ARGS = ["-e", ".[all]"]

#: Mock data used for building local version (when no git tags exist)
MOCK_DATA = {
    "revisions": [
        GitRef("v0.1.0", "", "", GitRefType.TAG, datetime.fromtimestamp(0)),
        GitRef("main", "", "", GitRefType.BRANCH, datetime.fromtimestamp(1)),
    ],
    "current": GitRef("local", "", "", GitRefType.BRANCH, datetime.now()),
}

#: Whether to build using only local files and mock data
MOCK = False

#: Whether to run the builds in sequence or in parallel
SEQUENTIAL = False


# =============================================================================
# Data factories for templates
# =============================================================================


def data(driver: DefaultDriver, rev: GitRef, env) -> dict:
    """Data passed to Sphinx conf.py for each version build."""
    revisions = driver.targets
    branches, tags = refs_by_type(revisions)
    latest = max(tags) if tags else (max(branches) if branches else rev)
    return {
        "current": rev,
        "tags": tags,
        "branches": branches,
        "revisions": revisions,
        "latest": latest,
    }


def root_data(driver: DefaultDriver) -> dict:
    """Data passed to root index template."""
    revisions = driver.builds
    branches, tags = refs_by_type(revisions)
    latest = max(tags) if tags else (max(branches) if branches else None)
    return {
        "revisions": revisions,
        "latest": latest,
    }


# =============================================================================
# Driver setup and execution
# =============================================================================

# Load overrides read from commandline to global scope
apply_overrides(globals())

# Determine repository root directory
root = Git.root(Path(__file__).parent)

# Setup driver and run it
src = Path(SOURCE_DIR)
DefaultDriver(
    root,
    OUTPUT_DIR,
    vcs=Git(
        branch_regex=BRANCH_REGEX,
        tag_regex=TAG_REGEX,
        buffer_size=1 * 10**9,  # 1 GB
        predicate=file_predicate([src]),  # exclude refs without source dir
    ),
    builder=SphinxBuilder(src, args=SPHINX_ARGS.split()),
    env=Pip.factory(
        venv=Path(".venv-docs"),
        args=PIP_ARGS,
        creator=VenvWrapper(),
        temporary=True,  # Create venv in temp dir relative to source path
    ),
    # Note: Don't set template_dir - use polyversion's default root templates
    # The templates in _templates/ are Sphinx templates that extend RTD theme
    static_dir=root / src / "_static",
    data_factory=data,
    root_data_factory=root_data,
    mock=MOCK_DATA,
).run(MOCK, SEQUENTIAL)
