# Changelog

## [1.0.0](https://github.com/CybLow/paginate/compare/py-v0.2.1...py-v1.0.0) (2026-06-15)


### ⚠ BREAKING CHANGES

* **py:** swap to the new flat package — in-memory engine on generated types
* **core:** complete v0.3 fat-core — reorg, domain SSOT, DX, perf
* **py:** pypaginate.{filtering,sorting,search,text} (and their FilterEngine / SortEngine / SearchEngine / normalize symbols) and the `pypaginate` CLI are removed — already documented in MIGRATION.md / CHANGELOG.md. The public pagination API (paginate, Dataset, *Params, *Page, *Spec, adapters) is unaffected.
* **core:** fuzzy/token-sort scores and ranking differ from the old rapidfuzz output, and the default search threshold is now 30 (was 75). Trigram is strong on names/titles/multi-word text but weaker on very short single-word typos. The FuzzyMode API and field/threshold knobs are unchanged.
* **py:** adopt ty type checker; replace # type: ignore with cast

### Features

* **core:** portable keyset predicate (keyset_terms) for every adapter ([bed836a](https://github.com/CybLow/paginate/commit/bed836ac6f8989491fdedc0377734a4acec3dd27))
* **py:** add Django QuerySet adapter (offset, filter, sort, search, cursor) ([1be9b18](https://github.com/CybLow/paginate/commit/1be9b1807dac6e165ec3a7b5c7a57cbf2e170a54))
* **py:** new package foundation — generated types + flat behavior layer ([8f5db21](https://github.com/CybLow/paginate/commit/8f5db218c2550788e8b1053a14b4379d00a898bb))
* **py:** rebuild SQLAlchemy / Django / FastAPI adapters on the flat API ([04644e2](https://github.com/CybLow/paginate/commit/04644e28df8c16d189886163438078e023459454))
* **py:** swap to the new flat package — in-memory engine on generated types ([d70515c](https://github.com/CybLow/paginate/commit/d70515ceea89c5a45dc2eb4a60cd3c559d033e64))


### Bug Fixes

* **core:** fuzzy-aware native match-filter; drop the divergent Python score ([afdabb6](https://github.com/CybLow/paginate/commit/afdabb6d5632becf2e36118abaf09d00114b3d63))
* **py:** drop unused `cast` import in the SQLAlchemy keyset adapter ([e44ea58](https://github.com/CybLow/paginate/commit/e44ea58fdf05bb1a9a72b81ea8b6c92783867373))
* surface malformed keyset cursors as a public InvalidCursorError ([3c094f2](https://github.com/CybLow/paginate/commit/3c094f2b8abbac045af3ba3348d76746abc504f4))


### Performance

* **core:** fold search into the one-pass offset pipeline ([96b47b0](https://github.com/CybLow/paginate/commit/96b47b074519476d9a48bfb3e1489ad8b80c379f))
* **core:** trigram fuzzy search + exact inverted index (drop rapidfuzz) ([c67fa74](https://github.com/CybLow/paginate/commit/c67fa7459f39983c48bb1caa73d23d72e947797d))


### Refactoring

* **core:** complete v0.3 fat-core — reorg, domain SSOT, DX, perf ([930d075](https://github.com/CybLow/paginate/commit/930d0755bc59e442d4a94d7a5badc2ec8a354f28))
* **py:** adopt ty type checker; replace # type: ignore with cast ([7b90dcc](https://github.com/CybLow/paginate/commit/7b90dccf146636d28cf69ca04ec7ebc4fa2ee1cb))
* **py:** derive offset page metadata and clamping from the core ([6e620fa](https://github.com/CybLow/paginate/commit/6e620faf86a8f31e35be815147e88061f885a7af))
* **py:** make the native cursor codec the single source of truth ([2b5dd8c](https://github.com/CybLow/paginate/commit/2b5dd8c3c6809a73206cdcd05009a1b8aeae21c7))
* **py:** remove legacy in-memory engine facades and the CLI ([6a359cb](https://github.com/CybLow/paginate/commit/6a359cbbe0c2c5cc5b4b167cd2aa34122e1ece3d))
* **py:** render the core keyset predicate in the SQLAlchemy adapter ([cc37d4b](https://github.com/CybLow/paginate/commit/cc37d4b4a6a053ee37e0ddd5361998a1f219b02b))
* **py:** tighten engine/page return types (remove gratuitous Any) ([5c67b34](https://github.com/CybLow/paginate/commit/5c67b341410632c2e4d6fe7355e97ebadd978026))


### Documentation

* **core:** complete rustdoc + enforce missing_docs + docs.rs config ([9fefa61](https://github.com/CybLow/paginate/commit/9fefa61a1c3aa962e5b03b91aeef1a4b1f21c0b4))
* **py:** rewrite README and examples for the current public API ([7dee820](https://github.com/CybLow/paginate/commit/7dee820b3cfca5662e2907c5ab6dffc3bee0fc0c))


### Build

* **py:** make Pydantic an optional ([fastapi]) dependency, not a core one ([2e36374](https://github.com/CybLow/paginate/commit/2e36374254b64c22fbedcc370c231d1e86507276))
