import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const pages = [
  'index.html',
  'arquivo/index.html',
  'sobre/index.html',
  'padroes/index.html',
  'en/index.html',
  'en/archive/index.html',
  'en/about/index.html',
  'en/standards/index.html'
];

const mobileMenu = '<button aria-controls="mainNav" aria-expanded="false" aria-label="Abrir menu" class="mobile-nav-toggle" id="mobileNavToggle" type="button"><span></span><span></span><span></span></button>';

for (const relativePath of pages) {
  const path = resolve(root, relativePath);
  let html = await readFile(path, 'utf8');
  const original = html;
  const isEnglish = /<html[^>]+lang="en/i.test(html) || relativePath.startsWith('en/');

  html = html.replace(
    /<link as="image" fetchpriority="high" href="https:\/\/www\.cosmosweek\.com\/assets\/og-default\.jpg" rel="preload"\/>\s*/g,
    ''
  );

  if (!html.includes('/assets/css/modern.css')) {
    html = html.replace(
      /<link href="\/assets\/css\/main\.css" rel="stylesheet"\s*\/>/,
      '<link href="/assets/css/main.css" rel="stylesheet"/>\n<link href="/assets/css/modern.css" rel="stylesheet"/>'
    );
  }

  if (!html.includes('/assets/favicon.svg')) {
    html = html.replace(
      /<link href="\/assets\/css\/main\.css"/,
      '<link href="/assets/favicon.svg" rel="icon" type="image/svg+xml"/>\n<link href="/site.webmanifest" rel="manifest"/>\n<link href="/assets/css/main.css"'
    );
  }

  html = html.replace(/class="phase3-premium(?![^"]*modern-editorial)/, 'class="phase3-premium modern-editorial');
  html = html.replace(/data-ui-phase="3"/, 'data-ui-phase="4"');
  html = html.replace(/<body([^>]*)>/i, (match, attrs) => {
    let next = attrs;
    if (/class="[^"]*"/.test(next)) {
      next = next.replace(/class="([^"]*)"/, (classMatch, classes) => {
        const values = new Set(classes.split(/\s+/).filter(Boolean));
        values.add('phase3-premium');
        values.add('modern-editorial');
        return `class="${[...values].join(' ')}"`;
      });
    } else {
      next = ` class="phase3-premium modern-editorial"${next}`;
    }
    if (/data-ui-phase="[^"]*"/.test(next)) next = next.replace(/data-ui-phase="[^"]*"/, 'data-ui-phase="4"');
    else next += ' data-ui-phase="4"';
    return `<body${next}>`;
  });

  if (!html.includes('id="mobileNavToggle"')) {
    html = html.replace(/(<nav[^>]+class="main-nav"[^>]*id="mainNav"[^>]*>)/, `${mobileMenu}\n$1`);
  }

  html = html.replace(/<a([^>]*id="langPt"[^>]*)>[^<]*<\/a>/, (match, attrs) => {
    const next = /aria-label=/.test(attrs) ? attrs : ` aria-label="Português"${attrs}`;
    return `<a${next}>PT</a>`;
  });
  html = html.replace(/<a([^>]*id="langEn"[^>]*)>[^<]*<\/a>/, (match, attrs) => {
    const next = /aria-label=/.test(attrs) ? attrs : ` aria-label="English"${attrs}`;
    return `<a${next}>EN</a>`;
  });

  if (!html.includes('data-cat="all"')) {
    html = html.replace(
      /(<div class="catbar-inner" id="catbarInner">)/,
      `$1<button aria-pressed="true" class="cat-pill on" data-cat="all" onclick="setCategory('all',this)">${isEnglish ? 'All' : 'Todas'}</button>\n`
    );
  }

  html = html.replace(/<input([^>]*id="searchInput"[^>]*)>/, (match, attrs) => {
    if (/aria-label=/.test(attrs)) return match;
    return `<input aria-label="${isEnglish ? 'Search Cosmos Week' : 'Buscar no Cosmos Week'}"${attrs}>`;
  });
  html = html.replace('<div class="toast" id="toast"></div>', '<div aria-live="polite" class="toast" id="toast" role="status"></div>');
  html = html.replace(/\s*·\s*<a href="\/guias\/">Guias<\/a><\/footer>/, '</footer>');

  if (html !== original) {
    await writeFile(path, html, 'utf8');
    console.log(`Atualizada: ${relativePath}`);
  }
}
