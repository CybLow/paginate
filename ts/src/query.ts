/**
 * One-shot item-returning query helpers — the ergonomic complement to the
 * index-returning {@link filterIndices}/{@link sortIndices}/{@link searchIndices}
 * and the mirror of pypaginate's top-level `filter` / `sort` / `search`. Each
 * returns a new array of the matching items (search in ranked order).
 *
 *     import { search, filter, sort } from "@cyblow/paginate";
 *     const adults = filter(users, { field: "age", operator: "gte", value: 18 });
 *     const hits = search(users, { query: "alice", fields: ["name", "email"] });
 */
import { filterGroupIndices, filterIndices, searchIndices, sortIndices } from "./engines.js";

import type { FilterGroup, FilterSpec, SearchSpec, SortSpec } from "./specs.js";

/** A single spec, a flat list (combined per each `logic`), or a nested group. */
export type FilterWhere = FilterSpec | readonly FilterSpec[] | FilterGroup;
/** A single sort key or a sequence applied in priority order. */
export type SortBy = SortSpec | readonly SortSpec[];

function isGroup(where: FilterWhere): where is FilterGroup {
  return !Array.isArray(where) && "conditions" in where;
}

/** Return the items matching `where`, in original order. */
export function filter<T extends object>(items: readonly T[], where: FilterWhere): T[] {
  let indices: number[];
  if (isGroup(where)) {
    indices = filterGroupIndices(items, where);
  } else {
    const specs = Array.isArray(where) ? where : [where];
    indices = filterIndices(items, specs as readonly FilterSpec[]);
  }
  return indices.map((i) => items[i]);
}

/** Return the items ordered by `by` (null-aware, stable). */
export function sort<T extends object>(items: readonly T[], by: SortBy): T[] {
  const specs = (Array.isArray(by) ? by : [by]) as readonly SortSpec[];
  return sortIndices(items, specs).map((i) => items[i]);
}

/** Return the items matching `spec` in ranked (relevance) order. */
export function search<T extends object>(items: readonly T[], spec: SearchSpec): T[] {
  return searchIndices(items, spec).map((i) => items[i]);
}
