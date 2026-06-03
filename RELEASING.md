# Releasing

This monorepo ships **three independently-versioned artifacts** from one `main`,
automated by [release-please](https://github.com/googleapis/release-please)
(manifest mode). You never hand-edit versions or hand-tag.

| Artifact | Path | Registry / name | Tag | Workflow |
|----------|------|-----------------|-----|----------|
| Engine | `crates/core` | crates.io · `paginate-core` | `core-v*` | `release-crate.yml` |
| Python | `py/` (binding `crates/pyo3`) | PyPI · `pypaginate` | `py-v*` | `release-python.yml` |
| Node/TS | `ts/` (binding `crates/node`) | npm · `@cyblow/paginate` | `ts-v*` | `release-npm.yml` |

## The flow

1. **Land Conventional Commits on `main`** (squash-merged PRs). `feat:` → minor,
   `fix:`/`perf:` → patch, `feat!:`/`BREAKING CHANGE:` → major. The **scope**
   selects the package (`feat(core):`, `fix(py):`, `feat(ts):`).
2. **release-please opens a "Release" PR per package** that bumped, updating the
   version + `CHANGELOG.md`. Config: [`release-please-config.json`](release-please-config.json),
   state: [`.release-please-manifest.json`](.release-please-manifest.json).
3. **Merge the Release PR.** release-please tags the merge commit
   (`core-vX.Y.Z` / `py-vX.Y.Z` / `ts-vX.Y.Z`).
4. **The tag triggers exactly one release workflow** (table above).

### Version lockstep (handled by `extra-files`)

- `crates/core` version is **concrete** in its `Cargo.toml` (release-please-rust
  bumps it). Other crate metadata stays workspace-inherited.
- A `py` release also bumps `crates/pyo3/Cargo.toml` (`extra-files`) — the wheel's
  binding crate tracks the `pypaginate` version.
- A `ts` release also bumps `crates/node/package.json` (`extra-files`) — the napi
  package `paginate-core` is published alongside `@cyblow/paginate`.

## Always dry-run first

Every release workflow has a `workflow_dispatch` dry-run:

```bash
gh workflow run release-python.yml -f dry_run=true   # multi-platform wheels → TestPyPI
gh workflow run release-npm.yml    -f dry_run=true   # npm publish --dry-run (+ platform .node)
gh workflow run release-crate.yml  -f dry_run=true   # cargo publish --dry-run
```

## One-time registry setup (gated — requires maintainer action)

> Do this **before** the first real release, and **re-do the PyPI step after the
> repo rename** — OIDC trust is keyed to `owner/repo/workflow`, so a rename
> silently breaks publishing until reconfigured.

- **PyPI (OIDC trusted publishing, no token):** on PyPI → project `pypaginate` →
  *Publishing* → add a trusted publisher: owner `CybLow`, repo `paginate`,
  workflow `release-python.yml`, environment `pypi`. Pre-release tags
  (`py-v*-rc*`) publish to **TestPyPI** (add the matching trusted publisher there).
- **npm:** create the `@cyblow` org; add `NPM_TOKEN` (automation) as a repo secret
  (or configure npm OIDC). `release-npm.yml` publishes the napi package
  `paginate-core` **plus its platform sub-packages** (`napi prepublish -t npm`),
  then `@cyblow/paginate`.
- **crates.io:** own the `paginate-core` name; add `CARGO_REGISTRY_TOKEN` as a
  repo secret for `release-crate.yml`.

## Supply-chain hardening (Python)

`release-python.yml` attaches a **CycloneDX SBOM** and a **SLSA build provenance
attestation** to the wheels, and runs `twine check` before publish.

## Manual fallback (only if automation is down)

```bash
# Python:  build wheels locally and upload (needs a PyPI token, not OIDC)
cd py && uv run maturin build --release --manifest-path ../crates/pyo3/Cargo.toml
# Crate:
cargo publish -p paginate-core
# npm:
cd crates/node && npm run build && npm publish && cd ../../ts && npm publish
```
