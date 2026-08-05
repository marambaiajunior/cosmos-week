import { readdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ignoredDirectories = new Set(['.git', '.github', 'node_modules', 'scripts']);

async function findHtmlFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    if (entry.name.startsWith('.') && entry.isDirectory()) continue;
    const absolutePath = join(directory, entry.name);

    if (entry.isDirectory()) {
      if (!ignoredDirectories.has(entry.name)) files.push(...await findHtmlFiles(absolutePath));
    } else if (extname(entry.name).toLowerCase() === '.html') {
      files.push(absolutePath);
    }
  }

  return files;
}

function escapeXml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;');
}

function attribute(tag, name) {
  return tag.match(new RegExp(`${name}=["']([^"']+)["']`, 'i'))?.[1] || '';
}

const canonicalPages = new Map();

for (const file of await findHtmlFiles(root)) {
  const html = await readFile(file, 'utf8');
  const canonicalTag = html.match(/<link\b[^>]*\brel=["']canonical["'][^>]*>/i)?.[0]
    || html.match(/<link\b[^>]*\bhref=["'][^"']+["'][^>]*\brel=["']canonical["'][^>]*>/i)?.[0];

  if (!canonicalTag) continue;

  const canonical = attribute(canonicalTag, 'href');
  if (!/^https:\/\/(?:www\.)?cosmosweek\.com\//i.test(canonical) || canonical.includes('?')) continue;

  const modifiedTag = html.match(/<meta\b[^>]*\bproperty=["']article:modified_time["'][^>]*>/i)?.[0];
  const publishedTag = html.match(/<meta\b[^>]*\bproperty=["']article:published_time["'][^>]*>/i)?.[0];
  const rawDate = attribute(modifiedTag || publishedTag || '', 'content');
  const lastModified = /^\d{4}-\d{2}-\d{2}/.test(rawDate) ? rawDate.slice(0, 10) : '';

  const current = canonicalPages.get(canonical);
  if (!current?.lastModified || lastModified > current.lastModified) {
    canonicalPages.set(canonical, { lastModified });
  }
}

const urls = [...canonicalPages.entries()].sort(([left], [right]) => left.localeCompare(right));
const rows = urls.map(([url, { lastModified }]) => {
  const lastmod = lastModified ? `\n    <lastmod>${lastModified}</lastmod>` : '';
  return `  <url>\n    <loc>${escapeXml(url)}</loc>${lastmod}\n  </url>`;
});

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${rows.join('\n')}\n</urlset>\n`;
await writeFile(resolve(root, 'sitemap.xml'), sitemap, 'utf8');

console.log(`Sitemap atualizado: ${urls.length} URLs canônicas.`);
