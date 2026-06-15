# Changelog

## [1.0.0](https://github.com/CybLow/paginate/compare/ts-v0.1.5...ts-v1.0.0) (2026-06-15)


### ⚠ BREAKING CHANGES

* **core:** complete v0.3 fat-core — reorg, domain SSOT, DX, perf
* **ts:** migrate the JS toolchain from npm/node to Bun
* **ts:** FilterSpec uses `operator` (not `op`); searchIndices takes a SearchSpec object; Dataset.page/Dataset.search take params/spec objects.

### Features

* **core:** portable keyset predicate (keyset_terms) for every adapter ([bed836a](https://github.com/CybLow/paginate/commit/bed836ac6f8989491fdedc0377734a4acec3dd27))
* **ts,node:** error hierarchy, search weights, construction-time spec validation ([bbe6d78](https://github.com/CybLow/paginate/commit/bbe6d788f1b89987d7e1534b25987912fd288dc7))
* **ts:** add Express, Prisma, and Drizzle adapters ([95781f8](https://github.com/CybLow/paginate/commit/95781f84141da12be2f36f3e9ed163f1039e032b))
* **ts:** modular package with params, pages, paginate() + builders ([d9a2df6](https://github.com/CybLow/paginate/commit/d9a2df6ede6090b482eeace58f5f335e6eb026ff))
* **ts:** re-type core engine errors to FilterError/SortError/SearchError ([1dbd94d](https://github.com/CybLow/paginate/commit/1dbd94d8f7282a54b27ae15d17cfb4d6196abe1f))


### Bug Fixes

* surface malformed keyset cursors as a public InvalidCursorError ([3c094f2](https://github.com/CybLow/paginate/commit/3c094f2b8abbac045af3ba3348d76746abc504f4))


### Performance

* **core:** fold search into the one-pass offset pipeline ([96b47b0](https://github.com/CybLow/paginate/commit/96b47b074519476d9a48bfb3e1489ad8b80c379f))
* profiling-led resident-engine optimization, hardening, and cleanup ([126e459](https://github.com/CybLow/paginate/commit/126e45965a9c0734b9a539babd81e4586408a64d))


### Refactoring

* **core:** complete v0.3 fat-core — reorg, domain SSOT, DX, perf ([930d075](https://github.com/CybLow/paginate/commit/930d0755bc59e442d4a94d7a5badc2ec8a354f28))


### Documentation

* **ts:** fix stale publishing note and broken README links ([4af8fe2](https://github.com/CybLow/paginate/commit/4af8fe2812a28fae5455822dc9e53e3ba12c480e))
* v0.3 migration guide, changelog, and JS adapter README ([926b143](https://github.com/CybLow/paginate/commit/926b1433c2a61204a68a55a9475f5bf8ae29b644))


### Build

* **ts:** migrate the JS toolchain from npm/node to Bun ([01488bd](https://github.com/CybLow/paginate/commit/01488bdd4a64ede03b56d762b0efd19479926448))
