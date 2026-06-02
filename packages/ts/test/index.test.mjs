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

test("filterGroupIndices: nested And/Or groups", () => {
  const items = [
    { id: 1, name: "Alice", age: 30 },
    { id: 2, name: "Bob", age: 17 },
    { id: 3, name: "Cara", age: 45 },
  ];
  // (name == "Alice" OR name == "Cara") AND age >= 18  ->  Alice, Cara
  const group = {
    logic: "and",
    conditions: [
      {
        logic: "or",
        conditions: [
          { field: "name", op: "eq", value: "Alice" },
          { field: "name", op: "eq", value: "Cara" },
        ],
      },
      { field: "age", op: "gte", value: 18 },
    ],
  };
  assert.deepEqual(p.filterGroupIndices(items, group), [0, 2]);
  // a bare leaf collapses to a single-spec filter
  assert.deepEqual(p.filterGroupIndices(items, { field: "age", op: "lt", value: 18 }), [1]);
});

test("Dataset: resident filter / sort / search map indices back to rows", () => {
  const items = [
    { id: 1, name: "Alice", age: 30 },
    { id: 2, name: "Bob", age: 17 },
    { id: 3, name: "Cara", age: 45 },
  ];
  const ds = new p.Dataset(items);
  assert.equal(ds.size, 3);
  assert.deepEqual(ds.filter([{ field: "age", op: "gte", value: 18, logic: "and" }]), [
    items[0],
    items[2],
  ]);
  assert.deepEqual(ds.sort([{ field: "age", direction: "desc" }]), [items[2], items[0], items[1]]);
  assert.deepEqual(ds.search("a", ["name"]), [items[0], items[2]]);
});

test("Dataset.page: filter + sort + paginate in one native call", () => {
  const items = Array.from({ length: 25 }, (_, i) => ({ id: i, age: i }));
  const ds = new p.Dataset(items);
  const page = ds.page(1, 10, {
    filters: [{ field: "age", op: "gte", value: 5, logic: "and" }],
    sorting: [{ field: "age", direction: "desc" }],
  });
  assert.equal(page.total, 20); // ages 5..24
  assert.equal(page.pages, 2);
  assert.equal(page.hasNext, true);
  assert.equal(page.hasPrevious, false);
  assert.equal(page.items.length, 10);
  assert.deepEqual(page.items[0], { id: 24, age: 24 }); // desc -> 24 first
  assert.deepEqual(page.items.at(-1), { id: 15, age: 15 });
});

test("Dataset.page: equals the one-shot filter+sort+slice path (consistency)", () => {
  const items = Array.from({ length: 50 }, (_, i) => ({ id: i, score: (i * 7) % 13 }));
  const ds = new p.Dataset(items);
  const filter = [{ field: "score", op: "lt", value: 6, logic: "and" }];
  const sorting = [{ field: "id", direction: "asc" }];
  // Reference: one-shot indices -> rows -> sort -> slice the first page.
  const filtered = p.filterIndices(items, filter).map((i) => items[i]);
  const sorted = p.sortIndices(filtered, sorting).map((i) => filtered[i]);
  const expected = sorted.slice(0, 8);
  const page = ds.page(1, 8, { filters: filter, sorting });
  assert.deepEqual(page.items, expected);
});
