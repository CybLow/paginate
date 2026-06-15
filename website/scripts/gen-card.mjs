// Rasterizes the social/OG card SVG to PNG (1200x630) with @resvg/resvg-js.
// Run: bun run gen:card  (the PNG is committed; regenerate after editing the SVG).
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { Resvg } from "@resvg/resvg-js";

const here = dirname(fileURLToPath(import.meta.url));
const img = join(here, "..", "static", "img");
const svg = readFileSync(join(img, "social-card.svg"), "utf8");

const resvg = new Resvg(svg, {
  fitTo: { mode: "width", value: 1200 },
  font: { loadSystemFonts: true },
});
const png = resvg.render().asPng();
writeFileSync(join(img, "social-card.png"), png);
console.log(`wrote social-card.png (${png.length} bytes)`);
