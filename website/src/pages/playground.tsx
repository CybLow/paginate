import { useEffect, useMemo, useState, type ReactNode } from 'react';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';
import CodeBlock from '@theme/CodeBlock';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './playground.module.css';

// The same Rust core that backs pypaginate and @cyblow/paginate, compiled to
// WebAssembly and run live in the browser. The module is loaded at runtime from
// /static (webpackIgnore keeps the bundler from trying to process it).
type Wasm = {
  default: (input?: unknown) => Promise<unknown>;
  filter: (items: string, field: string, operator: string, value: string) => string;
  sort: (items: string, field: string, direction: string) => string;
  search: (items: string, query: string, fields: string, fuzzy: string) => string;
  encodeCursor: (values: string) => string;
  decodeCursor: (cursor: string) => string;
};

const SAMPLE = JSON.stringify(
  [
    { id: 1, name: 'Alice Johnson', age: 30, role: 'admin' },
    { id: 2, name: 'Bob Alice', age: 17, role: 'user' },
    { id: 3, name: 'Carol Smith', age: 25, role: 'owner' },
    { id: 4, name: 'Dave Brown', age: 41, role: 'user' },
    { id: 5, name: 'Eve Davis', age: 22, role: 'user' },
  ],
  null,
  2,
);

const OPERATORS = [
  'eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in', 'contains', 'starts_with',
  'ends_with', 'like', 'ilike', 'between', 'is_null', 'is_not_null', 'regex',
  'empty', 'not_empty', 'exists',
];

function pretty(json: string): string {
  try {
    return JSON.stringify(JSON.parse(json), null, 2);
  } catch {
    return json;
  }
}

function run(fn: () => string): string {
  try {
    return pretty(fn());
  } catch (err) {
    return `// error: ${(err as Error).message}`;
  }
}

function Editor({ wasm }: { wasm: Wasm }): ReactNode {
  const [data, setData] = useState(SAMPLE);

  const [fField, setFField] = useState('age');
  const [fOp, setFOp] = useState('gte');
  const [fVal, setFVal] = useState('18');

  const [sField, setSField] = useState('name');
  const [sDir, setSDir] = useState('asc');

  const [query, setQuery] = useState('alice');
  const [sFields, setSFields] = useState('name');
  const [fuzzy, setFuzzy] = useState('exact');

  const [cursorValues, setCursorValues] = useState('[3, "2025-06-01T00:00:00"]');

  const filtered = useMemo(
    () => run(() => wasm.filter(data, fField, fOp, fVal || 'null')),
    [wasm, data, fField, fOp, fVal],
  );
  const sorted = useMemo(
    () => run(() => wasm.sort(data, sField, sDir)),
    [wasm, data, sField, sDir],
  );
  const searched = useMemo(
    () => run(() => wasm.search(data, query, JSON.stringify(sFields.split(',').map((s) => s.trim()).filter(Boolean)), fuzzy)),
    [wasm, data, query, sFields, fuzzy],
  );
  const encoded = useMemo(() => run(() => wasm.encodeCursor(cursorValues)), [wasm, cursorValues]);
  const roundTrip = useMemo(
    () => run(() => wasm.decodeCursor(wasm.encodeCursor(cursorValues))),
    [wasm, cursorValues],
  );

  return (
    <>
      <div className={styles.panel}>
        <h3>Dataset (JSON)</h3>
        <div className={styles.dataset}>
          <textarea value={data} onChange={(e) => setData(e.target.value)} spellCheck={false} />
        </div>
      </div>

      <div className={styles.grid}>
        <div className={styles.panel}>
          <h3>filter</h3>
          <div className={styles.controls}>
            <label>field<input value={fField} onChange={(e) => setFField(e.target.value)} /></label>
            <label>operator
              <select value={fOp} onChange={(e) => setFOp(e.target.value)}>
                {OPERATORS.map((op) => <option key={op} value={op}>{op}</option>)}
              </select>
            </label>
            <label>value (JSON)<input value={fVal} onChange={(e) => setFVal(e.target.value)} /></label>
          </div>
          <CodeBlock language="json">{filtered}</CodeBlock>
        </div>

        <div className={styles.panel}>
          <h3>sort</h3>
          <div className={styles.controls}>
            <label>field<input value={sField} onChange={(e) => setSField(e.target.value)} /></label>
            <label>direction
              <select value={sDir} onChange={(e) => setSDir(e.target.value)}>
                <option value="asc">asc</option>
                <option value="desc">desc</option>
              </select>
            </label>
          </div>
          <CodeBlock language="json">{sorted}</CodeBlock>
        </div>

        <div className={styles.panel}>
          <h3>search</h3>
          <div className={styles.controls}>
            <label>query<input value={query} onChange={(e) => setQuery(e.target.value)} /></label>
            <label>fields (csv)<input value={sFields} onChange={(e) => setSFields(e.target.value)} /></label>
            <label>fuzzy
              <select value={fuzzy} onChange={(e) => setFuzzy(e.target.value)}>
                <option value="exact">exact</option>
                <option value="fuzzy">fuzzy</option>
                <option value="token_sort">token_sort</option>
              </select>
            </label>
          </div>
          <CodeBlock language="json">{searched}</CodeBlock>
        </div>

        <div className={styles.panel}>
          <h3>cursor codec</h3>
          <div className={styles.controls}>
            <label style={{ flex: 1 }}>ordering values (JSON array)
              <input value={cursorValues} onChange={(e) => setCursorValues(e.target.value)} />
            </label>
          </div>
          <CodeBlock language="text">{`encodeCursor → ${encoded}\ndecodeCursor(encodeCursor(…)) → ${roundTrip}`}</CodeBlock>
        </div>
      </div>
    </>
  );
}

function Loader(): ReactNode {
  const jsUrl = useBaseUrl('/playground/pkg/paginate_wasm.js');
  const [wasm, setWasm] = useState<Wasm | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const mod = (await import(/* webpackIgnore: true */ jsUrl)) as Wasm;
        await mod.default();
        if (active) setWasm(mod);
      } catch (err) {
        if (active) setError(String(err));
      }
    })();
    return () => {
      active = false;
    };
  }, [jsUrl]);

  if (error) return <p className={styles.status}>Failed to load the WebAssembly engine: {error}</p>;
  if (!wasm) return <p className={styles.status}>Loading the WebAssembly engine…</p>;
  return <Editor wasm={wasm} />;
}

export default function PlaygroundPage(): ReactNode {
  return (
    <Layout
      title="Playground"
      description="Run paginate's Rust core live in your browser (compiled to WebAssembly): filter, sort, search, and the portable cursor codec."
    >
      <main className="container margin-vert--lg">
        <h1>Playground</h1>
        <p className={styles.intro}>
          This runs <strong>the actual Rust core</strong> — the same engine behind{' '}
          <code>pypaginate</code> and <code>@cyblow/paginate</code> — compiled to WebAssembly and
          executed in your browser. Edit the dataset and parameters; results update live. Cursors
          minted here decode byte-for-byte in Python and TypeScript.
        </p>
        <BrowserOnly fallback={<p className={styles.status}>Loading…</p>}>{() => <Loader />}</BrowserOnly>
      </main>
    </Layout>
  );
}
