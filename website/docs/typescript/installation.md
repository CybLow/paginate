---
sidebar_position: 1
title: Installation
---

# Installation

```bash
npm i @cyblow/paginate
# or
bun add @cyblow/paginate
# or
pnpm add @cyblow/paginate
```

**Node 18+.** The package is an idiomatic TypeScript adapter over the native addon
[`@cyblow/paginate-core`](https://www.npmjs.com/package/@cyblow/paginate-core), which
installs automatically as a **platform-specific dependency** — prebuilt binaries
(via napi-rs) for Linux (glibc + musl), macOS, and Windows on x86-64 and arm64. No
build step and no Rust toolchain.

Ships with TypeScript types; it works from plain JavaScript too.

## Verify

```ts
import { paginate, OffsetParams } from "@cyblow/paginate";

const page = paginate([1, 2, 3, 4, 5], new OffsetParams({ page: 1, limit: 2 }));
console.log(page.items, page.total); // [1, 2] 5
```

## Next

- [Quickstart](./quickstart) — paginate, filter, sort, and search in a few lines.
