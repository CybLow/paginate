# Changelog

## [1.0.0](https://github.com/CybLow/paginate/compare/core-v0.1.0...core-v1.0.0) (2026-06-04)


### ⚠ BREAKING CHANGES

* rename to paginate-core; native-first polyglot layout

### Features

* **core:** one-call pipeline — filter+sort+paginate in a single pass ([639d641](https://github.com/CybLow/paginate/commit/639d641b11e7b6bf6d9f2d2407d0cc4327c84d53))
* **core:** real fuzzy scoring (partial_ratio + token_sort_ratio) — task [#10](https://github.com/CybLow/paginate/issues/10) ([428687c](https://github.com/CybLow/paginate/commit/428687cd2a15cfc2b057c412001ce9f589725e2c))
* **core:** type stubs, typed errors, columnar multi-key/filter; arch + tooling hardening ([c055e5d](https://github.com/CybLow/paginate/commit/c055e5de7362ad0ae8c7af5e49294b8d1aac8e33))
* match-filter search variant + complete benchmark picture ([72d5f1d](https://github.com/CybLow/paginate/commit/72d5f1d3d320d1f4974eaaebb2d9d76b78508ed3))


### Performance

* **core:** columnar Bool columns — ~8x faster bool-inclusive filters ([ba3aee3](https://github.com/CybLow/paginate/commit/ba3aee30f4d0702c4860b4af4b1093b240be959d))
* **core:** columnar filter/sort/pipeline (int/float/str) + Node/TS Dataset ([62e0725](https://github.com/CybLow/paginate/commit/62e07250aaa0e668936b58548d2ebdebb92a549f))
* **core:** columnar int-filter fast path (10.8x -&gt; 29x) ([16fece4](https://github.com/CybLow/paginate/commit/16fece4a2d98f72d495ad6ff7fad924cf6c9a8d3))


### Refactoring

* rename to paginate-core; native-first polyglot layout ([9e30b8d](https://github.com/CybLow/paginate/commit/9e30b8df23077e803cf649c9140a7cd6dd940902))
