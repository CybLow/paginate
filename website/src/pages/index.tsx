import type { ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import CodeBlock from '@theme/CodeBlock';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import styles from './index.module.css';

const PYTHON_SAMPLE = `from pypaginate import paginate, filter, OffsetParams, FilterSpec

page = paginate(users, OffsetParams(page=1, limit=20))
page.total        # 1_000
page.has_next     # True

adults = filter(users, FilterSpec(field="age", operator="gte", value=18))`;

const TS_SAMPLE = `import { paginate, filter, OffsetParams } from "@cyblow/paginate";

const page = paginate(users, new OffsetParams({ page: 1, limit: 20 }));
page.total;       // 1_000
page.hasNext;     // true

const adults = filter(users, { field: "age", operator: "gte", value: 18 });`;

function Hero(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.hero)}>
      <div className="container">
        <h1 className={styles.heroTitle}>
          One pagination engine.<br />
          <span className={styles.heroAccent}>Every language.</span>
        </h1>
        <p className={styles.heroTagline}>{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link className="button button--primary button--lg" to="/docs/">
            Get started →
          </Link>
          <Link className="button button--secondary button--lg" to="/docs/general/why">
            Why paginate?
          </Link>
        </div>
        <div className={styles.install}>
          <code>pip install pypaginate</code>
          <span className={styles.installSep}>·</span>
          <code>npm i @cyblow/paginate</code>
          <span className={styles.installSep}>·</span>
          <code>cargo add paginate-core</code>
        </div>
      </div>
    </header>
  );
}

function ParityShowcase(): ReactNode {
  return (
    <section className={styles.showcase}>
      <div className="container">
        <h2 className={styles.showcaseTitle}>Same API. Same results. Two languages.</h2>
        <p className={styles.showcaseSubtitle}>
          The Python and TypeScript packages are thin adapters over one Rust core, so they
          return identical filtered/sorted/ranked order — and <strong>byte-identical cursors</strong>.
        </p>
        <div className={styles.showcaseGrid}>
          <div className={styles.showcaseCol}>
            <CodeBlock language="python" title="Python · pypaginate">
              {PYTHON_SAMPLE}
            </CodeBlock>
          </div>
          <div className={styles.showcaseCol}>
            <CodeBlock language="typescript" title="TypeScript · @cyblow/paginate">
              {TS_SAMPLE}
            </CodeBlock>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title} — fast, parity-guaranteed pagination`}
      description="Fast pagination, filtering, sorting & search with one Rust core and native Python & TypeScript packages that return byte-for-byte identical results."
    >
      <Hero />
      <main>
        <HomepageFeatures />
        <ParityShowcase />
      </main>
    </Layout>
  );
}
