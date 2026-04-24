(function() {
  'use strict';

  function injectStyles() {
    if (document.getElementById('cw-article-layout-styles')) return;

    var style = document.createElement('style');
    style.id = 'cw-article-layout-styles';
    style.textContent = [
      'html.cw-story-reflow .wrap { max-width: 1460px; }',
      'html.cw-story-reflow .article-lead-block { padding: 0 36px 24px; max-width: 1100px; margin-left: auto; margin-right: auto; text-align: center; }',
      'html.cw-story-reflow .article-lead-block .breadcrumbs { justify-content: center; text-align: center; margin-bottom: 18px; }',
      'html.cw-story-reflow .article-lead-block .hero-head { margin-bottom: 0; justify-items: center; text-align: center; }',
      'html.cw-story-reflow .article-lead-block h1, html.cw-story-reflow .article-lead-block .dek, html.cw-story-reflow .article-lead-block .editorial-strap, html.cw-story-reflow .article-lead-block .kicker-row { margin-left: auto; margin-right: auto; justify-content: center; }',
      'html.cw-story-reflow .article-lead-block h1 { max-width: 900px; font-weight: 900; font-size: clamp(2rem, 4.8vw, 3.35rem); line-height: 1.08; letter-spacing: -0.025em; text-align: center; text-wrap: balance; hyphens: auto; -webkit-hyphens: auto; overflow-wrap: anywhere; }',
      'html.cw-story-reflow .article-lead-block .dek { max-width: 68ch; text-align: center; }',
      'html.cw-story-reflow .hero { max-width: 1100px; margin: 0 auto; display: block; }',
      'html.cw-story-reflow .article-lead-block .top-story-tools { max-width: 720px; margin: 14px auto 0; padding: 8px; border-radius: 999px; background: rgba(251,250,247,.92); border: 1px solid rgba(221,214,203,.95); box-shadow: 0 8px 22px rgba(13,18,25,.04); text-align: center; }',
      'html.cw-story-reflow .article-lead-block .top-story-tools h2 { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }',
      'html.cw-story-reflow .article-lead-block .top-story-tools .story-tools { display: flex; flex-wrap: wrap; gap: 7px; justify-content: center; align-items: center; }',
      'html.cw-story-reflow .article-lead-block .top-story-tools .story-tool-btn, html.cw-story-reflow .article-lead-block .top-story-tools .story-link-btn { width: auto; min-width: 0; min-height: 34px; padding: 8px 12px; border-radius: 999px; font: 800 12px/1.2 Arial, sans-serif; letter-spacing: .035em; text-transform: uppercase; box-shadow: none; }',
      'html.cw-story-reflow .article-lead-block .top-story-tools .story-tool-status { text-align: center; margin-top: 6px; min-height: 14px; font: 700 11px/1.2 Arial, sans-serif; }',
      'html.cw-story-reflow .article-lead-block .top-story-tools .story-tool-btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }',
      'html.cw-story-reflow .article-lead-block .top-story-tools .story-link-btn { color: var(--accent-dark); background: #fff; }',
      'html.cw-story-reflow .top { max-width: 1100px; margin: 0 auto 16px; padding: 8px 10px; border: 1px solid rgba(221,214,203,.9); border-radius: 22px; background: rgba(255,255,255,.78); box-shadow: 0 8px 24px rgba(13,18,25,.035); }',
      'html.cw-story-reflow .top .brand { font-size: 12px; letter-spacing: .16em; }',
      'html.cw-story-reflow .top .utility-links { gap: 7px; align-items: center; }',
      'html.cw-story-reflow .top .pill-link { min-height: 32px; padding: 7px 11px; border-radius: 999px; background: #fff; border-color: rgba(221,214,203,.95); color: var(--accent-dark); font: 800 11px/1.2 Arial, sans-serif; letter-spacing: .075em; text-transform: uppercase; box-shadow: 0 3px 12px rgba(13,18,25,.035); }',

      'html.cw-story-reflow .content { padding-top: 26px; }',
      'html.cw-story-reflow article.card > .content:not(.article-lead-block) > .breadcrumbs, html.cw-story-reflow article.card > .content:not(.article-lead-block) > .hero-head { display: none !important; }',
      'html.cw-story-reflow .article-lead-block .hero-head { display: grid !important; visibility: visible !important; opacity: 1 !important; }',
      'html.cw-story-reflow .article-lead-block h1 { display: block !important; visibility: visible !important; opacity: 1 !important; margin-top: 0; }',
      'html.cw-story-reflow .article-lead-block .dek { display: block !important; visibility: visible !important; opacity: 1 !important; }',
      'html.cw-story-reflow .article-lead-block .editorial-strap { display: inline-flex !important; visibility: visible !important; opacity: 1 !important; }',
      'html.cw-story-reflow .article-grid { display: block; }',

      'html.cw-story-reflow .main-story { min-width: 0; max-width: 1100px; margin-left: auto; margin-right: auto; display: flex; flex-direction: column; align-items: center; }',
      'html.cw-story-reflow .main-story > * { width: 100%; }',
      'html.cw-story-reflow .main-story .body-label, html.cw-story-reflow .main-story .source-link, html.cw-story-reflow .main-story .article-footer-note { margin-left: auto; margin-right: auto; text-align: center; }',
      'html.cw-story-reflow .main-story .body-label { letter-spacing: .14em; margin-bottom: 18px; }',

      'html.cw-story-reflow .main-story .body {',
      '  max-width: 68ch;',
      '  margin-left: auto;',
      '  margin-right: auto;',
      '  font-size: clamp(1.06rem, 0.98rem + 0.22vw, 1.14rem);',
      '  line-height: 1.9;',
      '  letter-spacing: 0.003em;',
      '  word-spacing: 0.01em;',
      '  text-rendering: optimizeLegibility;',
      '  -webkit-font-smoothing: antialiased;',
      '}',
      'html.cw-story-reflow .main-story .body, html.cw-story-reflow .main-story .body > * { text-align: inherit; }',
      'html.cw-story-reflow .main-story .body p {',
      '  text-align: justify;',
      '  text-justify: inter-word;',
      '  hyphens: auto;',
      '  -webkit-hyphens: auto;',
      '  -ms-hyphens: auto;',
      '  margin: 0 0 1.35em;',
      '  text-indent: 1.75em;',
      '  line-height: 1.9;',
      '}',
      'html.cw-story-reflow .main-story .body p:first-of-type { text-indent: 0; }',
      'html.cw-story-reflow .main-story .body p:first-of-type::first-letter {',
      '  float: left;',
      '  font-size: 4.6em;',
      '  line-height: 0.82;',
      '  font-weight: 700;',
      '  margin: 0.05em 0.12em 0 0;',
      '  padding: 0;',
      '}',
      'html.cw-story-reflow .main-story .body h2, html.cw-story-reflow .main-story .body h3, html.cw-story-reflow .main-story .body h4 {',
      '  text-align: left;',
      '  margin: 2.2em 0 0.9em;',
      '  line-height: 1.25;',
      '}',
      'html.cw-story-reflow .main-story .body figcaption {',
      '  text-align: center;',
      '  margin: 12px auto 0;',
      '  max-width: 60ch;',
      '  line-height: 1.55;',
      '}',
      'html.cw-story-reflow .main-story .body blockquote {',
      '  border-left: 3px solid #cfdcf2;',
      '  border-top: 0;',
      '  padding: 0 0 0 18px;',
      '  margin: 1.8em 0;',
      '  text-align: justify;',
      '  text-justify: inter-word;',
      '}',
      'html.cw-story-reflow .main-story .body ul, html.cw-story-reflow .main-story .body ol {',
      '  display: block;',
      '  text-align: left;',
      '  margin: 1.1em 0 1.4em;',
      '  padding-left: 1.45em;',
      '  max-width: 68ch;',
      '}',
      'html.cw-story-reflow .main-story .body li {',
      '  margin: 0 0 0.6em;',
      '  line-height: 1.8;',
      '}',

      'html.cw-story-reflow .main-story .highlights {',
      '  max-width: 68ch;',
      '  margin-left: auto;',
      '  margin-right: auto;',
      '  text-align: left;',
      '}',
      'html.cw-story-reflow .main-story .highlights h2 { text-align: center; }',
      'html.cw-story-reflow .main-story .highlights p { text-align: justify; text-justify: inter-word; hyphens: auto; line-height: 1.8; }',
      'html.cw-story-reflow .main-story .highlights ul, html.cw-story-reflow .main-story .highlights ol { display: block; text-align: left; margin: 1em 0 1.2em; padding-left: 1.4em; }',
      'html.cw-story-reflow .main-story .footer-links { justify-content: center; display: flex; flex-wrap: wrap; gap: 12px; }',
      'html.cw-story-reflow .main-story .preview-gallery, html.cw-story-reflow .main-story .preview-inline-figure, html.cw-story-reflow .main-story .preview-video { margin-left: auto; margin-right: auto; }',
      'html.cw-story-reflow .body .preview-gallery { margin: 32px auto 34px; max-width: 100%; }',
      'html.cw-story-reflow .body .preview-inline-figure, html.cw-story-reflow .body .preview-video { margin: 0 auto; }',
      'html.cw-story-reflow .body .preview-inline-figure img { width: 100%; height: auto; display: block; border-radius: 14px; }',
      'html.cw-story-reflow .body .preview-video-frame { max-width: 100%; }',

      'html.cw-story-reflow .sidebar { position: static; top: auto; margin-top: 22px; max-width: 1100px; margin-left: auto; margin-right: auto; text-align: left; }',
      'html.cw-story-reflow .sidebar .editorial-panel, html.cw-story-reflow .sidebar .context-box, html.cw-story-reflow .sidebar .story-tools, html.cw-story-reflow .sidebar .meta-grid, html.cw-story-reflow .sidebar .related-links { text-align: left; }',
      'html.cw-story-reflow .sidebar ul, html.cw-story-reflow .sidebar ol { display: block; text-align: left; margin-left: 0; margin-right: 0; padding-left: 1.4em; }',

      'html.cw-story-reflow .after-story-stack { display: grid; gap: 18px; margin-top: 28px; max-width: 1100px; margin-left: auto; margin-right: auto; justify-items: stretch; }',
      'html.cw-story-reflow .after-story-stack > * { width: 100%; }',
      'html.cw-story-reflow .after-story-stack .meta-grid { margin: 0; }',
      'html.cw-story-reflow .after-story-stack > .source-link, html.cw-story-reflow .after-story-stack > .footer-links, html.cw-story-reflow .after-story-stack > .article-footer-note { max-width: 68ch; margin-left: auto; margin-right: auto; }',
      'html.cw-story-reflow .after-story-stack .meta-chip { text-align: center; }',

      'html.cw-story-reflow .article-trust-footer { max-width: 1100px; margin: 30px auto 0; padding: 20px 22px; border-radius: 18px; border: 1px solid #ddd6cb; background: #fbfaf7; text-align: center; box-shadow: 0 10px 28px rgba(13,18,25,.04); }',
      'html.cw-story-reflow .article-trust-footer strong { display: block; margin-bottom: 10px; font: 800 11px/1.25 Arial, sans-serif; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }',
      'html.cw-story-reflow .article-trust-footer nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 9px; }',
      'html.cw-story-reflow .article-trust-footer a { display: inline-flex; align-items: center; justify-content: center; min-height: 38px; padding: 9px 13px; border-radius: 999px; border: 1px solid #d7d0c5; color: #1451a0; background: #fff; font: 700 12px/1.2 Arial, sans-serif; text-decoration: none; }',
      'html.cw-story-reflow .article-trust-footer a:hover { border-color: #1451a0; }',

      '@media (max-width: 720px) {',
      '  html.cw-story-reflow .article-lead-block { padding-left: 18px; padding-right: 18px; padding-bottom: 18px; }',
      '  html.cw-story-reflow .article-lead-block h1 { font-size: clamp(1.48rem, 7.4vw, 2.08rem); line-height: 1.13; max-width: 100%; text-align: center; letter-spacing: -0.018em; }',
      '  html.cw-story-reflow .article-lead-block .top-story-tools { margin-top: 12px; padding: 8px; border-radius: 22px; }',
      '  html.cw-story-reflow .article-lead-block .top-story-tools .story-tools { display: flex; flex-wrap: wrap; gap: 7px; }',
      '  html.cw-story-reflow .article-lead-block .top-story-tools .story-tool-btn, html.cw-story-reflow .article-lead-block .top-story-tools .story-link-btn { flex: 1 1 calc(33.333% - 7px); width: auto; min-width: 92px; min-height: 34px; padding: 8px 9px; font-size: 11px; letter-spacing: .025em; }',
      '  html.cw-story-reflow .top { margin-bottom: 14px; padding: 8px; border-radius: 20px; align-items: center; }',
      '  html.cw-story-reflow .top .brand { width: 100%; text-align: center; font-size: 11px; }',
      '  html.cw-story-reflow .top .utility-links { width: 100%; justify-content: center; }',
      '  html.cw-story-reflow .top .pill-link { min-height: 31px; padding: 7px 10px; font-size: 10.5px; }',
      '  html.cw-story-reflow .main-story .body, html.cw-story-reflow .main-story .highlights { max-width: min(68ch, 100%); }',
      '  html.cw-story-reflow .main-story .body { font-size: 1rem; line-height: 1.78; }',
      '  html.cw-story-reflow .main-story .body p { text-indent: 0; margin-bottom: 1.15em; }',
      '  html.cw-story-reflow .main-story .body p:first-of-type::first-letter { float: none; font-size: inherit; line-height: inherit; font-weight: inherit; margin: 0; }',
      '}'
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


  function compactArticleActions(section) {
    if (!section) return;

    var lang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    var isEnglish = lang.indexOf('en') === 0 || location.pathname.indexOf('/en/') === 0;
    var copyBtn = section.querySelector('#copyArticleLink');
    var shareBtn = section.querySelector('#shareArticleBtn');
    var sourceBtn = section.querySelector('.story-link-btn');

    if (copyBtn) copyBtn.textContent = isEnglish ? 'Copy link' : 'Copiar link';
    if (shareBtn) shareBtn.textContent = isEnglish ? 'Share' : 'Compartilhar';
    if (sourceBtn) sourceBtn.textContent = isEnglish ? 'Source' : 'Fonte';
  }

  function refineTopUtilityLinks() {
    var links = document.querySelectorAll('.top .pill-link');
    links.forEach(function(link) {
      var text = (link.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
      if (text.indexOf('voltar ao cosmos week') !== -1 || text.indexOf('back to cosmos week') !== -1) {
        link.textContent = '← Cosmos Week';
      } else if (text.indexOf('read in english') !== -1) {
        link.textContent = 'English version';
      } else if (text.indexOf('read in portuguese') !== -1) {
        link.textContent = 'Portuguese version';
      }
    });
  }

  function addArticleTrustFooter(article, content) {
    if (!article || article.querySelector('.article-trust-footer')) return;

    var lang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    var isEnglish = lang.indexOf('en') === 0 || location.pathname.indexOf('/en/') === 0;

    var labels = isEnglish
      ? {
          title: 'Editorial transparency',
          about: 'About',
          standards: 'Standards',
          privacy: 'Privacy',
          terms: 'Terms',
          contact: 'Contact'
        }
      : {
          title: 'Transparência editorial',
          about: 'Sobre',
          standards: 'Padrões editoriais',
          privacy: 'Privacidade',
          terms: 'Termos',
          contact: 'Contato'
        };

    var links = isEnglish
      ? [
          ['/en/about/', labels.about],
          ['/en/standards/', labels.standards],
          ['/en/privacy/', labels.privacy],
          ['/en/terms/', labels.terms],
          ['/en/contact/', labels.contact]
        ]
      : [
          ['/sobre/', labels.about],
          ['/padroes/', labels.standards],
          ['/politica-de-privacidade.html', labels.privacy],
          ['/termos-de-uso.html', labels.terms],
          ['/contato/', labels.contact]
        ];

    var footer = document.createElement('footer');
    footer.className = 'article-trust-footer';
    footer.setAttribute('aria-label', labels.title);

    var strong = document.createElement('strong');
    strong.textContent = labels.title;
    footer.appendChild(strong);

    var nav = document.createElement('nav');
    links.forEach(function(link) {
      var a = document.createElement('a');
      a.href = link[0];
      a.textContent = link[1];
      nav.appendChild(a);
    });
    footer.appendChild(nav);

    (content || article).appendChild(footer);
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

    var leadBlock = null;
    if (breadcrumbs || heroHead) {
      leadBlock = document.createElement('div');
      leadBlock.className = 'content article-lead-block';
      if (breadcrumbs) leadBlock.appendChild(breadcrumbs);
      if (heroHead) leadBlock.appendChild(heroHead);
      article.insertBefore(leadBlock, hero);
    }

    var toolsPanel = sidebar ? sidebar.querySelector('.story-tools') : null;
    var toolsSection = toolsPanel ? toolsPanel.closest('.editorial-panel') : null;
    if (toolsSection && leadBlock) {
      toolsSection.classList.add('top-story-tools');
      compactArticleActions(toolsSection);
      leadBlock.appendChild(toolsSection);
    }

    refineTopUtilityLinks();

    if (body) {
      var inlineMedia = previewGallery || buildInlineHeroFigure(hero);
      if (inlineMedia) insertGalleryIntoBody(body, inlineMedia);
    }

    if (body) {
      if (bodyLabel && mainStory.firstElementChild !== bodyLabel) {
        mainStory.insertBefore(bodyLabel, mainStory.firstElementChild || null);
      }
      if (mainStory.children.length > 1 && mainStory.children[1] !== body) {
        bodyLabel
          ? mainStory.insertBefore(body, bodyLabel.nextSibling)
          : mainStory.insertBefore(body, mainStory.firstElementChild || null);
      }
    }

    var afterStory = document.createElement('div');
    afterStory.className = 'after-story-stack';
    moveAll([highlights, sourceLink, metaGrid, footerLinks, footerNote], afterStory);

    if (afterStory.children.length) {
      mainStory.appendChild(afterStory);
    }

    if (sidebar && sidebar.parentElement !== content) {
      content.appendChild(sidebar);
    }

    addArticleTrustFooter(article, content);

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
