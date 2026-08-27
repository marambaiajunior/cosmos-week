(function () {
  'use strict';

  var BOOK = {
    id: '9786526681633',
    name: 'Vórtice Maligno',
    author: 'Humberto Marambaia Junior',
    price: 59.12,
    currency: 'BRL',
    store: 'clube-de-autores'
  };
  var productTracked = false;

  function safeCampaignValue(value) {
    value = String(value || '').trim().slice(0, 100);
    if (!value || /@|https?:\/\//i.test(value) || /(?:\d[\s().+-]*){7,}/.test(value)) return '';
    return value
      .replace(/[^A-Za-z0-9._~-]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 64);
  }

  function campaignContext() {
    var result = {};
    try {
      var query = new URLSearchParams(window.location.search);
      ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(function (key) {
        var value = safeCampaignValue(query.get(key));
        if (value) result[key] = value.slice(0, 100);
      });
    } catch (_) {}
    return result;
  }

  function merge(base, extra) {
    var output = {};
    var key;
    base = base || {};
    extra = extra || {};
    for (key in base) if (Object.prototype.hasOwnProperty.call(base, key)) output[key] = base[key];
    for (key in extra) if (Object.prototype.hasOwnProperty.call(extra, key)) output[key] = extra[key];
    return output;
  }

  function track(name, params) {
    var payload = merge(campaignContext(), params || {});
    try {
      if (
        typeof window.cwHasAnalyticsConsent === 'function' &&
        window.cwHasAnalyticsConsent() &&
        typeof window.gtag === 'function'
      ) window.gtag('event', name, payload);
      document.dispatchEvent(new CustomEvent('cw:book-event', {
        detail: { name: name, params: payload }
      }));
    } catch (_) {}
  }

  function pageType() {
    return document.body ? (document.body.getAttribute('data-cw-page') || 'unknown') : 'unknown';
  }

  function itemPayload() {
    return {
      item_id: BOOK.id,
      item_name: BOOK.name,
      item_brand: BOOK.author,
      item_category: 'Livro',
      item_variant: 'Impresso',
      price: BOOK.price,
      quantity: 1
    };
  }

  function showToast(message) {
    var toast = document.getElementById('guideToast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(function () {
      toast.classList.remove('show');
    }, 3200);
  }

  function copyText(value) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(value);
    }
    return new Promise(function (resolve, reject) {
      try {
        var field = document.createElement('textarea');
        field.value = value;
        field.setAttribute('readonly', '');
        field.style.position = 'fixed';
        field.style.opacity = '0';
        document.body.appendChild(field);
        field.select();
        var copied = document.execCommand('copy');
        document.body.removeChild(field);
        if (copied) resolve();
        else reject(new Error('copy_failed'));
      } catch (error) {
        reject(error);
      }
    });
  }

  function shareGuide(button) {
    var url = button.getAttribute('data-share-url') || window.location.href;
    var data = {
      title: '7 perguntas antes de acreditar ou compartilhar',
      text: 'Checklist gratuito de pensamento crítico do Cosmos Week.',
      url: url
    };
    track('book_guide_share', {
      book_title: BOOK.name,
      share_method: navigator.share ? 'native' : 'clipboard',
      link_url: url,
      page_type: pageType()
    });
    if (navigator.share) {
      navigator.share(data).catch(function (error) {
        if (error && error.name === 'AbortError') return;
        copyText(url).then(function () { showToast('Link copiado.'); });
      });
      return;
    }
    copyText(url)
      .then(function () { showToast('Link copiado.'); })
      .catch(function () { showToast(url); });
  }

  document.addEventListener('click', function (event) {
    var printButton = event.target.closest('[data-print-guide]');
    if (printButton) {
      event.preventDefault();
      track('book_guide_print', {
        book_title: BOOK.name,
        page_type: pageType()
      });
      window.print();
      return;
    }

    var shareButton = event.target.closest('[data-share-guide]');
    if (shareButton) {
      event.preventDefault();
      shareGuide(shareButton);
      return;
    }

    var element = event.target.closest('[data-book-cta]');
    if (!element) return;

    var location = element.getAttribute('data-book-cta') || 'unknown';
    var linkUrl = element.href || '';
    var base = {
      book_id: BOOK.id,
      book_title: BOOK.name,
      cta_location: location,
      link_url: linkUrl,
      page_type: pageType()
    };

    track('book_cta_click', base);

    if (element.hasAttribute('data-book-guide')) {
      track('book_guide_click', merge(base, {
        guide_name: element.getAttribute('data-book-guide') || 'unknown'
      }));
    }

    if (element.hasAttribute('data-book-store') || element.hasAttribute('data-clube-autores')) {
      var store = element.getAttribute('data-book-store') || BOOK.store;
      track('book_store_click', merge(base, {
        store_name: store,
        value: BOOK.price,
        currency: BOOK.currency
      }));
      track('book_clube_autores_click', merge(base, {
        store_name: store,
        value: BOOK.price,
        currency: BOOK.currency
      }));
    }
  });

  function initNavigation() {
    var toggle = document.getElementById('mobileNavToggle');
    var nav = document.getElementById('mainNav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.setAttribute('aria-label', open ? 'Abrir menu' : 'Fechar menu');
      nav.classList.toggle('open', !open);
    });

    nav.addEventListener('click', function (event) {
      if (!event.target.closest('a')) return;
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Abrir menu');
      nav.classList.remove('open');
    });
  }

  function initFaqTracking() {
    var entries = document.querySelectorAll('.book-faq details');
    entries.forEach(function (entry, index) {
      entry.addEventListener('toggle', function () {
        if (!entry.open) return;
        var summary = entry.querySelector('summary');
        track('book_faq_open', {
          book_title: BOOK.name,
          faq_index: index + 1,
          faq_question: summary ? summary.textContent.replace(/\+\s*$/, '').trim().slice(0, 100) : ''
        });
      });
    });
  }

  function trackPageProduct() {
    if (productTracked || typeof window.cwHasAnalyticsConsent !== 'function' || !window.cwHasAnalyticsConsent()) return;
    var type = pageType();
    if (type === 'book') {
      productTracked = true;
      track('view_item', {
        currency: BOOK.currency,
        value: BOOK.price,
        items: [itemPayload()]
      });
      track('book_landing_view', {
        book_id: BOOK.id,
        book_title: BOOK.name,
        value: BOOK.price,
        currency: BOOK.currency
      });
    } else if (type === 'book-guide') {
      productTracked = true;
      track('book_guide_view', {
        book_id: BOOK.id,
        book_title: BOOK.name,
        guide_name: 'checklist'
      });
    }
  }

  function init() {
    initNavigation();
    initFaqTracking();
    document.addEventListener('cw:analytics-consent-granted', trackPageProduct);
    trackPageProduct();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
