// Tests for the built package (run `npm test`, which compiles first).
import { test } from "node:test";
import assert from "node:assert/strict";

import * as p from "../dist/index.js";

const PEOPLE = [
  { id: 1, name: "Alice", age: 30 },
  { id: 2, name: "Bob", age: 17 },
  { id: 3, name: "Cara", age: 45 },
];

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

test("one-shot filter / sort / search semantics", () => {
  assert.deepEqual(p.filterIndices(PEOPLE, [{ field: "age", operator: "gte", value: 18 }]), [0, 2]);
  assert.deepEqual(p.sortIndices(PEOPLE, [{ field: "age", direction: "desc" }]), [2, 0, 1]);
  assert.deepEqual(p.searchIndices(PEOPLE, { query: "a", fields: ["name"] }), [0, 2]);
});

test("legacy `op` alias still accepted by the binding", () => {
  assert.deepEqual(p.filterIndices(PEOPLE, [{ field: "age", op: "gte", value: 18 }]), [0, 2]);
});

test("And() / Or() build nested filter groups", () => {
  // (name == "Alice" OR name == "Cara") AND age >= 18  ->  Alice, Cara
  const group = p.And(
    p.Or(
      { field: "name", operator: "eq", value: "Alice" },
      { field: "name", operator: "eq", value: "Cara" },
    ),
    { field: "age", operator: "gte", value: 18 },
  );
  assert.deepEqual(p.filterGroupIndices(PEOPLE, group), [0, 2]);
  assert.deepEqual(p.filterGroupIndices(PEOPLE, { field: "age", operator: "lt", value: 18 }), [1]);
});

test("Dataset: resident filter / sort / search map indices back to rows", () => {
  const ds = new p.Dataset(PEOPLE);
  assert.equal(ds.size, 3);
  assert.deepEqual(ds.filter([{ field: "age", operator: "gte", value: 18 }]), [
    PEOPLE[0],
    PEOPLE[2],
  ]);
  assert.deepEqual(ds.sort([{ field: "age", direction: "desc" }]), [
    PEOPLE[2],
    PEOPLE[0],
    PEOPLE[1],
  ]);
  assert.deepEqual(ds.search({ query: "a", fields: ["name"] }), [PEOPLE[0], PEOPLE[2]]);
});

test("OffsetParams: defaults, offset, and validation", () => {
  assert.equal(new p.OffsetParams().offset, 0);
  assert.equal(new p.OffsetParams({ page: 3, limit: 20 }).offset, 40);
  assert.throws(() => new p.OffsetParams({ page: 0 }), p.ValidationError);
  assert.throws(() => new p.OffsetParams({ limit: 0 }), p.ValidationError);
  assert.throws(() => new p.OffsetParams({ limit: p.MAX_LIMIT + 1 }), p.ValidationError);
});

test("OffsetParams.clamp", () => {
  assert.equal(new p.OffsetParams({ page: 10, limit: 5 }).clamp(20).page, 4);
  const within = new p.OffsetParams({ page: 2, limit: 10 });
  assert.equal(within.clamp(50), within); // unchanged -> same instance
  assert.equal(new p.OffsetParams({ page: 5, limit: 10 }).clamp(0).page, 1);
});

test("CursorParams: after/before are mutually exclusive", () => {
  assert.equal(new p.CursorParams({ after: "abc" }).after, "abc");
  assert.throws(() => new p.CursorParams({ after: "a", before: "b" }), p.ValidationError);
});

test("paginate(): filter + sort + offset page over an array", () => {
  const items = Array.from({ length: 25 }, (_, i) => ({ id: i, age: i }));
  const page = p.paginate(items, new p.OffsetParams({ page: 1, limit: 10 }), {
    filters: [{ field: "age", operator: "gte", value: 5 }],
    sorting: [{ field: "age", direction: "desc" }],
  });
  assert.equal(page.total, 20); // ages 5..24
  assert.equal(page.pages, 2);
  assert.equal(page.hasNext, true);
  assert.equal(page.hasPrevious, false);
  assert.equal(page.items.length, 10);
  assert.deepEqual(page.items[0], { id: 24, age: 24 });
  assert.deepEqual(page.items.at(-1), { id: 15, age: 15 });
});

test("Dataset.page equals the one-shot filter+sort+slice path", () => {
  const items = Array.from({ length: 50 }, (_, i) => ({ id: i, score: (i * 7) % 13 }));
  const ds = new p.Dataset(items);
  const filter = [{ field: "score", operator: "lt", value: 6 }];
  const sorting = [{ field: "id", direction: "asc" }];
  const filtered = p.filterIndices(items, filter).map((i) => items[i]);
  const sorted = p.sortIndices(filtered, sorting).map((i) => filtered[i]);
  const expected = sorted.slice(0, 8);
  const page = ds.page(new p.OffsetParams({ page: 1, limit: 8 }), { filters: filter, sorting });
  assert.deepEqual(page.items, expected);
});

test("Dataset.page applies search as a match-filter (explicit sorting wins)", () => {
  const items = [
    { id: 1, name: "Alice" },
    { id: 2, name: "Bob" },
    { id: 3, name: "Cara" },
    { id: 4, name: "Dan" },
  ];
  const ds = new p.Dataset(items);
  const page = ds.page(new p.OffsetParams({ page: 1, limit: 10 }), {
    search: { query: "a", fields: ["name"], mode: "contains", fuzzy: "exact", threshold: 30 },
    sorting: [{ field: "id", direction: "desc" }],
  });
  // contains "a": Alice, Cara, Dan (not Bob); sorted id desc -> Dan, Cara, Alice.
  assert.deepEqual(
    page.items.map((r) => r.name),
    ["Dan", "Cara", "Alice"],
  );
  assert.equal(page.total, 3);
});

test("keysetTerms: lexicographic OR-of-AND predicate structure", () => {
  assert.deepEqual(p.keysetTerms([true]), [[[0, "gt"]]]);
  assert.deepEqual(p.keysetTerms([true, false]), [
    [[0, "gt"]],
    [
      [0, "eq"],
      [1, "lt"],
    ],
  ]);
});

test("offsetPage / cursorPage builders", () => {
  const op = p.offsetPage([1, 2, 3], 100, new p.OffsetParams({ page: 1, limit: 20 }));
  assert.equal(op.total, 100);
  assert.equal(op.pages, 5);
  assert.equal(op.hasNext, true);
  assert.equal(op.hasPrevious, false);

  const cp = p.cursorPage([1, 2], new p.CursorParams({ limit: 20 }), { nextCursor: "xyz" });
  assert.equal(cp.hasNext, true);
  assert.equal(cp.nextCursor, "xyz");
  assert.equal(cp.hasPrevious, false);
  assert.equal(cp.previousCursor, null);
});
