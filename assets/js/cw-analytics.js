(function () {
  'use strict';

  var DEFAULT_GA_ID = 'G-MX20J1ZG06';
  var CONSENT_KEY = 'cw_cookie_consent';
  var TRACKED_URL = '';
  var trackingTimer = 0;

  function currentScript() {
    return document.currentScript || document.querySelector('script[data-ga-id]');
  }

  function getMeasurementId() {
    var script = currentScript();
    var id = script && script.getAttribute('data-ga-id');
    return (id || DEFAULT_GA_ID || '').trim();
  }

  var GA_ID = getMeasurementId();
  if (!GA_ID) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag(){ window.dataLayer.push(arguments); };

  function normalizeConsent(mode) {
    mode = String(mode || '').toLowerCase().trim();
    if (mode === 'granted' || mode === 'accept' || mode === 'accepted' || mode === 'analytics-only') return 'analytics';
    if (mode === 'all' || mode === 'full' || mode === 'allow-all') return 'full';
    if (mode === 'deny' || mode === 'declined' || mode === 'reject' || mode === 'rejected') return 'denied';
    if (mode === 'analytics' || mode === 'denied') return mode;
    return '';
  }

  function consentSignals(mode) {
    var normalized = normalizeConsent(mode);
    var full = normalized === 'full';
    var analytics = normalized === 'full' || normalized === 'analytics';
    return {
      analytics_storage: analytics ? 'granted' : 'denied',
      ad_storage: full ? 'granted' : 'denied',
      ad_user_data: full ? 'granted' : 'denied',
      ad_personalization: full ? 'granted' : 'denied'
    };
  }

  function getSavedConsent() {
    try { return normalizeConsent(localStorage.getItem(CONSENT_KEY)); }
    catch (e) { return ''; }
  }

  function setSavedConsent(mode) {
    var normalized = normalizeConsent(mode) || 'denied';
    try { localStorage.setItem(CONSENT_KEY, normalized); } catch (e) {}
    return normalized;
  }

  window.gtag('consent', 'default', {
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    wait_for_update: 500
  });

  var savedConsent = getSavedConsent();
  if (savedConsent) {
    if (savedConsent === 'granted') savedConsent = setSavedConsent('analytics');
    window.gtag('consent', 'update', consentSignals(savedConsent));
  }

  function loadGoogleTag() {
    if (document.querySelector('script[src*="googletagmanager.com/gtag/js?id=' + GA_ID + '"]')) return;
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    var firstScript = document.getElementsByTagName('script')[0];
    if (firstScript && firstScript.parentNode) firstScript.parentNode.insertBefore(script, firstScript);
    else document.head.appendChild(script);
  }

  function canonicalLocation() {
    var canonical = document.querySelector('link[rel="canonical"]');
    var href = canonical && canonical.getAttribute('href');
    return href || window.location.href;
  }

  function pagePathFromUrl(url) {
    try {
      var parsed = new URL(url, window.location.href);
      return parsed.pathname + parsed.search;
    } catch (e) {
      return window.location.pathname + window.location.search;
    }
  }

  function trackPageView(options) {
    options = options || {};
    if (typeof window.gtag !== 'function') return;

    var location = options.location || canonicalLocation();
    var key = location + '|' + (document.title || '');
    if (!options.force && key === TRACKED_URL) return;
    TRACKED_URL = key;

    window.gtag('event', 'page_view', {
      page_title: options.title || document.title || 'Cosmos Week',
      page_location: location,
      page_path: options.path || pagePathFromUrl(location)
    });
  }

  function schedulePageView(force) {
    if (trackingTimer) window.clearTimeout(trackingTimer);
    trackingTimer = window.setTimeout(function () {
      trackingTimer = 0;
      trackPageView({ force: !!force });
    }, 80);
  }

  window.cwTrackPageView = function (options) {
    trackPageView(options || {});
  };

  window.cwUpdateConsent = function (mode, options) {
    var normalized = setSavedConsent(mode);
    window.gtag('consent', 'update', consentSignals(normalized));
    if (normalized === 'analytics' || normalized === 'full') {
      schedulePageView(options && options.force === false ? false : true);
    }
    return normalized;
  };

  window.setCookieConsent = function (mode) {
    window.cwUpdateConsent(mode, { force: true });
    hideCookieBanner();
  };

  loadGoogleTag();
  window.gtag('js', new Date());
  window.gtag('config', GA_ID, {
    anonymize_ip: true,
    send_page_view: false
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { schedulePageView(false); initCookieBanner(); });
  } else {
    schedulePageView(false);
    initCookieBanner();
  }

  function hookHistoryMethod(methodName) {
    var original = history[methodName];
    if (typeof original !== 'function') return;
    history[methodName] = function () {
      var result = original.apply(this, arguments);
      schedulePageView(false);
      return result;
    };
  }

  hookHistoryMethod('pushState');
  hookHistoryMethod('replaceState');
  window.addEventListener('popstate', function () { schedulePageView(false); });

  function detectLanguage() {
    var htmlLang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    if (htmlLang.indexOf('en') === 0 || /^\/en(?:\/|$)/i.test(window.location.pathname)) return 'en';
    return 'pt';
  }

  function bannerCopy() {
    if (detectLanguage() === 'en') {
      return {
        aria: 'Cookie notice',
        title: 'Privacy',
        text: 'We use analytics to measure audience and improve Cosmos Week. You can accept everything, allow analytics only, or decline.',
        policy: 'Privacy policy',
        policyUrl: '/en/privacy/',
        deny: 'Decline',
        analytics: 'Analytics only',
        full: 'Accept all'
      };
    }
    return {
      aria: 'Aviso de cookies',
      title: 'Privacidade',
      text: 'Usamos analytics para medir audiência e melhorar o Cosmos Week. Você pode aceitar tudo, liberar só analytics ou recusar.',
      policy: 'Política de privacidade',
      policyUrl: '/politica-de-privacidade.html',
      deny: 'Recusar',
      analytics: 'Só analytics',
      full: 'Aceitar tudo'
    };
  }

  function ensureBannerStyles() {
    if (document.getElementById('cw-analytics-cookie-style')) return;
    var style = document.createElement('style');
    style.id = 'cw-analytics-cookie-style';
    style.textContent = [
      '.cookie-banner{position:fixed;left:50%;bottom:18px;z-index:2147483000;width:min(960px,calc(100% - 28px));transform:translate(-50%,120%);opacity:0;pointer-events:none;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px;border:1px solid rgba(13,58,117,.18);border-radius:24px;background:rgba(255,255,255,.94);box-shadow:0 22px 80px rgba(15,23,42,.18);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);transition:transform .25s ease,opacity .25s ease;font:500 14px/1.45 Arial,system-ui,sans-serif;color:#172033}',
      '.cookie-banner.show{transform:translate(-50%,0);opacity:1;pointer-events:auto}',
      '.cookie-copy{min-width:0}.cookie-title{font-weight:800;color:#0d3a75;margin-bottom:4px}.cookie-text{color:#475569}.cookie-text a{color:#1451a0;text-decoration:underline;text-underline-offset:3px}',
      '.cookie-actions{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end}.cookie-actions button,.cookie-banner button{appearance:none;border:1px solid rgba(13,58,117,.18);border-radius:999px;padding:10px 13px;background:#fff;color:#0d3a75;font:800 12px/1 Arial,system-ui,sans-serif;cursor:pointer}.cookie-actions .primary-btn,.cookie-banner .primary-btn{background:#1451a0;border-color:#1451a0;color:#fff}.cookie-actions .ghost-btn:hover,.cookie-banner .ghost-btn:hover{border-color:#1451a0}',
      '@media(max-width:720px){.cookie-banner{align-items:stretch;flex-direction:column;bottom:10px;border-radius:20px}.cookie-actions{justify-content:flex-start}.cookie-actions button,.cookie-banner button{flex:1 1 auto}}'
    ].join('');
    document.head.appendChild(style);
  }

  function createCookieBanner() {
    var copy = bannerCopy();
    var banner = document.createElement('div');
    banner.id = 'cookieBanner';
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-label', copy.aria);
    banner.innerHTML = '' +
      '<div class="cookie-copy">' +
        '<div class="cookie-title" id="cookieTitle">' + copy.title + '</div>' +
        '<div class="cookie-text" id="cookieText">' + copy.text + ' <a href="' + copy.policyUrl + '" id="cookiePolicyLink">' + copy.policy + '</a>.</div>' +
      '</div>' +
      '<div class="cookie-actions">' +
        '<button class="ghost-btn" id="cookieDenyBtn" type="button">' + copy.deny + '</button>' +
        '<button class="ghost-btn" id="cookieAnalyticsBtn" type="button">' + copy.analytics + '</button>' +
        '<button class="primary-btn" id="cookieAcceptBtn" type="button">' + copy.full + '</button>' +
      '</div>';
    document.body.appendChild(banner);
    return banner;
  }

  function hideCookieBanner() {
    var banner = document.getElementById('cookieBanner');
    if (banner) banner.classList.remove('show');
  }

  function initCookieBanner() {
    ensureBannerStyles();
    var banner = document.getElementById('cookieBanner') || createCookieBanner();
    var deny = document.getElementById('cookieDenyBtn');
    var analytics = document.getElementById('cookieAnalyticsBtn');
    var full = document.getElementById('cookieAcceptBtn');

    if (deny) deny.onclick = function () { window.setCookieConsent('denied'); };
    if (analytics) analytics.onclick = function () { window.setCookieConsent('analytics'); };
    if (full) full.onclick = function () { window.setCookieConsent('full'); };

    if (getSavedConsent()) {
      banner.classList.remove('show');
    } else {
      window.setTimeout(function () { banner.classList.add('show'); }, 250);
    }
  }
})();
