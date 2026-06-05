/**
 * Express / Connect adapter: parse `req.query` into validated pagination params.
 * Framework-agnostic — it only needs an object of query values, so it also fits
 * Fastify, Koa, and `URLSearchParams` (via `Object.fromEntries`).
 */
import { CursorParams, OffsetParams } from "../params.js";

/** A parsed query string (Express's `req.query` shape). */
export type QueryLike = Record<string, string | string[] | undefined>;

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function intOr(value: string | string[] | undefined, fallback: number): number {
  const raw = first(value);
  if (raw === undefined || raw === "") {
    return fallback;
  }
  const n = Number(raw);
  return Number.isFinite(n) ? n : fallback;
}

/** `{ page, limit }` from the query (validated; throws ValidationError if bad). */
export function offsetParamsFromQuery(query: QueryLike): OffsetParams {
  return new OffsetParams({ page: intOr(query.page, 1), limit: intOr(query.limit, 20) });
}

/** `{ limit, after?, before? }` from the query (after/before mutually exclusive). */
export function cursorParamsFromQuery(query: QueryLike): CursorParams {
  return new CursorParams({
    limit: intOr(query.limit, 20),
    after: first(query.after) ?? null,
    before: first(query.before) ?? null,
  });
}
