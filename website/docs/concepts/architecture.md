---
sidebar_position: 1
---

# Architecture — fat core, thin adapters

All computation lives **once** in the Rust core (`paginate-core`): filtering (20
operators + nested And/Or groups), stable multi-key sorting with null placement,
ranked + fuzzy (trigram) search, the cursor codec, the keyset predicate, and
pagination math.

The language packages are **thin adapters**:

- they marshal your objects / ORM rows into the plain data the core understands;
- the core returns **indices**, and the adapter selects your original objects — rows
  are never copied or validated through the binding (zero per-row cost);
- validation rules, wire tokens, and limits live in the core too, so the packages
  delegate rather than re-implement.

```text
            paginate-core (Rust) — algorithms + validation + wire contract
                 │  plain data  ↔  indices
        ┌────────┴────────┐
   pypaginate (PyO3)   @cyblow/paginate (napi)
   thin typed adapter   thin typed adapter
```

## Generated types

The type **shapes** (filter / sort / search specs, params, page metadata, enums) are
generated from a single JSON Schema emitted by the core. The Python package renders
them as dataclasses and the TypeScript package as interfaces, so the two can't drift
and both match the Rust source.

## Adapters

In-memory pagination needs no adapter — the core *is* the engine, reached through the
top-level `paginate` / `filter` / `sort` / `search` and `Dataset`. Adapters exist only
to bridge systems the core can't see: **SQLAlchemy**, **Django**, and **FastAPI** in
Python; **Prisma**, **Drizzle**, and **Express** in TypeScript.
