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
    cd py && uv run ty check src

# All Python checks.
py: py-lint py-type py-test

# -- Node / TypeScript (@cyblow/paginate) -----------------------------------

# Build the napi addon + run the TS suite (Bun).
ts-test:
    cd ts && bun run test

# Format + lint.
ts-lint:
    cd ts && bun run format:check
    cd ts && bun run lint

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

# -- Codegen: types from the Rust JSON Schema (the single source of truth) ---

# Export the canonical wire-type JSON Schema from crates/core to schemas/.
schema-gen:
    cargo test -p paginate-core --features schema export_schema

# Regenerate the Python types from that schema: lean dataclasses for the core +
# Pydantic v2 models for the [fastapi] extra. (TS types via json-schema-to-typescript
# --unreachableDefinitions, and the PyO3 _core.pyi stub via pyo3-stub-gen, are
# wired as separate steps.) Shapes live once in Rust; this just renders them.
gen: schema-gen
    mkdir -p py/src/pypaginate/_generated
    uvx --from datamodel-code-generator datamodel-codegen \
        --input schemas/paginate.schema.json --input-file-type jsonschema \
        --output-model-type dataclasses.dataclass --target-python-version 3.11 \
        --use-standard-collections --use-union-operator \
        --use-schema-description --use-field-description \
        --enum-field-as-literal all --disable-timestamp \
        --output py/src/pypaginate/_generated/types.py
    uvx --from datamodel-code-generator datamodel-codegen \
        --input schemas/paginate.schema.json --input-file-type jsonschema \
        --output-model-type pydantic_v2.BaseModel --target-python-version 3.11 \
        --use-standard-collections --use-union-operator \
        --use-schema-description --use-field-description \
        --enum-field-as-literal all --disable-timestamp \
        --output py/src/pypaginate/adapters/fastapi/_models.py
    cd py && uv run ruff format src/pypaginate/_generated/types.py src/pypaginate/adapters/fastapi/_models.py
