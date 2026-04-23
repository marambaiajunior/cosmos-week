(function() {
  'use strict';

  function injectStyles() {
    if (document.getElementById('cw-article-layout-styles')) return;
    var style = document.createElement('style');
    style.id = 'cw-article-layout-styles';
    style.textContent = [
      'html.cw-story-reflow .article-lead-block { padding-bottom: 18px; }',
      'html.cw-story-reflow .article-lead-block .hero-head { margin-bottom: 0; }',
      'html.cw-story-reflow .article-grid { display: block; }',
      'html.cw-story-reflow .main-story { min-width: 0; }',
      'html.cw-story-reflow .sidebar { position: static; top: auto; margin-top: 18px; max-width: 980px; }',
      'html.cw-story-reflow .after-story-stack { display: grid; gap: 18px; margin-top: 28px; max-width: 980px; }',
      'html.cw-story-reflow .after-story-stack .meta-grid { margin: 0; }',
      'html.cw-story-reflow .after-story-stack > .source-link, html.cw-story-reflow .after-story-stack > .footer-links, html.cw-story-reflow .after-story-stack > .article-footer-note { max-width: 70ch; }',
      'html.cw-story-reflow .body .preview-gallery { margin: 28px 0 30px; max-width: 100%; }',
      'html.cw-story-reflow .body .preview-inline-figure, html.cw-story-reflow .body .preview-video { margin: 0; }',
      'html.cw-story-reflow .body .preview-inline-figure img { width: 100%; height: auto; display: block; }',
      'html.cw-story-reflow .body .preview-video-frame { max-width: 100%; }'
    ].join('\n');
    document.head.appendChild(style);
  }

  function firstDirectChildByClass(parent, className) {
    if (!parent) return null;
    for (var i = 0; i < parent.children.length; i += 1) {
      var child = parent.children[i];
      if (child.classList && child.classList.contains(className)) return child;
    }
    return null;
  }

  function buildInlineHeroFigure(hero) {
    if (!hero || !hero.getAttribute('src')) return null;

    var wrapper = document.createElement('section');
    wrapper.className = 'preview-gallery inline-media-break inline-hero-break';

    var figure = document.createElement('figure');
    figure.className = 'preview-inline-figure inline-hero-echo';

    var img = document.createElement('img');
    img.src = hero.getAttribute('src');
    img.alt = hero.getAttribute('alt') || '';
    img.loading = 'lazy';
    img.decoding = 'async';

    var referrerPolicy = hero.getAttribute('referrerpolicy');
    if (referrerPolicy) img.setAttribute('referrerpolicy', referrerPolicy);

    figure.appendChild(img);
    wrapper.appendChild(figure);
    return wrapper;
  }

  function insertGalleryIntoBody(body, gallery) {
    if (!body || !gallery) return;
    if (body.contains(gallery)) return;

    var paragraphs = [];
    for (var i = 0; i < body.children.length; i += 1) {
      var child = body.children[i];
      if (child.tagName === 'P' && !child.classList.contains('art-source')) {
        paragraphs.push(child);
      }
    }

    if (!paragraphs.length) {
      body.appendChild(gallery);
      return;
    }

    var targetIndex;
    if (paragraphs.length >= 6) {
      targetIndex = Math.max(1, Math.floor(paragraphs.length / 2) - 1);
    } else if (paragraphs.length >= 4) {
      targetIndex = 1;
    } else {
      targetIndex = paragraphs.length - 1;
    }

    paragraphs[targetIndex].insertAdjacentElement('afterend', gallery);
  }

  function moveAll(elements, destination) {
    elements.forEach(function(el) {
      if (el) destination.appendChild(el);
    });
  }

  function applyLayout() {
    var article = document.querySelector('article.card[data-article-slug]');
    if (!article || article.dataset.articleFlowApplied === 'true') return;

    var hero = article.querySelector('img.hero');
    var content = article.querySelector('.content');
    if (!hero || !content) return;

    var breadcrumbs = firstDirectChildByClass(content, 'breadcrumbs');
    var heroHead = firstDirectChildByClass(content, 'hero-head');
    var metaGrid = firstDirectChildByClass(content, 'meta-grid');
    var articleGrid = firstDirectChildByClass(content, 'article-grid');
    if (!articleGrid) return;

    var mainStory = articleGrid.querySelector('.main-story');
    var sidebar = articleGrid.querySelector('.sidebar');
    if (!mainStory) return;

    var bodyLabel = mainStory.querySelector('.body-label');
    var body = mainStory.querySelector('.body');
    var highlights = mainStory.querySelector('.highlights');
    var previewGallery = mainStory.querySelector('.preview-gallery');
    var sourceLink = mainStory.querySelector('.source-link');
    var footerLinks = mainStory.querySelector('.footer-links');
    var footerNote = mainStory.querySelector('.article-footer-note');

    if (breadcrumbs || heroHead) {
      var leadBlock = document.createElement('div');
      leadBlock.className = 'content article-lead-block';
      if (breadcrumbs) leadBlock.appendChild(breadcrumbs);
      if (heroHead) leadBlock.appendChild(heroHead);
      article.insertBefore(leadBlock, hero);
    }

    if (body) {
      var inlineMedia = previewGallery || buildInlineHeroFigure(hero);
      if (inlineMedia) insertGalleryIntoBody(body, inlineMedia);
    }

    if (body) {
      if (bodyLabel && mainStory.firstElementChild !== bodyLabel) {
        mainStory.insertBefore(bodyLabel, mainStory.firstElementChild || null);
      }
      if (mainStory.children.length > 1 && mainStory.children[1] !== body) {
        bodyLabel ? mainStory.insertBefore(body, bodyLabel.nextSibling) : mainStory.insertBefore(body, mainStory.firstElementChild || null);
      }
    }

    var afterStory = document.createElement('div');
    afterStory.className = 'after-story-stack';
    moveAll([sourceLink, metaGrid, highlights, footerLinks, footerNote], afterStory);
    if (afterStory.children.length) {
      mainStory.appendChild(afterStory);
    }

    if (sidebar && sidebar.parentElement !== content) {
      content.appendChild(sidebar);
    }

    document.documentElement.classList.add('cw-story-reflow');
    article.dataset.articleFlowApplied = 'true';
  }

  injectStyles();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyLayout, { once: true });
  } else {
    applyLayout();
  }
})();
