/**
 * One-shot in-memory engines — pypaginate's exact filter / sort / search
 * semantics over a JS array, returning indices into the original array.
 *
 * PERF: for raw in-memory speed prefer native `Array` methods — marshalling a
 * large array across the FFI costs more than the work. Use these when you need
 * the precise cross-language semantics, or use a resident {@link Dataset} to
 * marshal once and query many times.
 *
 * Each call re-types core engine failures (a bare napi `Error`) into the typed
 * `FilterError` / `SortError` / `SearchError`, matching pypaginate's taxonomy.
 */
import * as core from "@cyblow/paginate-core";

import { FilterError, SearchError, SortError, rethrowEngineError } from "./errors.js";
import type { FilterGroup, FilterSpec, SearchSpec, SortSpec } from "./specs.js";

/** Indices of `items` matching flat filter `specs` (combined per each `logic`). */
export function filterIndices(items: readonly object[], specs: readonly FilterSpec[]): number[] {
  try {
    return core.filterIndices(items as unknown[], specs as unknown[]);
  } catch (e) {
    rethrowEngineError(e, FilterError);
  }
}

/** Indices of `items` matching a nested `And`/`Or` `FilterGroup`. */
export function filterGroupIndices(items: readonly object[], group: FilterGroup): number[] {
  try {
    return core.filterGroupIndices(items as unknown[], group as unknown);
  } catch (e) {
    rethrowEngineError(e, FilterError);
  }
}

/** Index permutation sorting `items` by `specs` (null-aware, stable). */
export function sortIndices(items: readonly object[], specs: readonly SortSpec[]): number[] {
  try {
    return core.sortIndices(items as unknown[], specs as unknown[]);
  } catch (e) {
    rethrowEngineError(e, SortError);
  }
}

/** Ranked-search indices over the spec's `fields` (relevance order). */
export function searchIndices(items: readonly object[], spec: SearchSpec): number[] {
  try {
    return core.searchIndices(
      items as unknown[],
      spec.query,
      spec.fields as string[],
      spec.mode,
      spec.fuzzy,
      spec.threshold,
      spec.minLength,
      spec.maxResults,
      spec.weights as Record<string, number> | undefined,
    );
  } catch (e) {
    rethrowEngineError(e, SearchError);
  }
}
