"""Sphinx-polyversion configuration for pypaginate documentation.

This file configures multi-version documentation builds using sphinx-polyversion.
Run with: uv run sphinx-polyversion docs/poly.py

Uses a custom UV-based environment builder for fast, reproducible builds.
"""

from __future__ import annotations

import asyncio
import os
from asyncio.subprocess import PIPE
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Any, cast

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.builder import BuildError
from sphinx_polyversion.driver import DefaultDriver
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate, refs_by_type
from sphinx_polyversion.pyvenv import VirtualPythonEnvironment
from sphinx_polyversion.sphinx import SphinxBuilder


if TYPE_CHECKING:
    from typing import Self

# =============================================================================
# UV Environment Builder
# =============================================================================


class Uv(VirtualPythonEnvironment):
    """Build Environment for isolated builds with uv.

    Use this to use uv to create an isolated python venv for each
    build and to install specific dependency groups.

    Parameters
    ----------
    path : Path
        The path of the current revision.
    name : str
        The name of the environment (usually the name of the revision).
    args : Iterable[str]
        The cmd arguments to pass to `uv sync` (e.g., ["--group", "docs"]).
    env : dict[str, str], optional
        A dictionary of environment variables which are overridden in the
        virtual environment, by default None.
    venv_name : str, optional
        Name of the venv directory, by default ".venv-docs".

    """

    def __init__(
        self,
        path: Path,
        name: str,
        *,
        args: Iterable[str],
        env: dict[str, str] | None = None,
        venv_name: str = ".venv-docs",
    ):
        """Build Environment for isolated builds using uv.

        Parameters
        ----------
        path : Path
            The path of the current revision.
        name : str
            The name of the environment (usually the name of the revision).
        args : Iterable[str]
            The cmd arguments to pass to `uv sync`.
        env : dict[str, str], optional
            A dictionary of environment variables which are forwarded to the
            virtual environment, by default None.
        venv_name : str, optional
            Name of the venv directory, by default ".venv-docs".

        """
        # Find a unique venv path
        venv_path = path / venv_name
        i = 0
        while venv_path.exists():
            venv_path = path / f"{venv_name}-{i}"
            i += 1

        super().__init__(
            path,
            name,
            venv_path,
            env=env,
        )
        self.args = list(args)

    async def __aenter__(self) -> Self:
        """Set the uv venv up.

        Raises
        ------
        BuildError
            Running `uv sync` failed.

        """
        # Run uv sync to create venv and install deps
        self.logger.info("`uv sync`")

        cmd: list[str] = ["uv", "sync", "--python-preference", "only-managed"]
        cmd += self.args

        env = os.environ.copy()
        self.apply_overrides(env)

        # Set UV_PROJECT_ENVIRONMENT to control where uv creates the venv
        env["UV_PROJECT_ENVIRONMENT"] = str(self.venv)
        env.pop("VIRTUAL_ENV", None)  # Unset any active venv

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.path,
            env=env,
            stdout=PIPE,
            stderr=PIPE,
        )
        out, err = await process.communicate()
        out_str = out.decode(errors="ignore")
        err_str = err.decode(errors="ignore")

        self.logger.debug("Installation output:\n %s", out_str)
        if process.returncode != 0:
            self.logger.error("Installation error:\n %s", err_str)
            raise BuildError from CalledProcessError(
                cast(int, process.returncode), " ".join(cmd), out_str, err_str
            )

        return self

    @classmethod
    def factory(
        cls,
        *,
        args: Iterable[str],
        env: dict[str, str] | None = None,
        venv_name: str = ".venv-docs",
    ) -> Callable[[Path, str], Uv]:
        """Create a factory function for Uv environments.

        This is useful for passing to DefaultDriver as the `env` parameter.

        Parameters
        ----------
        args : Iterable[str]
            The cmd arguments to pass to `uv sync`.
        env : dict[str, str], optional
            Environment variables to override.
        venv_name : str, optional
            Name of the venv directory.

        Returns
        -------
        Callable[[Path, str], Uv]
            A factory function that creates Uv instances.

        """
        args_list = list(args)

        def _factory(path: Path, name: str) -> Uv:
            return cls(path, name, args=args_list, env=env, venv_name=venv_name)

        return _factory


# =============================================================================
# Configuration
# =============================================================================

#: Regex matching the branches to build docs for
BRANCH_REGEX = r"^main$"

#: Regex matching the tags to build docs for (semantic versioning)
TAG_REGEX = r"^v\d+\.\d+\.\d+$"

#: Output dir relative to project root
OUTPUT_DIR = "site"

#: Source directory (where conf.py lives)
SOURCE_DIR = "docs"

#: Arguments to pass to `sphinx-build`
SPHINX_ARGS = "-a -v"

#: Arguments to pass to `uv sync`
UV_ARGS = ["--frozen", "--group", "docs", "--all-extras"]

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


def data(driver: DefaultDriver, rev: GitRef, env: Any) -> dict[str, Any]:  # noqa: ARG001
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


def root_data(driver: DefaultDriver) -> dict[str, Any]:
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
    env=Uv.factory(
        args=UV_ARGS,
        venv_name=".venv-docs",
    ),
    # Note: Don't set template_dir - use polyversion's default root templates
    # The templates in _templates/ are Sphinx templates that extend RTD theme
    static_dir=root / src / "_static",
    data_factory=data,
    root_data_factory=root_data,
    mock=MOCK_DATA,
).run(MOCK, SEQUENTIAL)
