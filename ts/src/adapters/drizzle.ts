/**
 * Drizzle adapter: build the keyset (cursor) `where` condition from the core's
 * portable predicate. Drizzle's operators (`and`, `or`, `gt`, `lt`, `eq`) and
 * column references are *injected*, so this carries no `drizzle-orm` dependency
 * and works with any Drizzle version:
 *
 *     import { and, or, gt, lt, eq } from "drizzle-orm";
 *     const where = keysetCondition(
 *       [{ column: posts.createdAt }, { column: posts.id }],
 *       [lastRow.createdAt, lastRow.id],
 *       { and, or, gt, lt, eq },
 *     );
 *     db.select().from(posts).where(where).orderBy(posts.createdAt, posts.id).limit(20);
 */
import { effectiveAscending, keysetTerms } from "../keyset.js";

import type { Scalar } from "../cursor.js";
import type { SortDir } from "../keyset.js";

/** The Drizzle boolean/comparison operators this adapter renders with. */
export interface DrizzleOps {
  and: (...conditions: unknown[]) => unknown;
  or: (...conditions: unknown[]) => unknown;
  gt: (column: unknown, value: unknown) => unknown;
  lt: (column: unknown, value: unknown) => unknown;
  eq: (column: unknown, value: unknown) => unknown;
}

/** One ordering key: the Drizzle column and its direction (default ascending). */
export interface KeysetColumn {
  column: unknown;
  direction?: SortDir;
}

/**
 * A Drizzle `where` condition selecting rows strictly after `cursorValues` along
 * `keys`. Pass `backwards: true` for a `before` cursor (flips each direction).
 */
export function keysetCondition(
  keys: readonly KeysetColumn[],
  cursorValues: readonly Scalar[],
  ops: DrizzleOps,
  opts: { backwards?: boolean } = {},
): unknown {
  const ascending = effectiveAscending(
    keys.map((k) => k.direction),
    opts.backwards,
  );
  const orClauses = keysetTerms(ascending).map((term) => {
    const ands = term.map(([i, op]) => ops[op](keys[i].column, cursorValues[i]));
    return ands.length === 1 ? ands[0] : ops.and(...ands);
  });
  return orClauses.length === 1 ? orClauses[0] : ops.or(...orClauses);
}
