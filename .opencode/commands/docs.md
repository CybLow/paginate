# Documentation Workflow

The unified docs site lives in `website/` (Docusaurus). It covers all three packages
(Rust core + Python + TypeScript) — guides, concepts, and a per-language API reference.

## Commands

```bash
cd website

# Generate the Python API reference (pydoc-markdown) — run once before dev
bun run gen:python

# Dev server (hot reload; the TypeScript API reference regenerates via TypeDoc)
bun start

# Full production build (Python ref + TypeDoc + build) — what CI runs
bun run build:full

# Serve the production build locally
bun run serve
```

## Structure

```
website/
├── docusaurus.config.ts   # site config (nav, offline search, TypeDoc plugin)
├── sidebars.ts            # one auto-generated sidebar from docs/
├── pydoc-markdown.yml     # Python API reference config
└── docs/
    ├── intro.md           # Overview (home, slug: /)
    ├── getting-started/   # install + quickstart (tutorial)
    ├── pagination/ filtering/ sorting/ search/ integrations/   # guides (how-to)
    ├── concepts/          # architecture, parity, cursor encoding (explanation)
    ├── reference/         # API: TypeScript (TypeDoc) · Python (pydoc-markdown) · Rust (docs.rs)
    └── migration.md
```

The generated API references (`docs/reference/typescript/`, `docs/reference/python/`)
are gitignored and rebuilt by `bun run build:full`.

## Writing docs

- **Diátaxis**: keep each page one type — tutorial / how-to / reference / explanation.
- Show working, copy-paste examples with **realistic data**; pair Python + TypeScript.
- Use relative `.md` links; lead with the answer; short paragraphs; tables for params.
- Deployed to GitHub Pages by `.github/workflows/docs.yml` on push to `main`.
```
