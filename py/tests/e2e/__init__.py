"""End-to-end scenario tests — full filter/sort/search/paginate journeys.

Every test in this package is built against the *new* public API
(:func:`pypaginate.paginate`, :func:`pypaginate.filter` / ``sort`` / ``search``,
:class:`pypaginate.Dataset`, and the framework adapters) — there are no engine or
backend imports. The root ``conftest.py`` auto-marks everything here ``e2e``.
"""

from __future__ import annotations
