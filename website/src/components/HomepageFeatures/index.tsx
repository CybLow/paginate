import type { ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

type Feature = {
  icon: string;
  title: string;
  description: ReactNode;
};

const FEATURES: Feature[] = [
  {
    icon: '🦀',
    title: 'One Rust core',
    description: (
      <>
        Filtering, sorting, ranked search, the cursor codec, and pagination math live
        once in a native engine. The language packages are thin, typed adapters.
      </>
    ),
  },
  {
    icon: '🔗',
    title: 'Cross-language parity',
    description: (
      <>
        Python and TypeScript return the same order and <strong>byte-identical
        cursors</strong>, pinned by a frozen golden fixture asserted in CI.
      </>
    ),
  },
  {
    icon: '🔍',
    title: 'Filter, sort & search',
    description: (
      <>
        20 filter operators with nested <code>And</code>/<code>Or</code>, stable
        null-aware multi-key sorting, and ranked trigram fuzzy search.
      </>
    ),
  },
  {
    icon: '➡️',
    title: 'Cursor pagination',
    description: (
      <>
        Opaque, URL-safe keyset cursors that stay correct under writes and decode
        byte-for-byte across Python, TypeScript, and Rust.
      </>
    ),
  },
  {
    icon: '🧩',
    title: 'Framework integrations',
    description: (
      <>
        SQLAlchemy, Django, and FastAPI in Python; Express, Prisma, and Drizzle in
        TypeScript — built on the same portable predicate.
      </>
    ),
  },
  {
    icon: '🛡️',
    title: 'Typed & dependency-light',
    description: (
      <>
        Full type hints (Python) and types (TS) generated from one schema, so they
        can&apos;t drift. Zero runtime dependencies in the core.
      </>
    ),
  },
];

type LanguageCard = {
  emoji: string;
  name: string;
  pkg: string;
  to: string;
};

const LANGUAGES: LanguageCard[] = [
  { emoji: '🐍', name: 'Python', pkg: 'pypaginate', to: '/docs/python/installation' },
  { emoji: '🟦', name: 'TypeScript', pkg: '@cyblow/paginate', to: '/docs/typescript/installation' },
  { emoji: '🦀', name: 'Rust', pkg: 'paginate-core', to: '/docs/rust/overview' },
];

function FeatureCard({ icon, title, description }: Feature): ReactNode {
  return (
    <div className={styles.card}>
      <div className={styles.cardIcon} aria-hidden="true">
        {icon}
      </div>
      <h3 className={styles.cardTitle}>{title}</h3>
      <p className={styles.cardBody}>{description}</p>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.grid}>
          {FEATURES.map((f) => (
            <FeatureCard key={f.title} {...f} />
          ))}
        </div>

        <h2 className={styles.pickTitle}>Pick your language</h2>
        <div className={styles.langGrid}>
          {LANGUAGES.map((l) => (
            <Link key={l.name} className={clsx(styles.card, styles.langCard)} to={l.to}>
              <span className={styles.langEmoji} aria-hidden="true">
                {l.emoji}
              </span>
              <span className={styles.langName}>{l.name}</span>
              <code className={styles.langPkg}>{l.pkg}</code>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
