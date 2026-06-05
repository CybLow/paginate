/**
 * Keyset (cursor) predicate structure — the lexicographic OR-of-AND comparison
 * for `ORDER BY (k0, k1, ...)`. The native core owns the structure; the ORM
 * adapters (Drizzle / Prisma) render each `key[i] OP value[i]` and combine with
 * their own AND/OR.
 */
import * as core from "@cyblow/paginate-core";

/** A keyset comparison operator. */
export type KeysetOp = "gt" | "lt" | "eq";

/** One AND-term: `[keyIndex, op]` pairs to render and AND together. */
export type KeysetTerm = ReadonlyArray<readonly [number, KeysetOp]>;

/**
 * Lexicographic keyset predicate as OR-of-AND terms for the effective key
 * directions. `ascending[i]` is the direction of key `i` *after* any
 * backward-pagination flip; the strict comparison is `gt` when ascending, else
 * `lt`. Render `key[i] OP value[i]`, AND each term, then OR the terms.
 */
export function keysetTerms(ascending: readonly boolean[]): KeysetTerm[] {
  return core.keysetTerms(ascending as boolean[]) as KeysetTerm[];
}

/** A keyed sort direction (`undefined` defaults to ascending). */
export type SortDir = "asc" | "desc" | undefined;

/**
 * Effective key directions for a keyset predicate: ascending unless `"desc"`,
 * XOR-flipped when paginating `backwards` (a `before` cursor).
 */
export function effectiveAscending(directions: readonly SortDir[], backwards = false): boolean[] {
  return directions.map((d) => (d !== "desc") !== backwards);
}
