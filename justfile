# paginate monorepo task runner — unifies the Rust core, the Python (pypaginate)
# and the Node/TS (@cyblow/paginate) lanes behind one command set.
# Install just: https://github.com/casey/just   ·   Run `just` to list recipes.

# Default: show the recipe list.
default:
    @just --list

# -- Rust core + bindings ---------------------------------------------------

# Format check (workspace + the excluded pyo3 crate).
rust-fmt:
    cargo fmt --all --check
    cargo fmt --manifest-path crates/pyo3/Cargo.toml --check

# Clippy with warnings denied (workspace + pyo3).
rust-lint:
    cargo clippy --workspace --all-targets -- -D warnings
    cargo clippy --manifest-path crates/pyo3/Cargo.toml --all-targets -- -D warnings

# Tests (workspace + pyo3).
rust-test:
    cargo test --workspace
    cargo test --manifest-path crates/pyo3/Cargo.toml

# All Rust checks.
rust: rust-fmt rust-lint rust-test

# -- Python (pypaginate) ----------------------------------------------------

# Build the native _core extension into the dev venv.
py-build:
    cd py && uv run maturin develop

# Run the Python suite (no benchmarks, no perf) after building the ext.
py-test: py-build
    cd py && uv run pytest -q -p no:benchmark --ignore=tests/perf

# Format + lint.
py-lint:
    cd py && uv run ruff format --check src tests
    cd py && uv run ruff check src tests

# Type-check.
py-type:
    cd py && uv run mypy src

# All Python checks.
py: py-lint py-type py-test

# -- Node / TypeScript (@cyblow/paginate) -----------------------------------

# Build the napi addon + run the TS suite.
ts-test:
    npm --prefix ts test

# Format + lint.
ts-lint:
    npm --prefix ts run format:check
    npm --prefix ts run lint

# All TS checks.
ts: ts-lint ts-test

# -- Cross-cutting ----------------------------------------------------------

# Just the tests, every language.
test: rust-test py-test ts-test

# The full gate, every language (what CI enforces).
all: rust py ts

# Regenerate the frozen cross-language parity golden (tests/fixtures/parity.json).
parity-gen:
    cd py && uv run python ../tests/fixtures/generate_parity.py
