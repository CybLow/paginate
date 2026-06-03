// Conventional Commits — enforced by the `commit-lint` CI job and (optionally)
// a local commit-msg hook. CommonJS so it loads without a "type":"module" root.
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Subjects can be a touch longer than the 72-char default for clarity.
    'header-max-length': [2, 'always', 100],
    // Scopes map to the monorepo layers (warning, not error — scope is optional).
    'scope-enum': [
      1,
      'always',
      ['core', 'pyo3', 'py', 'node', 'ts', 'docs', 'ci', 'repo', 'deps', 'release', 'bench'],
    ],
  },
};
