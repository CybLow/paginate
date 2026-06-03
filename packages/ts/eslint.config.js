// Flat ESLint config (ESLint 9 + typescript-eslint), non-type-aware recommended
// rules — fast and sufficient for this thin adapter package.
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist/", "node_modules/"] },
  ...tseslint.configs.recommended,
);
