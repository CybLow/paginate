/**
 * `@cyblow/paginate` — idiomatic TypeScript over the native `paginate-core`
 * engine. The Rust core owns all computation and speaks only plain data; this
 * package maps an app's models/ORM rows to the plain DTOs the engine
 * understands. The headline guarantee is **cross-language parity**: a cursor
 * minted by a Python (`pypaginate`) service decodes byte-for-byte here, and the
 * filter / sort / search semantics are identical.
 *
 *     import { paginate, OffsetParams } from "@cyblow/paginate";
 *     const page = paginate(users, new OffsetParams({ page: 1, limit: 20 }));
 *     page.total; // number
 */

// -- cursor codec -----------------------------------------------------------
export { encodeCursor, decodeCursor } from "./cursor.js";
export type { Scalar, CursorValues } from "./cursor.js";

// -- offset math + text -----------------------------------------------------
export { offset, maxPages, clampPage, offsetMeta } from "./pagination.js";
export type { OffsetMeta } from "./pagination.js";
export { normalize } from "./normalize.js";

// -- keyset (cursor) predicate ----------------------------------------------
export { keysetTerms } from "./keyset.js";
export type { KeysetOp, KeysetTerm } from "./keyset.js";

// -- specs (filter / sort / search) -----------------------------------------
export { And, Or } from "./specs.js";
export type {
  FilterOperator,
  FilterLogic,
  FilterSpec,
  FilterGroup,
  SortSpec,
  SearchFieldMode,
  FuzzyMode,
  SearchSpec,
} from "./specs.js";

// -- one-shot engines -------------------------------------------------------
export { filterIndices, filterGroupIndices, sortIndices, searchIndices } from "./engines.js";

// -- params + pages ---------------------------------------------------------
export { OffsetParams, CursorParams, MAX_LIMIT } from "./params.js";
export { offsetPage, cursorPage } from "./pages.js";
export type { OffsetPage, CursorPage } from "./pages.js";

// -- errors -----------------------------------------------------------------
export { PaginateError, ValidationError } from "./errors.js";

// -- resident dataset + top-level paginate ----------------------------------
export { Dataset } from "./dataset.js";
export { paginate } from "./paginate.js";
export type { PaginateOptions } from "./paginate.js";

// -- framework / ORM adapters (thin spec + predicate builders) ---------------
export * as express from "./adapters/express.js";
export * as prisma from "./adapters/prisma.js";
export * as drizzle from "./adapters/drizzle.js";
