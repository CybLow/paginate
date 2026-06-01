/**
 * paginate — idiomatic TypeScript over the native `paginate-core` engine.
 *
 * The Rust core (`crates/core`) owns all computation and speaks only plain data;
 * this package is the *adapter* that maps an app's ORM models to the DTO *port*
 * the engine understands. The ORM lives HERE, never in the core:
 *
 *     ORM model ─▶ plain DTO ─▶ native core call ─▶ result ─▶ apply to DB
 *
 * ## What to use the core for
 *
 * The **cursor codec** is the headline: a cursor minted by a Python service
 * decodes byte-for-byte here and vice versa, so a polyglot system shares one
 * keyset-pagination scheme with zero drift. `normalize` and the pagination math
 * are here for the same behaviour-consistency reason.
 *
 * The **filter / sort / search** helpers expose pypaginate's *exact* semantics
 * (20 operators, null-aware sort, ranked search) for parity — but for raw
 * in-memory speed prefer native `Array` methods: marshalling a large array
 * across the FFI costs far more than the work (see `BENCHMARKS.md`). Use these
 * when you need the precise behaviour, not as a speed-up.
 */

import * as core from "paginate-core";

// -- value model ------------------------------------------------------------

/** A plain ordering value — no host objects cross the boundary. */
export type Scalar = string | number | boolean | null;

/** A keyset ordering tuple extracted from a record, e.g. `[createdAt, id]`. */
export type CursorValues = ReadonlyArray<Scalar>;

/** Page metadata for offset pagination. */
export interface OffsetMeta {
  page: number;
  pages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// -- cursor codec (wire-compatible with the Python service) -----------------

/** Encode ordering values into a URL-safe, Python-compatible cursor string. */
export function encodeCursor(values: CursorValues): string {
  return core.encodeCursor(values as unknown[]);
}

/** Decode a cursor string back into its ordering values. */
export function decodeCursor(cursor: string): Scalar[] {
  return core.decodeCursor(cursor) as Scalar[];
}

// -- offset pagination math -------------------------------------------------

export const offset = (page: number, limit: number): number => core.offset(page, limit);

export const maxPages = (total: number, limit: number): number => core.maxPages(total, limit);

export const clampPage = (page: number, limit: number, total: number): number =>
  core.clampPage(page, limit, total);

export const offsetMeta = (page: number, limit: number, total: number): OffsetMeta =>
  core.offsetMeta(page, limit, total) as OffsetMeta;

// -- text -------------------------------------------------------------------

/** Normalize text exactly as the Python package does (NFKD accent-strip + lower). */
export const normalize = (value: string): string => core.normalizeText(value);

// -- in-memory engines (behaviour parity; prefer native Array ops for speed) --

export type FilterOp =
  | "eq"
  | "ne"
  | "gt"
  | "gte"
  | "lt"
  | "lte"
  | "in"
  | "not_in"
  | "contains"
  | "starts_with"
  | "ends_with"
  | "like"
  | "ilike"
  | "between"
  | "is_null"
  | "is_not_null"
  | "regex"
  | "empty"
  | "not_empty"
  | "exists";

export interface FilterSpec {
  field: string;
  op: FilterOp;
  value?: unknown;
  logic?: "and" | "or";
}

export interface SortSpec {
  field: string;
  direction?: "asc" | "desc";
  nulls?: "first" | "last";
}

export interface SearchOptions {
  mode?: "prefix" | "contains" | "exact";
  threshold?: number;
  minLength?: number;
  maxResults?: number;
}

/** Indices of `items` matching `specs` — pypaginate's exact filter semantics. */
export function filterIndices(items: readonly object[], specs: readonly FilterSpec[]): number[] {
  return core.filterIndices(items as unknown[], specs as unknown[]);
}

/** Index permutation sorting `items` by `specs` (null-aware, stable). */
export function sortIndices(items: readonly object[], specs: readonly SortSpec[]): number[] {
  return core.sortIndices(items as unknown[], specs as unknown[]);
}

/** Ranked-search indices over `fields`. */
export function searchIndices(
  items: readonly object[],
  query: string,
  fields: readonly string[],
  opts: SearchOptions = {},
): number[] {
  return core.searchIndices(
    items as unknown[],
    query,
    fields as string[],
    opts.mode,
    undefined,
    opts.threshold,
    opts.minLength,
    opts.maxResults,
  );
}

// -- resident Dataset (marshal once, query many) ----------------------------

/** One page of results: the host's own rows for the page, plus offset metadata. */
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

/**
 * A resident dataset: marshal the rows into the Rust core ONCE, then run many
 * `filter`/`sort`/`search`/`page` queries natively. The core returns indices and
 * this wrapper maps them back to your own objects, so the host stays a thin
 * adapter and a `page` request is a single FFI crossing.
 *
 * This is the only in-memory shape where crossing into Rust can pay off for JS:
 * the one-shot `filterIndices`/`sortIndices`/`searchIndices` helpers re-marshal
 * the whole array on every call and lose to V8 (see `BENCHMARKS.md`). Build the
 * dataset once and query it many times.
 */
export class Dataset<T extends object> {
  private readonly inner: core.Dataset;
  private readonly rows: readonly T[];

  constructor(rows: readonly T[]) {
    this.rows = rows;
    this.inner = new core.Dataset(rows as unknown[]);
  }

  /** Number of rows held. */
  get size(): number {
    return this.inner.size;
  }

  /** Rows matching the filter specs (pypaginate's exact semantics). */
  filter(specs: readonly FilterSpec[]): T[] {
    return this.select(this.inner.filter(specs as unknown[]));
  }

  /** Rows sorted by the specs (null-aware, stable). */
  sort(specs: readonly SortSpec[]): T[] {
    return this.select(this.inner.sort(specs as unknown[]));
  }

  /** Rows ranked by relevance of `query` over `fields`. */
  search(query: string, fields: readonly string[], opts: SearchOptions = {}): T[] {
    return this.select(
      this.inner.search(
        query,
        fields as string[],
        opts.mode,
        undefined,
        opts.threshold,
        opts.minLength,
        opts.maxResults,
      ),
    );
  }

  /** Filter + sort + offset-paginate in ONE native call. */
  page(
    page: number,
    limit: number,
    opts: { filters?: readonly FilterSpec[]; sorting?: readonly SortSpec[] } = {},
  ): Page<T> {
    const result = this.inner.page(
      page,
      limit,
      opts.filters as unknown[] | undefined,
      opts.sorting as unknown[] | undefined,
    );
    return {
      items: this.select(result.indices),
      total: Number(result.total),
      page: Number(result.page),
      pages: Number(result.pages),
      hasNext: result.hasNext,
      hasPrevious: result.hasPrevious,
    };
  }

  private select(indices: number[]): T[] {
    return indices.map((i) => this.rows[i] as T);
  }
}

// -- example: the ORM -> DTO -> core pattern (ORM lives here, not in core) ----

/** A Prisma-like model row — stands in for whatever ORM entity the app uses. */
interface ArticleModel {
  id: number;
  createdAt: Date;
  title: string;
}

/**
 * Encode the keyset cursor for the page after `lastRow`. The adapter extracts
 * only the ordering keys into a plain DTO (`Date` → ISO string); the core never
 * sees the `ArticleModel`. Applying the keyset `WHERE`/`ORDER BY`/`LIMIT` with
 * the ORM happens in the caller, never in the core.
 */
export function encodeNextCursor(lastRow: ArticleModel): string {
  const dto: CursorValues = [lastRow.createdAt.toISOString(), lastRow.id];
  return encodeCursor(dto);
}
