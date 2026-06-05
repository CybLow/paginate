/**
 * Declarative filter / sort / search specifications, mirroring pypaginate's
 * `domain/specs.py`. Users construct these; the engines (and adapters) consume
 * them. `And()` / `Or()` build nested boolean groups.
 */

/** The 20 supported filter operators (type-checked at definition time). */
export type FilterOperator =
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

/** Logical combinator for flat filter lists. */
export type FilterLogic = "and" | "or";

/** A single filter condition. `operator` is canonical; `op` is a legacy alias. */
export interface FilterSpec {
  field: string;
  operator: FilterOperator;
  value?: unknown;
  logic?: FilterLogic;
}

/** A nested boolean group: each condition is a `FilterSpec` or `FilterGroup`. */
export interface FilterGroup {
  logic: FilterLogic;
  conditions: ReadonlyArray<FilterSpec | FilterGroup>;
}

/** A single sort key (null-aware, direction-aware). */
export interface SortSpec {
  field: string;
  direction?: "asc" | "desc";
  nulls?: "first" | "last";
}

/** How a token matches a field value. */
export type SearchFieldMode = "prefix" | "contains" | "exact";

/** Fuzzy matching strategy. */
export type FuzzyMode = "exact" | "fuzzy" | "token_sort";

/**
 * A search specification (query + fields + scoring options).
 *
 * Note: per-field `weights` are supported by the Python package but not yet by
 * the JS binding, so they are intentionally absent here.
 */
export interface SearchSpec {
  query: string;
  fields: ReadonlyArray<string>;
  mode?: SearchFieldMode;
  fuzzy?: FuzzyMode;
  threshold?: number;
  minLength?: number;
  maxResults?: number;
}

/** Build an AND group of filter conditions. */
export function And(...conditions: ReadonlyArray<FilterSpec | FilterGroup>): FilterGroup {
  return { logic: "and", conditions };
}

/** Build an OR group of filter conditions. */
export function Or(...conditions: ReadonlyArray<FilterSpec | FilterGroup>): FilterGroup {
  return { logic: "or", conditions };
}
