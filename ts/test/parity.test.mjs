// Cross-language parity: the Node/TS binding must agree with the frozen golden
// in tests/fixtures/parity.json — the same fixture the Rust core
// (crates/core/tests/parity.rs) and Python binding
// (py/tests/property/test_cross_language_parity.py) assert against. All three
// must encode identical cursor bytes and return identical filter/sort/search
// indices. See tests/fixtures/generate_parity.py to regenerate the golden.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import * as p from "../dist/index.js";

const fixture = JSON.parse(
  readFileSync(new URL("../../tests/fixtures/parity.json", import.meta.url), "utf8"),
);

// Typed scalars cross the JS boundary as their tagged wire object, which encodes
// byte-identically to Python's real datetime/Decimal/UUID and Rust's typed Value.
test("cursor encode matches the golden (plain + typed)", () => {
  for (const c of [...fixture.cursors, ...fixture.cursors_typed]) {
    assert.equal(p.encodeCursor(c.values), c.encoded, JSON.stringify(c.values));
  }
});

// JS has no datetime/decimal/uuid types, so only plain-scalar cursors round-trip
// without host-type loss (typed values come back as strings — by design).
test("plain cursor round-trips byte-identically", () => {
  for (const c of fixture.cursors) {
    assert.deepEqual(p.decodeCursor(c.encoded), c.values);
  }
});

test("filter indices match the golden", () => {
  for (const c of fixture.filter) {
    const specs = c.specs.map(([field, op, value, logic]) => ({ field, op, value, logic }));
    assert.deepEqual(p.filterIndices(c.items, specs), c.expected, JSON.stringify(c.specs));
  }
});

test("sort indices match the golden", () => {
  for (const c of fixture.sort) {
    const specs = c.specs.map(([field, direction, nulls]) => ({ field, direction, nulls }));
    assert.deepEqual(p.sortIndices(c.items, specs), c.expected, JSON.stringify(c.specs));
  }
});

test("search indices match the golden", () => {
  for (const c of fixture.search) {
    assert.deepEqual(
      p.searchIndices(c.items, c.query, c.fields, { mode: c.mode }),
      c.expected,
      c.query,
    );
  }
});
