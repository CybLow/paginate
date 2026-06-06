/**
 * Declarative filter / sort / search specifications, mirroring pypaginate's
 * `domain/specs.py`. Users construct these; the engines (and adapters) consume
 * them. `And()` / `Or()` build nested boolean groups (validating nesting depth).
 */
import * as core from "@cyblow/paginate-core";

import { FilterValidationError, SearchQueryError } from "./errors.js";

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

/** A search specification (query + fields + scoring options). */
export interface SearchSpec {
  query: string;
  fields: ReadonlyArray<string>;
  mode?: SearchFieldMode;
  fuzzy?: FuzzyMode;
  threshold?: number;
  minLength?: number;
  maxResults?: number;
  /** Per-field relevance multipliers, keyed by field name (default 1.0). */
  weights?: Readonly<Record<string, number>>;
}

/** Nesting depth of a group: `1 + deepest nested group` (a group of only leaves
 * is depth 1), mirroring pypaginate's `_measure_depth`. */
function measureDepth(group: FilterGroup): number {
  let deepest = 0;
  for (const condition of group.conditions) {
    if ("conditions" in condition) deepest = Math.max(deepest, measureDepth(condition));
  }
  return 1 + deepest;
}

/** Validate a freshly built group's nesting depth against the core limit,
 * surfacing the core's message as a FilterValidationError. */
function checkDepth(group: FilterGroup): FilterGroup {
  try {
    core.validateFilterDepth(measureDepth(group));
  } catch (err) {
    throw new FilterValidationError((err as Error).message);
  }
  return group;
}

/** Build an AND group of filter conditions (validates nesting depth). */
export function And(...conditions: ReadonlyArray<FilterSpec | FilterGroup>): FilterGroup {
  return checkDepth({ logic: "and", conditions });
}

/** Build an OR group of filter conditions (validates nesting depth). */
export function Or(...conditions: ReadonlyArray<FilterSpec | FilterGroup>): FilterGroup {
  return checkDepth({ logic: "or", conditions });
}

/**
 * Validate and return a search spec — the query length is checked against the
 * core limit at construction (mirrors pypaginate's `SearchSpec`), surfacing the
 * core's message as a SearchQueryError. Specs may still be written as plain
 * literals; use this when you want fail-fast validation up front.
 */
export function searchSpec(spec: SearchSpec): SearchSpec {
  try {
    core.validateSearchQuery(spec.query);
  } catch (err) {
    throw new SearchQueryError((err as Error).message);
  }
  return spec;
}
