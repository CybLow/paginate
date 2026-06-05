/**
 * Cursor codec — wire-compatible with the Python (`pypaginate`) and Rust cores.
 *
 * A cursor minted by a Python service decodes byte-for-byte here and vice versa,
 * so a polyglot system shares one keyset-pagination scheme. The codec lives in
 * the native core; this is a thin typed wrapper.
 */
import * as core from "@cyblow/paginate-core";

/** A plain ordering value — no host objects cross the boundary. */
export type Scalar = string | number | boolean | null;

/** A keyset ordering tuple extracted from a record, e.g. `[createdAt, id]`. */
export type CursorValues = ReadonlyArray<Scalar>;

/** Encode ordering values into a URL-safe, Python-compatible cursor string. */
export function encodeCursor(values: CursorValues): string {
  return core.encodeCursor(values as unknown[]);
}

/** Decode a cursor string back into its ordering values. */
export function decodeCursor(cursor: string): Scalar[] {
  return core.decodeCursor(cursor) as Scalar[];
}
