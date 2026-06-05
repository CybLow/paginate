/**
 * Offset pagination math — a thin typed wrapper over the native core, so the
 * arithmetic (offset, page count, clamping, metadata) matches Python exactly.
 */
import * as core from "@cyblow/paginate-core";

/** Page metadata for offset pagination. */
export interface OffsetMeta {
  page: number;
  pages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

/** Zero-based row offset for `(page, limit)`. */
export const offset = (page: number, limit: number): number => core.offset(page, limit);

/** Total page count for `total` rows at `limit` per page (0 when empty). */
export const maxPages = (total: number, limit: number): number => core.maxPages(total, limit);

/** Clamp `page` into the valid `[1, maxPage]` range. */
export const clampPage = (page: number, limit: number, total: number): number =>
  core.clampPage(page, limit, total);

/** Page metadata `(page, pages, hasNext, hasPrevious)` for `(page, limit, total)`. */
export const offsetMeta = (page: number, limit: number, total: number): OffsetMeta =>
  core.offsetMeta(page, limit, total) as OffsetMeta;
