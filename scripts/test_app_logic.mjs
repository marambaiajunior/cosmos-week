// Offline regression checks for application logic; no browser or live services.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const source = await readFile(new URL('../assets/js/app.js', import.meta.url), 'utf8');
const bookSource = await readFile(new URL('../assets/js/book.js', import.meta.url), 'utf8');
let passed = 0;

function element() {
  const attrs = new Map();
  const classes = new Set();
  return {
    dataset: {}, value: '', innerHTML: '', textContent: '', style: {}, listeners: new Map(),
    classList: {
      add: (...names) => names.forEach(name => classes.add(name)),
      remove: (...names) => names.forEach(name => classes.delete(name)),
      contains: name => classes.has(name),
      toggle(name, force = !classes.has(name)) { if (force) classes.add(name); else classes.delete(name); return force; },
    },
    setAttribute(name, value) { attrs.set(name, String(value)); },
    getAttribute(name) { return attrs.get(name) ?? null; },
    removeAttribute(name) { attrs.delete(name); },
    addEventListener(name, fn) { this.listeners.set(name, [...(this.listeners.get(name) || []), fn]); },
    appendChild() {}, insertAdjacentElement() {}, focus() {},
    querySelector() { return null; }, querySelectorAll() { return []; },
  };
}

function runtime({ brokenStorage = false } = {}) {
  const nodes = new Map();
  const listeners = new Map();
  const requests = [];
  const memory = new Map();
  const location = { pathname: '/', search: '', hash: '', href: 'https://www.cosmosweek.com/', origin: 'https://www.cosmosweek.com', reload() {}, assign() {} };
  const document = {
    readyState: 'loading', title: '', body: element(), documentElement: element(),
    addEventListener(type, fn) { listeners.set(type, [...(listeners.get(type) || []), fn]); },
    getElementById(id) { if (!nodes.has(id)) nodes.set(id, element()); return nodes.get(id); },
    querySelector() { return null; }, querySelectorAll() { return []; },
    createElement(tag) {
      const node = element();
      if (tag === 'textarea') Object.defineProperty(node, 'value', { get: () => node.innerHTML });
      if (tag === 'div') Object.defineProperty(node, 'textContent', { get: () => node.innerHTML.replace(/<[^>]*>/g, '') });
      return node;
    },
  };
  const storage = {
    getItem(key) { if (brokenStorage) throw new Error('Storage denied'); return memory.get(key) || null; },
    setItem(key, value) { if (brokenStorage) throw new Error('Storage denied'); memory.set(key, value); },
  };
  const context = vm.createContext({
    console, document, location, URL, URLSearchParams, AbortController, CSS: { escape: String },
    localStorage: storage, sessionStorage: storage, navigator: {},
    setTimeout, clearTimeout, requestAnimationFrame: fn => fn(),
    history: { state: null, replaceState() {}, pushState() {} },
    addEventListener() {}, scrollTo() {}, matchMedia: () => ({ matches: false }),
    fetch: async url => { requests.push(url); throw new Error('Offline'); },
  });
  context.window = context;
  vm.runInContext(source, context);
  return { context, nodes, requests, document, listeners, run: code => vm.runInContext(code, context) };
}

async function check(name, fn) {
  await fn();
  passed += 1;
  console.log(`PASS ${name}`);
}

await check('blocked storage does not prevent startup or language selection', () => {
  const env = runtime({ brokenStorage: true });
  env.run('applyUIStrings = () => {}; rerenderCurrentView = () => {}; syncCurrentRouteUrl = () => {};');
  return env.run("setLanguage('en')").then(() => assert.equal(env.run('currentLang'), 'en'));
});

await check('returning visitors fetch the current edition even with cached stories', async () => {
  const env = runtime();
  env.run("DB = [{slug:'old-story',title:'Old',publishedIso:'2026-01-01'}];");
  let calls = 0;
  env.context.fetch = async () => { calls += 1; return { ok: true, json: async () => [{ slug: 'new-story', title: 'New', publishedIso: '2026-09-07' }] }; };
  await Promise.all([env.run('ensureSummaryFeedLoaded()'), env.run('ensureSummaryFeedLoaded()')]);
  assert.equal(calls, 1);
  assert.equal(env.run('DB[0].slug'), 'new-story');
  assert.equal(env.run('fullArchiveLoaded'), false);
});

await check('refresh failures remain failures instead of claiming success', async () => {
  const env = runtime();
  await assert.rejects(env.run('ensureSummaryFeedLoaded(true)'));
  assert.equal(env.run('summaryFeedLoaded'), false);
});

await check('archive failure is reported and retry can recover', async () => {
  const env = runtime();
  await env.run('ensureFullArchiveLoaded()');
  assert.equal(env.run('fullArchiveLoaded'), false);
  assert.equal(env.run('archiveLoadFailed'), true);
  assert.match(env.run('archiveStatusMarkup()'), /Tentar novamente/);
  env.context.fetch = async () => ({ ok: true, json: async () => [{ slug: 'recovered', title: 'Recovered' }] });
  await env.run('ensureFullArchiveLoaded()');
  assert.equal(env.run('fullArchiveLoaded'), true);
  assert.equal(env.run('archiveLoadFailed'), false);
});

await check('Portuguese article body does not satisfy an English article request', () => {
  const env = runtime();
  env.run("var article = {body:'p'.repeat(200),body_pt:'p'.repeat(200)};");
  assert.equal(env.run("articleHasBody(article, 'pt')"), true);
  assert.equal(env.run("articleHasBody(article, 'en')"), false);
});

await check('navigation away invalidates a pending article response', () => {
  const env = runtime();
  const token = env.run('articleNavigationToken');
  env.run("activatePage('home')");
  assert.equal(env.run('articleNavigationToken'), token + 1);
});

await check('search loads the complete archive and renders only a page of results', async () => {
  const env = runtime();
  env.run('markNav = () => {}; updateMetaStatic = () => {}; cardMarkup = post => `<article>${post.slug}</article>`;');
  env.context.fetch = async () => ({ ok: true, json: async () => Array.from({ length: 100 }, (_, i) => ({ slug: `star-${i}`, title: 'Estrela distante' })) });
  env.run("renderSearch('estrela')");
  await env.run('ensureFullArchiveLoaded()');
  await Promise.resolve();
  assert.equal(env.run('currentSearchResults.length'), 100);
  assert.equal((env.nodes.get('searchGrid').innerHTML.match(/<article>/g) || []).length, 30);
  assert.equal(env.nodes.get('searchLoadMore').hidden, false);
  assert.match(env.nodes.get('searchLoadMore').textContent, /70/);
});

await check('feed text cannot become markup in headline cards', () => {
  const env = runtime();
  const card = env.run("cardMarkup({slug:'safe',title:'<img src=x onerror=alert(1)>',cat:'Astronomia',source:'Source'})");
  assert.match(card, /&lt;img/);
  assert.doesNotMatch(card, /<h3[^>]*><img/);
});

await check('book script does not attach a second menu handler on portal pages', () => {
  const env = runtime();
  env.document.body.dataset.cwPage = 'home';
  const before = env.listeners.get('DOMContentLoaded')?.length || 0;
  vm.runInContext(bookSource, env.context);
  const callbacks = env.listeners.get('DOMContentLoaded').slice(before);
  callbacks.forEach(fn => fn());
  assert.equal(env.nodes.get('mobileNavToggle')?.listeners.get('click')?.length || 0, 0);
});

console.log(`Application logic: ${passed} regression cases passed.`);
