/**
 * Pagination result pages. Each page carries only the fields for its mode (no
 * null leakage), mirroring pypaginate's `OffsetPage` / `CursorPage`. Page
 * metadata comes from the native engine via {@link offsetMeta}.
 */
import { offsetMeta } from "./pagination.js";

import type { CursorParams, OffsetParams } from "./params.js";

/** Offset pagination result. */
export interface OffsetPage<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  limit: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

/** Cursor pagination result (no `total`/`page` — those are offset-only). */
export interface CursorPage<T> {
  items: T[];
  limit: number;
  hasNext: boolean;
  hasPrevious: boolean;
  nextCursor: string | null;
  previousCursor: string | null;
}

/** Build an {@link OffsetPage} from page items, the match total, and the params. */
export function offsetPage<T>(items: T[], total: number, params: OffsetParams): OffsetPage<T> {
  const meta = offsetMeta(params.page, params.limit, total);
  return {
    items,
    total,
    page: meta.page,
    pages: meta.pages,
    limit: params.limit,
    hasNext: meta.hasNext,
    hasPrevious: meta.hasPrevious,
  };
}

/** Build a {@link CursorPage} from page items, the params, and the edge cursors. */
export function cursorPage<T>(
  items: T[],
  params: CursorParams,
  cursors: { nextCursor?: string | null; previousCursor?: string | null } = {},
): CursorPage<T> {
  const nextCursor = cursors.nextCursor ?? null;
  const previousCursor = cursors.previousCursor ?? null;
  return {
    items,
    limit: params.limit,
    hasNext: nextCursor !== null,
    hasPrevious: previousCursor !== null,
    nextCursor,
    previousCursor,
  };
}
