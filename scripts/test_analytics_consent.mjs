import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';


const analyticsSource = await readFile(new URL('../assets/js/cw-analytics.js', import.meta.url), 'utf8');
const bookSource = await readFile(new URL('../assets/js/book.js', import.meta.url), 'utf8');


function fakeElement(tagName = 'div') {
  const tokens = new Set();
  return {
    tagName: tagName.toUpperCase(),
    id: '',
    className: '',
    innerHTML: '',
    textContent: '',
    attributes: new Map(),
    classList: {
      add: (...names) => names.forEach(name => tokens.add(name)),
      remove: (...names) => names.forEach(name => tokens.delete(name)),
      contains: name => tokens.has(name),
    },
    setAttribute(name, value) { this.attributes.set(name, String(value)); },
    getAttribute(name) { return this.attributes.get(name) ?? null; },
    appendChild() {},
    focus() {},
  };
}


function analyticsRuntime(savedConsent = '') {
  const listeners = new Map();
  const elements = new Map();
  const timers = [];
  const injectedScripts = [];
  const storage = new Map(savedConsent ? [['cw_cookie_consent', savedConsent]] : []);
  let timerId = 0;

  const firstScript = fakeElement('script');
  firstScript.parentNode = {
    insertBefore(element) {
      injectedScripts.push(element.src);
    },
  };

  const document = {
    currentScript: {
      getAttribute(name) { return name === 'data-ga-id' ? 'G-MX20J1ZG06' : null; },
    },
    readyState: 'loading',
    title: 'Vórtice Maligno',
    documentElement: { getAttribute: name => name === 'lang' ? 'pt-BR' : null },
    head: { appendChild(element) { if (element.tagName === 'SCRIPT' && element.src) injectedScripts.push(element.src); } },
    body: {
      appendChild(element) {
        if (element.id) elements.set(element.id, element);
      },
    },
    createElement: fakeElement,
    getElementsByTagName(name) { return name === 'script' ? [firstScript] : []; },
    getElementById(id) { return elements.get(id) || null; },
    querySelector(selector) {
      if (selector === 'script[data-ga-id]') return this.currentScript;
      if (selector === 'link[rel="canonical"]') return { getAttribute: () => 'https://www.cosmosweek.com/livro/vortice-maligno/' };
      return null;
    },
    addEventListener(type, handler) {
      const handlers = listeners.get(type) || [];
      handlers.push(handler);
      listeners.set(type, handlers);
    },
    dispatchEvent(event) {
      for (const handler of listeners.get(event.type) || []) handler(event);
    },
  };

  const context = {
    console,
    document,
    history: { pushState() {}, replaceState() {} },
    location: {
      href: 'https://www.cosmosweek.com/livro/vortice-maligno/',
      pathname: '/livro/vortice-maligno/',
      search: '',
    },
    localStorage: {
      getItem(key) { return storage.get(key) || null; },
      setItem(key, value) { storage.set(key, String(value)); },
    },
    URL,
    CustomEvent: class CustomEvent {
      constructor(type, options = {}) { this.type = type; this.detail = options.detail; }
    },
    setTimeout(handler) { timers.push(handler); timerId += 1; return timerId; },
    clearTimeout() {},
    addEventListener(type, handler) {
      const handlers = listeners.get(`window:${type}`) || [];
      handlers.push(handler);
      listeners.set(`window:${type}`, handlers);
    },
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(analyticsSource, context, { filename: 'cw-analytics.js' });

  function fire(type) {
    for (const handler of listeners.get(type) || []) handler({ type });
  }

  function runTimers() {
    while (timers.length) timers.shift()();
  }

  function events(name) {
    return (context.dataLayer || []).filter(args => args[0] === 'event' && (!name || args[1] === name));
  }

  return { context, fire, injectedScripts, runTimers, events, storage };
}


{
  const runtime = analyticsRuntime();
  assert.equal(runtime.injectedScripts.length, 0, 'GA must not load before consent');
  runtime.fire('DOMContentLoaded');
  runtime.runTimers();
  assert.equal(runtime.injectedScripts.length, 0, 'DOMContentLoaded must not bypass consent');
  assert.equal(runtime.events('page_view').length, 0, 'page_view must not fire before consent');

  runtime.context.setCookieConsent('denied');
  runtime.runTimers();
  assert.equal(runtime.injectedScripts.length, 0, 'declining must keep GA unloaded');
  assert.equal(runtime.events('page_view').length, 0, 'declining must keep page_view blocked');

  runtime.context.setCookieConsent('analytics');
  runtime.runTimers();
  assert.equal(runtime.injectedScripts.length, 1, 'analytics consent must load GA once');
  assert.equal(runtime.events('page_view').length, 1, 'analytics consent must produce one page_view');

  runtime.context.setCookieConsent('denied');
  runtime.context.cwTrackPageView({ force: true });
  runtime.runTimers();
  assert.equal(runtime.events('page_view').length, 1, 'withdrawal must block later page_view events');
}


{
  const runtime = analyticsRuntime('analytics');
  runtime.fire('DOMContentLoaded');
  runtime.runTimers();
  assert.equal(runtime.injectedScripts.length, 1, 'saved analytics consent must load GA once');
  assert.equal(runtime.events('page_view').length, 1, 'saved analytics consent must not duplicate page_view');
}


function bookRuntime() {
  const listeners = new Map();
  const analyticsEvents = [];
  let consent = false;
  const document = {
    readyState: 'loading',
    body: { getAttribute: name => name === 'data-cw-page' ? 'book' : null },
    addEventListener(type, handler) {
      const handlers = listeners.get(type) || [];
      handlers.push(handler);
      listeners.set(type, handlers);
    },
    dispatchEvent(event) {
      for (const handler of listeners.get(event.type) || []) handler(event);
    },
    getElementById() { return null; },
    querySelectorAll() { return []; },
  };
  const context = {
    console,
    document,
    location: { search: '', href: 'https://www.cosmosweek.com/livro/vortice-maligno/' },
    URLSearchParams,
    CustomEvent: class CustomEvent {
      constructor(type, options = {}) { this.type = type; this.detail = options.detail; }
    },
    navigator: {},
    Promise,
    setTimeout,
    clearTimeout,
    gtag(...args) { if (args[0] === 'event') analyticsEvents.push(args); },
    cwHasAnalyticsConsent() { return consent; },
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(bookSource, context, { filename: 'book.js' });
  for (const handler of listeners.get('DOMContentLoaded') || []) handler({ type: 'DOMContentLoaded' });
  assert.equal(analyticsEvents.length, 0, 'book events must wait for consent');
  consent = true;
  document.dispatchEvent(new context.CustomEvent('cw:analytics-consent-granted', { detail: { mode: 'analytics' } }));
  assert.deepEqual(analyticsEvents.map(args => args[1]), ['view_item', 'book_landing_view']);
  document.dispatchEvent(new context.CustomEvent('cw:analytics-consent-granted', { detail: { mode: 'analytics' } }));
  assert.equal(analyticsEvents.length, 2, 'product view must be deduplicated');
}


bookRuntime();
console.log('Analytics consent tests: PASS');
