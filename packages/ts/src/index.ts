/**
 * paginate — TypeScript consumer of paginate-core. **SCAFFOLD.**
 *
 * This file demonstrates the ports-and-adapters pattern that every language
 * package follows. The Rust engine (`crates/core`) owns all computation and
 * speaks only plain data; this package is the *adapter* that maps a concrete
 * ORM to the DTO *port* the engine understands.
 *
 *     ORM model ─▶ plain DTO ─▶ native core call ─▶ result ─▶ apply to DB
 *      (here)       (here)       (paginate-core)              (here)
 *
 * STRICT RULE: the ORM lives in THIS package, never in the Rust core. The core
 * never imports Prisma/Drizzle/TypeORM or touches a database — it only ever
 * sees DTOs and returns plain data (cursor strings, page metadata, or indices).
 */

// The native addon, built by the napi-rs adapter crate `crates/node`.
// (Adapter crate is planned; this import is the scaffold's stand-in for the
// real, native module — the same compute surface exposed to Python as
// `paginate_core`.)
import * as core from "paginate-core";

// --------------------------------------------------------------------------
// DTO: the ONLY shape the core sees. Plain, ORM-agnostic ordering values —
// no Prisma client, no entity instance, no query builder crosses this line.
// --------------------------------------------------------------------------

/** A keyset ordering tuple extracted from a record (e.g. `[createdAt, id]`). */
export type CursorDto = ReadonlyArray<string | number | boolean | null>;

/** A Prisma-like model row. Stands in for whatever ORM the app actually uses. */
interface ArticleModel {
  id: number;
  createdAt: Date;
  title: string;
}

// --------------------------------------------------------------------------
// Adapter: ORM model -> DTO -> core. Mapping the ORM is the ADAPTER's job;
// the core only sees the DTO it is handed back.
// --------------------------------------------------------------------------

/**
 * Encode a keyset cursor for the page that follows `lastRow`.
 *
 * Step 1 (adapter): map the ORM model to a plain DTO — extract only the
 * ordering keys, converting host types (`Date`) to plain values.
 * Step 2 (core): hand the DTO to the native engine, which returns a wire-
 * compatible cursor string. (Step 3 — applying a keyset `WHERE`/`ORDER BY`/
 * `LIMIT` with the ORM — happens in the caller, never in the core.)
 */
export function encodeNextCursor(lastRow: ArticleModel): string {
  // Step 1: ORM model -> plain DTO (ORM mapping is the adapter's job).
  const dto: CursorDto = [lastRow.createdAt.toISOString(), lastRow.id];

  // Step 2: DTO -> core. The engine never saw the ArticleModel — only the DTO.
  return core.encodeCursor(dto);
}

// TODO(scaffold): add `decodeCursor` + offset helpers (`offset`, `maxPages`,
// `offsetMeta`, `clampPage`) and the Drizzle/TypeORM adapters, mirroring the
// `paginate_core` PyO3 surface. The in-memory engines (filter/sort/search)
// will return INDICES so the adapter selects from its own ORM rows by index —
// host rows never round-trip through Rust.
