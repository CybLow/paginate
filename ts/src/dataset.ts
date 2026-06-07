/**
 * A resident dataset: marshal rows into the Rust core ONCE, then run many
 * filter / sort / search / page queries natively (the core returns indices, this
 * wrapper maps them back to your own objects). This is the only in-memory shape
 * where crossing into Rust pays off for JS — the one-shot `*Indices` helpers
 * re-marshal the whole array on every call. Build once, query many times.
 *
 * Core engine failures are re-typed into the typed `FilterError` / `SortError` /
 * `SearchError`, matching pypaginate's exception taxonomy.
 */
import * as core from "@cyblow/paginate-core";

import { FilterError, PaginateError, SearchError, SortError, rethrowEngineError } from "./errors.js";
import type { OffsetParams } from "./params.js";
import type { OffsetPage } from "./pages.js";
import type { FilterSpec, SearchSpec, SortSpec } from "./specs.js";

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
    try {
      return this.select(this.inner.filter(specs as unknown as core.FilterSpecInput[]));
    } catch (e) {
      rethrowEngineError(e, FilterError);
    }
  }

  /** Rows sorted by the specs (null-aware, stable). */
  sort(specs: readonly SortSpec[]): T[] {
    try {
      return this.select(this.inner.sort(specs as unknown as core.SortSpecInput[]));
    } catch (e) {
      rethrowEngineError(e, SortError);
    }
  }

  /** Rows ranked by relevance of the search spec's query over its fields. */
  search(spec: SearchSpec): T[] {
    try {
      return this.select(
        this.inner.search(
          spec.query,
          spec.fields as string[],
          spec.mode,
          spec.fuzzy,
          spec.threshold,
          spec.minLength,
          spec.maxResults,
          spec.weights as Record<string, number> | undefined,
        ),
      );
    } catch (e) {
      rethrowEngineError(e, SearchError);
    }
  }

  /**
   * Filter + search + sort + offset-paginate in ONE native call. `search` is a
   * match-filter (keep rows matching the query); an explicit `sorting` still
   * decides the order, and the resident trigram index prunes fuzzy candidates.
   */
  page(
    params: OffsetParams,
    opts: {
      filters?: readonly FilterSpec[];
      sorting?: readonly SortSpec[];
      search?: SearchSpec;
    } = {},
  ): OffsetPage<T> {
    try {
      const result = this.inner.page(
        params.page,
        params.limit,
        opts.filters as unknown as core.FilterSpecInput[] | undefined,
        opts.sorting as unknown as core.SortSpecInput[] | undefined,
        opts.search ? searchStageArg(opts.search) : undefined,
      );
      return {
        items: this.select(result.indices),
        total: Number(result.total),
        page: Number(result.page),
        pages: Number(result.pages),
        limit: params.limit,
        hasNext: result.hasNext,
        hasPrevious: result.hasPrevious,
      };
    } catch (e) {
      // Multi-op: the core's message prefix selects filter/sort/search; anything
      // else (incl. field-not-found, which carries no op) → the base error.
      rethrowEngineError(e, PaginateError);
    }
  }

  private select(indices: number[]): T[] {
    return indices.map((i) => this.rows[i] as T);
  }
}

/** The `{ query, fields, mode, fuzzy, threshold }` object the core page search
 * stage parses (a match-filter; `minLength` / `maxResults` do not apply). */
function searchStageArg(spec: SearchSpec): Record<string, unknown> {
  return {
    query: spec.query,
    fields: spec.fields,
    mode: spec.mode,
    fuzzy: spec.fuzzy,
    threshold: spec.threshold,
  };
}
