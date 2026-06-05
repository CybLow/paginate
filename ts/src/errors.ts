/** Error hierarchy mirroring pypaginate's domain exceptions. */

/** Base error for all paginate failures. */
export class PaginateError extends Error {}

/** Invalid pagination input (bad page/limit, malformed cursor, ...). */
export class ValidationError extends PaginateError {
  constructor(message: string) {
    super(message);
    this.name = "ValidationError";
  }
}
