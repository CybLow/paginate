"""Run the example scripts end-to-end so they can never drift from the API.

The ``examples/`` scripts are referenced from the README and docs; executing them
in CI guarantees the documented usage still imports and runs against the shipped
package. Each is run via ``runpy`` from its file path (no import-path setup), and
the FastAPI example is exercised through a ``TestClient`` instead of launching a
server.
"""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.integration

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


@pytest.mark.parametrize("name", ["basic_pagination", "filtering", "keyset_pagination"])
def test_example_script_runs(name: str) -> None:
    """The script executes its ``main()`` without raising."""
    runpy.run_path(str(EXAMPLES / f"{name}.py"), run_name="__main__")


def test_fastapi_example_serves() -> None:
    """The FastAPI example app paginates and rejects invalid params (HTTP 422)."""
    namespace = runpy.run_path(str(EXAMPLES / "fastapi_integration.py"))
    with TestClient(namespace["app"]) as client:
        ok = client.get("/users", params={"page": 1, "limit": 5})
        assert ok.status_code == 200
        assert ok.json()["total"] == 100

        bad = client.get("/users", params={"page": 0})
        assert bad.status_code == 422
