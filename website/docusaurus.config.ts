import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'paginate',
  tagline: 'Fast pagination, filtering, sorting & search — one Rust core, native Python & TypeScript packages',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // GitHub Pages: https://cyblow.github.io/paginate/
  url: 'https://cyblow.github.io',
  baseUrl: '/paginate/',
  organizationName: 'CybLow',
  projectName: 'paginate',

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/', // docs are the site root (docs-only project)
          editUrl: 'https://github.com/CybLow/paginate/tree/main/website/',
        },
        // Docs-only project: a library reference, not a blog.
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  // TypeScript API *reference*, generated from ts/src by TypeDoc — kept separate
  // from the usage Guides so "how to use it" and "the API surface" don't blur.
  plugins: [
    [
      'docusaurus-plugin-typedoc',
      {
        id: 'typescript-api',
        entryPoints: ['../ts/src/index.ts'],
        tsconfig: '../ts/tsconfig.json',
        out: 'docs/reference/typescript',
        readme: 'none',
        skipErrorChecking: true,
      },
    ],
  ],

  // Offline full-text search (Docusaurus ships none) — no Algolia account needed.
  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexBlog: false,
        docsRouteBasePath: '/',
      },
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'paginate',
      logo: {
        alt: 'paginate logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://docs.rs/paginate-core',
          label: 'Rust API (docs.rs)',
          position: 'right',
        },
        {
          href: 'https://github.com/CybLow/paginate',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting started', to: '/getting-started/installation' },
            { label: 'Concepts', to: '/concepts/architecture' },
          ],
        },
        {
          title: 'Packages',
          items: [
            { label: 'pypaginate (PyPI)', href: 'https://pypi.org/project/pypaginate/' },
            { label: '@cyblow/paginate (npm)', href: 'https://www.npmjs.com/package/@cyblow/paginate' },
            { label: 'paginate-core (crates.io)', href: 'https://crates.io/crates/paginate-core' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'Rust API (docs.rs)', href: 'https://docs.rs/paginate-core' },
            { label: 'GitHub', href: 'https://github.com/CybLow/paginate' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} CybLow. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['rust', 'python', 'bash', 'toml', 'json'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
