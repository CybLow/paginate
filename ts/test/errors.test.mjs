// Core engine failures surface as the typed FilterError / SortError /
// SearchError (parity with pypaginate's exception taxonomy), not a bare Error.
import { test } from "node:test";
import assert from "node:assert/strict";

import * as p from "../dist/index.js";

const rows = [{ name: "alice" }, { name: "bob" }];
const badRegex = { field: "name", operator: "regex", value: "[" };

test("filterIndices re-types a core engine error as FilterError", () => {
  assert.throws(
    () => p.filterIndices(rows, [badRegex]),
    (e) => e instanceof p.FilterError && e instanceof p.PaginateError,
  );
});

test("Dataset.filter re-types a core engine error as FilterError", () => {
  const ds = new p.Dataset(rows);
  assert.throws(
    () => ds.filter([badRegex]),
    (e) => e instanceof p.FilterError,
  );
});

test("Dataset.page re-types a filter-stage error via the message prefix", () => {
  const ds = new p.Dataset(rows);
  assert.throws(
    () => ds.page(new p.OffsetParams({ page: 1, limit: 10 }), { filters: [badRegex] }),
    (e) => e instanceof p.FilterError,
  );
});
