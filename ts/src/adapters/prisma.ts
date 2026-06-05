/**
 * Prisma adapter: build the `where` fragment and `skip`/`take` args for offset
 * and keyset (cursor) pagination. Pure data — no `@prisma/client` dependency.
 *
 * Keyset multi-column cursors are expressed as a nested boolean `where` object
 * rendered from the core's portable keyset predicate, e.g. for
 * `orderBy: [{ createdAt: "asc" }, { id: "asc" }]` after `[t, 42]`:
 *
 *     { OR: [ { createdAt: { gt: t } },
 *             { AND: [ { createdAt: t }, { id: { gt: 42 } } ] } ] }
 */
import { effectiveAscending, keysetTerms } from "../keyset.js";

import type { Scalar } from "../cursor.js";
import type { OffsetParams } from "../params.js";
import type { SortDir } from "../keyset.js";

/** A Prisma `where` fragment. */
export type PrismaWhere = Record<string, unknown>;

/** One ordering key: the model field and its direction (default ascending). */
export interface KeysetKey {
  field: string;
  direction?: SortDir;
}

/** `{ skip, take }` for `prisma.model.findMany` offset pagination. */
export function offsetArgs(params: OffsetParams): { skip: number; take: number } {
  return { skip: params.offset, take: params.limit };
}

function compare(field: string, op: "gt" | "lt" | "eq", value: Scalar): PrismaWhere {
  return op === "eq" ? { [field]: value } : { [field]: { [op]: value } };
}

/**
 * A Prisma `where` fragment selecting rows strictly after `cursorValues` along
 * `keys`. Pass `backwards: true` for a `before` cursor (flips each direction).
 * Combine with your own filters via `{ AND: [yourWhere, keysetWhere(...)] }`.
 */
export function keysetWhere(
  keys: readonly KeysetKey[],
  cursorValues: readonly Scalar[],
  opts: { backwards?: boolean } = {},
): PrismaWhere {
  const ascending = effectiveAscending(
    keys.map((k) => k.direction),
    opts.backwards,
  );
  const orClauses = keysetTerms(ascending).map((term) => {
    const ands = term.map(([i, op]) => compare(keys[i].field, op, cursorValues[i]));
    return ands.length === 1 ? ands[0] : { AND: ands };
  });
  return orClauses.length === 1 ? orClauses[0] : { OR: orClauses };
}
