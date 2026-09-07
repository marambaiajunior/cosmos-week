import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const fields = JSON.parse(await readFile(resolve(root, 'scripts/public_card_fields.json'), 'utf8'));

function compactCard(post, archive = false) {
  const source = { ...post, imageCount: post.inline_images?.length || post.imageCount || 0 };
  return Object.fromEntries(fields.filter(key => {
    const value = source[key];
    if (archive && ['sub', 'sub_pt', 'sub_en'].includes(key)) return false;
    if (archive && key.startsWith('shareUrl_')) {
      const route = key.endsWith('_en') ? 'en/news' : 'noticia';
      if (value === `https://www.cosmosweek.com/${route}/${encodeURIComponent(post.slug)}/`) return false;
    }
    if (value === undefined || value === null || value === '' || (Array.isArray(value) && !value.length)) return false;
    // The reader falls back to the unsuffixed field in either language.
    if (/_(pt|en)$/.test(key) && fields.includes(key.slice(0, -3)) && JSON.stringify(value) === JSON.stringify(source[key.slice(0, -3)])) return false;
    return true;
  }).map(key => [key, source[key]]));
}

for (const [input, output] of [
  ['posts.json', 'assets/data/posts-index.json'],
  ['all_posts.json', 'assets/data/archive-index.json'],
]) {
  const posts = JSON.parse(await readFile(resolve(root, input), 'utf8'));
  if (!Array.isArray(posts) || !posts.length) throw new TypeError(`${input} precisa conter uma lista não vazia.`);
  const index = posts.filter(post => post && post.slug).map(post => compactCard(post, input === 'all_posts.json'));
  if (new Set(index.map(post => post.slug)).size !== index.length) throw new Error(`Slugs duplicados em ${input}`);
  const bytes = `${JSON.stringify(index)}\n`;
  await mkdir(dirname(resolve(root, output)), { recursive: true });
  await writeFile(resolve(root, output), bytes, 'utf8');
  console.log(`${output}: ${index.length} matérias, ${(Buffer.byteLength(bytes) / 1024).toFixed(1)} KB.`);
}
