/**
 * Pagination input parameters — Elysia-style: the params type determines the
 * page type. The range/exclusivity rules and `MAX_LIMIT` live **once** in the
 * Rust core (shared with pypaginate, so they can't drift); these classes are
 * thin holders that delegate to it and rethrow as `ValidationError`. Only the
 * JS-specific integer guard stays here (JS has no integer type).
 */
import * as core from "@cyblow/paginate-core";

import { clampPage } from "./pagination.js";
import { ValidationError } from "./errors.js";

/** Maximum allowed page limit (DoS mitigation). Single source: the Rust core. */
export const MAX_LIMIT: number = core.MAX_LIMIT;

/** Run a core validator, rethrowing its native error as a `ValidationError`. */
function check(validate: () => void): void {
  try {
    validate();
  } catch (e) {
    throw new ValidationError((e as Error).message);
  }
}

/** Offset pagination input: `{ page, limit }` (defaults: page 1, limit 20). */
export class OffsetParams {
  readonly page: number;
  readonly limit: number;

  constructor({ page = 1, limit = 20 }: { page?: number; limit?: number } = {}) {
    if (!Number.isInteger(page) || !Number.isInteger(limit)) {
      throw new ValidationError("page and limit must be integers");
    }
    check(() => core.validateOffset(page, limit));
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
    if (!Number.isInteger(limit)) {
      throw new ValidationError("limit must be an integer");
    }
    check(() => core.validateCursor(limit, after !== null, before !== null));
    this.limit = limit;
    this.after = after;
    this.before = before;
  }
}
