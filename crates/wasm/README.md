# paginate-wasm

WebAssembly bindings for [`paginate-core`](../core), powering the documentation
**[playground](https://cyblow.github.io/paginate/playground)**. The same Rust engine
that backs `pypaginate` and `@cyblow/paginate` runs here in the browser, so the
playground executes the real core — not a re-implementation.

It is **excluded from the cargo workspace** (it builds only for `wasm32`) and exposes a
small JSON-in/JSON-out surface: `filter`, `sort`, `search`, `encodeCursor`,
`decodeCursor`.

## Regenerating the bundle

The generated bundle is committed to `website/static/playground/pkg/` (the docs deploy
serves it as a static asset — it does not build wasm in CI). Regenerate it after
changing the core or this crate:

```bash
# one-time setup
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli   # must match the wasm-bindgen crate version in Cargo.toml

# build + generate the web-target JS glue into the site's static dir
cd crates/wasm
cargo build --target wasm32-unknown-unknown --release
wasm-bindgen --target web \
  --out-dir ../../website/static/playground/pkg \
  --out-name paginate_wasm \
  target/wasm32-unknown-unknown/release/paginate_wasm.wasm
rm -f ../../website/static/playground/pkg/*.d.ts   # runtime needs only .js + .wasm
```

The page loads `paginate_wasm.js` at runtime (a `webpackIgnore` dynamic import), and its
default `init()` fetches `paginate_wasm_bg.wasm` from the same directory.
