/**
 * Text normalization — delegates to the native core so JS, Python, and Rust
 * agree byte-for-byte (NFKD accent-strip + case-fold + whitespace collapse).
 */
import * as core from "@cyblow/paginate-core";

/** Normalize text exactly as the Python package does (accent-strip + lower). */
export const normalize = (value: string): string => core.normalizeText(value);
