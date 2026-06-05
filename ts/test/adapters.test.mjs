// Tests for the framework / ORM adapters (built package).
import { test } from "node:test";
import assert from "node:assert/strict";

import * as p from "../dist/index.js";

// -- express ----------------------------------------------------------------

test("express: offsetParamsFromQuery parses + validates", () => {
  const params = p.express.offsetParamsFromQuery({ page: "3", limit: "50" });
  assert.equal(params.page, 3);
  assert.equal(params.limit, 50);
  assert.equal(params.offset, 100);
});

test("express: offsetParamsFromQuery defaults + array values", () => {
  const params = p.express.offsetParamsFromQuery({ page: ["2", "9"] });
  assert.equal(params.page, 2); // first value
  assert.equal(params.limit, 20); // default
});

test("express: bad query throws ValidationError", () => {
  assert.throws(() => p.express.offsetParamsFromQuery({ page: "0" }), p.ValidationError);
});

test("express: cursorParamsFromQuery", () => {
  const params = p.express.cursorParamsFromQuery({ limit: "10", after: "abc" });
  assert.equal(params.limit, 10);
  assert.equal(params.after, "abc");
  assert.equal(params.before, null);
});

// -- prisma -----------------------------------------------------------------

test("prisma: offsetArgs", () => {
  assert.deepEqual(p.prisma.offsetArgs(new p.OffsetParams({ page: 3, limit: 20 })), {
    skip: 40,
    take: 20,
  });
});

test("prisma: keysetWhere single ascending key", () => {
  const where = p.prisma.keysetWhere([{ field: "id" }], [42]);
  assert.deepEqual(where, { id: { gt: 42 } });
});

test("prisma: keysetWhere two keys (asc, asc) -> nested OR/AND", () => {
  const where = p.prisma.keysetWhere([{ field: "createdAt" }, { field: "id" }], ["t", 42]);
  assert.deepEqual(where, {
    OR: [{ createdAt: { gt: "t" } }, { AND: [{ createdAt: "t" }, { id: { gt: 42 } }] }],
  });
});

test("prisma: keysetWhere honors desc + backwards flip", () => {
  const fwd = p.prisma.keysetWhere([{ field: "id", direction: "desc" }], [42]);
  assert.deepEqual(fwd, { id: { lt: 42 } });
  const back = p.prisma.keysetWhere([{ field: "id", direction: "desc" }], [42], {
    backwards: true,
  });
  assert.deepEqual(back, { id: { gt: 42 } });
});

// -- drizzle ----------------------------------------------------------------

// Mock Drizzle operators that build a plain JSON tree so we can assert structure.
const OPS = {
  and: (...c) => ({ and: c }),
  or: (...c) => ({ or: c }),
  gt: (col, val) => ({ gt: [col, val] }),
  lt: (col, val) => ({ lt: [col, val] }),
  eq: (col, val) => ({ eq: [col, val] }),
};

test("drizzle: keysetCondition single key", () => {
  const cond = p.drizzle.keysetCondition([{ column: "id" }], [42], OPS);
  assert.deepEqual(cond, { gt: ["id", 42] });
});

test("drizzle: keysetCondition two keys -> or(gt, and(eq, lt))", () => {
  const cond = p.drizzle.keysetCondition(
    [{ column: "createdAt" }, { column: "id", direction: "desc" }],
    ["t", 42],
    OPS,
  );
  assert.deepEqual(cond, {
    or: [{ gt: ["createdAt", "t"] }, { and: [{ eq: ["createdAt", "t"] }, { lt: ["id", 42] }] }],
  });
});
