# Changelog

## [1.0.0](https://github.com/CybLow/paginate/compare/core-v0.1.0...core-v1.0.0) (2026-06-15)


### ⚠ BREAKING CHANGES

* **core:** complete v0.3 fat-core — reorg, domain SSOT, DX, perf
* **core:** fuzzy/token-sort scores and ranking differ from the old rapidfuzz output, and the default search threshold is now 30 (was 75). Trigram is strong on names/titles/multi-word text but weaker on very short single-word typos. The FuzzyMode API and field/threshold knobs are unchanged.

### Features

* **core:** generate wire types from a JSON Schema source of truth ([7c99a59](https://github.com/CybLow/paginate/commit/7c99a59df4ea42c4b9b2b62c2e8159a243d16e51))
* **core:** portable keyset predicate (keyset_terms) for every adapter ([bed836a](https://github.com/CybLow/paginate/commit/bed836ac6f8989491fdedc0377734a4acec3dd27))


### Bug Fixes

* **core:** fuzzy-aware native match-filter; drop the divergent Python score ([afdabb6](https://github.com/CybLow/paginate/commit/afdabb6d5632becf2e36118abaf09d00114b3d63))


### Performance

* **core:** decorate-sort + alloc-free fuzzy scoring (in-memory hot paths) ([3f744c7](https://github.com/CybLow/paginate/commit/3f744c78eb7046b27102027baacac22e556d5a50))
* **core:** fold search into the one-pass offset pipeline ([96b47b0](https://github.com/CybLow/paginate/commit/96b47b074519476d9a48bfb3e1489ad8b80c379f))
* **core:** hoist tokens + early-exit cutoff in fuzzy ranked search ([93d8783](https://github.com/CybLow/paginate/commit/93d8783f8536b1dcb6b799eee9e986b1dba60596))
* **core:** single-pass ASCII text normalization (one allocation) ([408bea5](https://github.com/CybLow/paginate/commit/408bea54acfcf8df14c322f1d4e535638a7013ff))
* **core:** trigram fuzzy search + exact inverted index (drop rapidfuzz) ([c67fa74](https://github.com/CybLow/paginate/commit/c67fa7459f39983c48bb1caa73d23d72e947797d))
* profiling-led resident-engine optimization, hardening, and cleanup ([126e459](https://github.com/CybLow/paginate/commit/126e45965a9c0734b9a539babd81e4586408a64d))


### Refactoring

* **core:** complete v0.3 fat-core — reorg, domain SSOT, DX, perf ([930d075](https://github.com/CybLow/paginate/commit/930d0755bc59e442d4a94d7a5badc2ec8a354f28))


### Documentation

* **core:** complete rustdoc + enforce missing_docs + docs.rs config ([9fefa61](https://github.com/CybLow/paginate/commit/9fefa61a1c3aa962e5b03b91aeef1a4b1f21c0b4))
* **core:** update crate metadata for the shipped TypeScript port ([45519b4](https://github.com/CybLow/paginate/commit/45519b4d91074cb1ff7054ff177c224feb839580))
