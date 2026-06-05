/**
 * Top-level in-memory pagination. Filter + sort + offset-paginate an array in a
 * single native call by building a resident {@link Dataset} under the hood, so
 * the host stays a thin adapter.
 *
 * Cursor (keyset) pagination is a database concern — use the ORM adapters
 * (Drizzle / Prisma) with {@link encodeCursor} / {@link decodeCursor}, not an
 * in-memory array.
 */
import { Dataset } from "./dataset.js";

import type { OffsetParams } from "./params.js";
import type { OffsetPage } from "./pages.js";
import type { FilterSpec, SortSpec } from "./specs.js";

/** Optional filter + sort applied before paginating. */
export interface PaginateOptions {
  filters?: readonly FilterSpec[];
  sorting?: readonly SortSpec[];
}

/** Offset-paginate an in-memory array into an {@link OffsetPage}. */
export function paginate<T extends object>(
  items: readonly T[],
  params: OffsetParams,
  opts: PaginateOptions = {},
): OffsetPage<T> {
  return new Dataset(items).page(params, opts);
}
