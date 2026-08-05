import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const inputPath = resolve(projectRoot, 'all_posts.json');
const outputPath = resolve(projectRoot, 'assets', 'data', 'archive-index.json');

const PUBLIC_CARD_FIELDS = [
  'id', 'slug', 'cat', 'catCls', 'img',
  'title', 'title_pt', 'title_en',
  'excerpt', 'excerpt_pt', 'excerpt_en',
  'date', 'date_pt', 'date_en',
  'time', 'time_pt', 'time_en',
  'read', 'read_pt', 'read_en',
  'publishedIso', 'lastModifiedIso',
  'source', 'sourceDomain', 'sourceType', 'editorialBand',
  'keywords', 'keywords_pt', 'keywords_en',
  'srcUrl', 'featured', 'trending', 'isPreprint',
  'score', 'scoreBreakdown', 'video', 'audio'
];

const posts = JSON.parse(await readFile(inputPath, 'utf8'));
if (!Array.isArray(posts)) throw new TypeError('all_posts.json precisa conter uma lista.');

const index = posts
  .filter(post => post && post.slug)
  .map(post => Object.fromEntries(
    PUBLIC_CARD_FIELDS
      .filter(key => {
        const value = post[key];
        return value !== undefined && value !== null && value !== '' && (!Array.isArray(value) || value.length > 0);
      })
      .map(key => [key, post[key]])
  ));

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(index)}\n`, 'utf8');

const sizeMb = Buffer.byteLength(JSON.stringify(index)) / 1024 / 1024;
console.log(`Arquivo público criado: ${index.length} matérias, ${sizeMb.toFixed(2)} MB.`);
