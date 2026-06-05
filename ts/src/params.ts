/**
 * Pagination input parameters — Elysia-style: the params type determines the
 * page type. Mirrors pypaginate's `domain/params.py` (illegal states are
 * unrepresentable; validation rules match, including `MAX_LIMIT`).
 */
import { clampPage } from "./pagination.js";
import { ValidationError } from "./errors.js";

/** Maximum allowed page limit (DoS mitigation). Mirrors pypaginate.MAX_LIMIT. */
export const MAX_LIMIT = 1000;

function validateLimit(limit: number): void {
  if (!Number.isInteger(limit) || limit < 1) {
    throw new ValidationError("limit must be >= 1");
  }
  if (limit > MAX_LIMIT) {
    throw new ValidationError(`limit must not exceed ${MAX_LIMIT}`);
  }
}

/** Offset pagination input: `{ page, limit }` (defaults: page 1, limit 20). */
export class OffsetParams {
  readonly page: number;
  readonly limit: number;

  constructor({ page = 1, limit = 20 }: { page?: number; limit?: number } = {}) {
    if (!Number.isInteger(page) || page < 1) {
      throw new ValidationError("page must be >= 1");
    }
    validateLimit(limit);
    this.page = page;
    this.limit = limit;
  }

  /** Zero-based offset for database queries. */
  get offset(): number {
    return (this.page - 1) * this.limit;
  }

  /** Return params with `page` clamped into `[1, maxPage]` for `total` rows. */
  clamp(total: number): OffsetParams {
    const safe = clampPage(this.page, this.limit, Math.max(total, 0));
    return safe === this.page ? this : new OffsetParams({ page: safe, limit: this.limit });
  }
}

/** Cursor pagination input: `{ limit, after?, before? }` (mutually exclusive). */
export class CursorParams {
  readonly limit: number;
  readonly after: string | null;
  readonly before: string | null;

  constructor({
    limit = 20,
    after = null,
    before = null,
  }: { limit?: number; after?: string | null; before?: string | null } = {}) {
    validateLimit(limit);
    if (after !== null && before !== null) {
      throw new ValidationError("after and before are mutually exclusive");
    }
    this.limit = limit;
    this.after = after;
    this.before = before;
  }
}
