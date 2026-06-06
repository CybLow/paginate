"""Core performance benchmarks for the new pypaginate public API.

Every module here drives the ``benchmark`` fixture, so the suite only runs under
``--run-benchmark`` (the CI Benchmarks lane adds ``--run-slow`` for the scaling
curves). These cover the core ops only — filter / sort / search / paginate plus
``Dataset.page`` — over deterministic factory data; no external-library
comparisons live here.
"""
