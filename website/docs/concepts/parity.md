---
sidebar_position: 2
---

# Cross-language parity

Because the engine has a single implementation, the Python and TypeScript packages
return **identical results** — the same filtered / sorted / ranked order — and
**byte-identical cursors**.

A frozen golden fixture (`tests/fixtures/parity.json`) is asserted by all three
languages in CI: the Rust core, `pypaginate`, and `@cyblow/paginate` must each
reproduce it exactly. It covers:

- all 20 filter operators (incl. `in` / `not_in`, `between`, `is_null`, `regex`,
  `empty` / `not_empty`, `exists`) and AND/OR logic,
- sort direction with null placement (`first` / `last`),
- search modes (`contains` / `prefix` / `exact`),
- the cursor codec, including typed values (datetime, date, decimal, uuid).

The practical payoff: a cursor minted by a Python service decodes byte-for-byte in a
TypeScript client, and a filter expression behaves the same everywhere.
