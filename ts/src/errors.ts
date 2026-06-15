/**
 * Error hierarchy mirroring pypaginate's `domain/exceptions.py`.
 *
 * Every error carries a structured `details` payload (always an object) for
 * programmatic handling, matching the Python side. `instanceof` works across
 * transpile targets (the base restores the prototype chain).
 */

/** Options accepted by the base error (and, with `field`, by some subclasses). */
export interface PaginateErrorOptions {
  details?: Record<string, unknown>;
}

/** Base error for all paginate failures (aliased as `PaginationError`). */
export class PaginateError extends Error {
  /** Structured, programmatic detail payload (mirrors pypaginate's `details`). */
  readonly details: Readonly<Record<string, unknown>>;

  constructor(message: string, options: PaginateErrorOptions = {}) {
    super(message);
    this.name = new.target.name;
    this.details = options.details ?? {};
    // Restore the prototype chain so `instanceof` holds when down-levelled.
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

/** Cross-language alias: pypaginate's base is named `PaginationError`. */
export const PaginationError = PaginateError;

/** Raised when pagination configuration is invalid. */
export class ConfigurationError extends PaginateError {}

/** Raised when filtering operations fail (optionally naming the `field`). */
export class FilterError extends PaginateError {
  readonly field?: string;

  constructor(message: string, options: PaginateErrorOptions & { field?: string } = {}) {
    super(message, options);
    this.field = options.field;
  }
}

/** Raised when filter specification validation fails. */
export class FilterValidationError extends FilterError {}

/** Raised when search operations fail. */
export class SearchError extends PaginateError {}

/** Raised when search query processing fails. */
export class SearchQueryError extends SearchError {}

/** Raised when sort operations fail. */
export class SortError extends PaginateError {}

/** Raised when generic validation fails (bad page/limit, mutually exclusive cursors, ...). */
export class ValidationError extends PaginateError {
  readonly field?: string;

  constructor(message: string, options: PaginateErrorOptions & { field?: string } = {}) {
    super(message, options);
    this.field = options.field;
  }
}

/** Raised when a keyset cursor is malformed, truncated, or tampered with. */
export class InvalidCursorError extends ValidationError {}

/**
 * Re-throw a caught core engine error as the matching typed error, mirroring
 * pypaginate's exception taxonomy so JS consumers get `FilterError` /
 * `SortError` / `SearchError` (not a bare `Error`). The core tags each category
 * in its message; `fallback` covers field-not-found (no category) and anything
 * unrecognized — pass the operation's own error class so context stays correct.
 */
export function rethrowEngineError(
  err: unknown,
  fallback: new (message: string) => PaginateError,
): never {
  const message = err instanceof Error ? err.message : String(err);
  if (message.startsWith("filter error")) throw new FilterError(message);
  if (message.startsWith("sort error")) throw new SortError(message);
  if (message.startsWith("search error")) throw new SearchError(message);
  if (message.startsWith("invalid cursor")) throw new InvalidCursorError(message);
  throw new fallback(message);
}
