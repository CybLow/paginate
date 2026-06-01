// Tests for the built package (run `npm test`, which compiles first).
import { test } from "node:test";
import assert from "node:assert/strict";

import * as p from "../dist/index.js";

test("cursor encode is byte-compatible with the Python codec", () => {
  assert.equal(p.encodeCursor([1, "a"]), "WzEsImEiXQ");
});

test("cursor round-trips (incl. ISO datetime string + null + bool)", () => {
  const values = ["2025-06-01T00:00:00", 42, null, true];
  assert.deepEqual(p.decodeCursor(p.encodeCursor(values)), values);
});

test("offset pagination math", () => {
  assert.equal(p.offset(3, 20), 40);
  assert.equal(p.maxPages(101, 20), 6);
  assert.equal(p.clampPage(10, 20, 100), 5);
  assert.deepEqual(p.offsetMeta(1, 20, 100), {
    page: 1,
    pages: 5,
    hasNext: true,
    hasPrevious: false,
  });
});

test("text normalization matches the core (accent strip + lower)", () => {
  assert.equal(p.normalize("  Héllo   WORLD "), "hello world");
});

test("filter / sort / search semantics (behaviour parity)", () => {
  const items = [
    { id: 1, name: "Alice", age: 30 },
    { id: 2, name: "Bob", age: 17 },
    { id: 3, name: "Cara", age: 45 },
  ];
  assert.deepEqual(
    p.filterIndices(items, [{ field: "age", op: "gte", value: 18, logic: "and" }]),
    [0, 2],
  );
  assert.deepEqual(p.sortIndices(items, [{ field: "age", direction: "desc" }]), [2, 0, 1]);
  assert.deepEqual(p.searchIndices(items, "a", ["name"]), [0, 2]);
});
