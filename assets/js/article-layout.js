(function() {
  'use strict';

  function injectStyles() {
    if (document.getElementById('cw-article-layout-styles')) return;

    var style = document.createElement('style');
    style.id = 'cw-article-layout-styles';
    style.textContent = [
      'html.cw-story-reflow {',
      '  --cw-sky: #dff3ff;',
      '  --cw-sky-2: #eef9ff;',
      '  --cw-ice: rgba(255,255,255,.74);',
      '  --cw-ice-strong: rgba(255,255,255,.88);',
      '  --cw-line: rgba(120,160,205,.24);',
      '  --cw-ink: #111827;',
      '  --cw-muted: #64748b;',
      '  --cw-blue: #1d6ed8;',
      '  --cw-blue-dark: #0d3a75;',
      '}',

      'html.cw-story-reflow body {',
      '  background:',
      '    radial-gradient(circle at 12% -10%, rgba(191,232,255,.82) 0, rgba(191,232,255,0) 34%),',
      '    radial-gradient(circle at 92% 12%, rgba(223,243,255,.92) 0, rgba(223,243,255,0) 30%),',
      '    linear-gradient(180deg, #f7fcff 0%, #f8fafc 48%, #f4f7fb 100%) !important;',
      '  color: var(--cw-ink);',
      '}',
      'html.cw-story-reflow body::before {',
      '  content: "";',
      '  position: fixed;',
      '  inset: 0;',
      '  pointer-events: none;',
      '  z-index: -1;',
      '  background-image:',
      '    linear-gradient(rgba(13,58,117,.035) 1px, transparent 1px),',
      '    linear-gradient(90deg, rgba(13,58,117,.026) 1px, transparent 1px);',
      '  background-size: 44px 44px;',
      '  mask-image: linear-gradient(to bottom, rgba(0,0,0,.82), rgba(0,0,0,.16) 58%, transparent 100%);',
      '}',

      'html.cw-story-reflow .wrap { max-width: 1180px; padding-left: clamp(18px, 4vw, 38px); padding-right: clamp(18px, 4vw, 38px); }',
      'html.cw-story-reflow main.wrap { padding-top: 22px; padding-bottom: 96px; }',

      'html.cw-story-reflow .top {',
      '  max-width: 1040px;',
      '  margin: 0 auto 18px;',
      '  padding: 9px 10px;',
      '  display: flex;',
      '  align-items: center;',
      '  justify-content: space-between;',
      '  gap: 12px;',
      '  border: 1px solid rgba(140,178,220,.24);',
      '  border-radius: 999px;',
      '  background: rgba(255,255,255,.66);',
      '  box-shadow: 0 18px 60px rgba(15,23,42,.06);',
      '  backdrop-filter: blur(22px) saturate(155%);',
      '  -webkit-backdrop-filter: blur(22px) saturate(155%);',
      '}',
      'html.cw-story-reflow .top .brand {',
      '  padding-left: 12px;',
      '  color: #0f2748;',
      '  font: 850 11px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .18em;',
      '  text-transform: uppercase;',
      '}',
      'html.cw-story-reflow .top .utility-links { display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-end; gap: 7px; }',
      'html.cw-story-reflow .top .pill-link {',
      '  min-height: 32px;',
      '  display: inline-flex;',
      '  align-items: center;',
      '  justify-content: center;',
      '  padding: 7px 12px;',
      '  border-radius: 999px;',
      '  border: 1px solid rgba(140,178,220,.28);',
      '  background: rgba(255,255,255,.62);',
      '  color: var(--cw-blue-dark);',
      '  font: 750 11px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .055em;',
      '  text-transform: uppercase;',
      '  text-decoration: none;',
      '  box-shadow: 0 8px 24px rgba(15,23,42,.045);',
      '}',
      'html.cw-story-reflow .top .pill-link:hover { background: rgba(255,255,255,.88); border-color: rgba(29,110,216,.32); transform: translateY(-1px); }',

      'html.cw-story-reflow article.card {',
      '  overflow: visible;',
      '  border: 1px solid rgba(140,178,220,.24);',
      '  border-radius: 34px;',
      '  background: linear-gradient(180deg, rgba(255,255,255,.72), rgba(255,255,255,.50));',
      '  box-shadow: 0 30px 110px rgba(15,23,42,.09);',
      '  backdrop-filter: blur(28px) saturate(150%);',
      '  -webkit-backdrop-filter: blur(28px) saturate(150%);',
      '}',
      'html.cw-story-reflow article.card::before {',
      '  content: "";',
      '  position: absolute;',
      '  inset: 0;',
      '  border-radius: inherit;',
      '  pointer-events: none;',
      '  background:',
      '    radial-gradient(circle at 50% 0%, rgba(223,243,255,.74), rgba(223,243,255,0) 42%),',
      '    linear-gradient(180deg, rgba(255,255,255,.52), rgba(255,255,255,0));',
      '}',
      'html.cw-story-reflow article.card > * { position: relative; z-index: 1; }',

      'html.cw-story-reflow .article-lead-block {',
      '  padding: clamp(24px, 5vw, 58px) clamp(20px, 5vw, 72px) clamp(18px, 3vw, 30px);',
      '  max-width: 1040px;',
      '  margin-left: auto;',
      '  margin-right: auto;',
      '}',
      'html.cw-story-reflow .article-lead-block .breadcrumbs {',
      '  display: flex;',
      '  align-items: center;',
      '  justify-content: flex-start;',
      '  gap: 8px;',
      '  margin: 0 0 clamp(20px, 3.2vw, 34px);',
      '  color: rgba(71,85,105,.84);',
      '  font: 760 12px/1.2 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .04em;',
      '}',
      'html.cw-story-reflow .article-lead-block .breadcrumbs a { color: rgba(13,58,117,.86); text-decoration: none; }',
      'html.cw-story-reflow .article-lead-block .breadcrumbs a:hover { color: var(--cw-blue); text-decoration: underline; text-underline-offset: 4px; }',
      'html.cw-story-reflow .article-lead-block .breadcrumbs .sep { color: rgba(100,116,139,.50); }',

      'html.cw-story-reflow .article-lead-block .hero-head {',
      '  display: grid !important;',
      '  justify-items: start;',
      '  text-align: left;',
      '  gap: 0;',
      '  max-width: 890px;',
      '  margin: 0;',
      '}',
      'html.cw-story-reflow .article-lead-block h1 {',
      '  display: block !important;',
      '  max-width: 880px;',
      '  margin: 0;',
      '  color: #0f172a;',
      '  font-family: var(--serif, Georgia, serif);',
      '  font-weight: 760;',
      '  font-size: clamp(2.25rem, 5.4vw, 4.72rem);',
      '  line-height: .98;',
      '  letter-spacing: -.055em;',
      '  text-wrap: balance;',
      '  overflow-wrap: anywhere;',
      '  hyphens: auto;',
      '  -webkit-hyphens: auto;',
      '}',
      'html.cw-story-reflow .article-lead-block .dek {',
      '  display: block !important;',
      '  max-width: 760px;',
      '  margin: clamp(16px, 2.4vw, 24px) 0 0;',
      '  color: #475569;',
      '  font: 470 clamp(1.06rem, 1.55vw, 1.36rem)/1.62 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: -.012em;',
      '}',
      'html.cw-story-reflow .article-lead-block .editorial-strap { display: none !important; }',

      'html.cw-story-reflow .cw-article-byline {',
      '  display: flex;',
      '  flex-wrap: wrap;',
      '  align-items: center;',
      '  gap: 8px 10px;',
      '  margin: clamp(17px, 2.4vw, 26px) 0 0;',
      '  color: #516174;',
      '  font: 710 12px/1.25 var(--sans, Inter, system-ui, sans-serif);',
      '}',
      'html.cw-story-reflow .cw-article-byline span { display: inline-flex; align-items: center; gap: 8px; }',
      'html.cw-story-reflow .cw-article-byline span + span::before { content: ""; width: 4px; height: 4px; border-radius: 999px; background: rgba(29,110,216,.36); }',
      'html.cw-story-reflow .cw-topic-row {',
      '  display: flex !important;',
      '  flex-wrap: wrap;',
      '  justify-content: flex-start;',
      '  gap: 8px;',
      '  margin: 14px 0 0;',
      '}',
      'html.cw-story-reflow .cw-topic-row span {',
      '  display: inline-flex;',
      '  align-items: center;',
      '  min-height: 30px;',
      '  padding: 7px 11px;',
      '  border-radius: 999px;',
      '  border: 1px solid rgba(125,177,224,.26);',
      '  background: rgba(237,249,255,.70);',
      '  color: #255071;',
      '  font: 760 11px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .04em;',
      '  text-transform: none;',
      '}',

      'html.cw-story-reflow article.card > img.hero {',
      '  width: calc(100% - clamp(30px, 6vw, 76px));',
      '  max-width: 1040px;',
      '  max-height: min(680px, 62vh);',
      '  object-fit: cover;',
      '  margin: 0 auto clamp(22px, 4vw, 42px);',
      '  border-radius: clamp(22px, 4vw, 32px);',
      '  border: 1px solid rgba(255,255,255,.72);',
      '  box-shadow: 0 28px 80px rgba(15,23,42,.16);',
      '  background: rgba(255,255,255,.5);',
      '}',

      'html.cw-story-reflow .content { padding: 0 clamp(18px, 4vw, 48px) clamp(34px, 5vw, 64px); }',
      'html.cw-story-reflow article.card > .content:not(.article-lead-block) > .breadcrumbs, html.cw-story-reflow article.card > .content:not(.article-lead-block) > .hero-head { display: none !important; }',
      'html.cw-story-reflow article.card > .content:not(.article-lead-block) > .meta-grid { display: none !important; }',
      'html.cw-story-reflow .article-grid { display: block; }',

      'html.cw-story-reflow .main-story {',
      '  width: 100%;',
      '  max-width: 890px;',
      '  margin: 0 auto;',
      '  display: flex;',
      '  flex-direction: column;',
      '  align-items: stretch;',
      '}',
      'html.cw-story-reflow .main-story .body-label {',
      '  width: fit-content;',
      '  margin: 0 auto 18px;',
      '  padding: 8px 12px;',
      '  text-align: center;',
      '  border-radius: 999px;',
      '  border: 1px solid rgba(125,177,224,.24);',
      '  background: rgba(255,255,255,.62);',
      '  color: #557085;',
      '  font: 820 11px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .13em;',
      '  text-transform: uppercase;',
      '}',
      'html.cw-story-reflow .main-story .body {',
      '  max-width: 68ch;',
      '  margin: 0 auto;',
      '  color: #1f2937;',
      '  font: 430 clamp(1.075rem, 1rem + .22vw, 1.17rem)/1.92 var(--body, Lora, Georgia, serif);',
      '  letter-spacing: -.002em;',
      '  word-spacing: .012em;',
      '  text-rendering: optimizeLegibility;',
      '  -webkit-font-smoothing: antialiased;',
      '}',
      'html.cw-story-reflow .main-story .body p {',
      '  margin: 0 0 1.35em;',
      '  text-align: justify;',
      '  text-justify: inter-word;',
      '  hyphens: auto;',
      '  -webkit-hyphens: auto;',
      '  -ms-hyphens: auto;',
      '}',
      'html.cw-story-reflow .main-story .body p:first-of-type { text-indent: 0; }',
      'html.cw-story-reflow .main-story .body p:first-of-type::first-letter {',
      '  float: left;',
      '  font-family: var(--serif, Georgia, serif);',
      '  font-size: 4.7em;',
      '  line-height: .78;',
      '  font-weight: 760;',
      '  margin: .06em .13em 0 0;',
      '  color: #0f2748;',
      '}',
      'html.cw-story-reflow .main-story .body h2, html.cw-story-reflow .main-story .body h3, html.cw-story-reflow .main-story .body h4 {',
      '  margin: 2.25em 0 .85em;',
      '  color: #0f172a;',
      '  font-family: var(--serif, Georgia, serif);',
      '  line-height: 1.18;',
      '  letter-spacing: -.025em;',
      '  text-align: left;',
      '}',
      'html.cw-story-reflow .main-story .body a { color: var(--cw-blue-dark); text-decoration-thickness: 1px; text-underline-offset: 4px; }',
      'html.cw-story-reflow .main-story .body blockquote {',
      '  margin: 1.9em 0;',
      '  padding: 18px 22px;',
      '  border-left: 3px solid rgba(29,110,216,.42);',
      '  border-radius: 18px;',
      '  background: rgba(237,249,255,.58);',
      '  color: #334155;',
      '}',
      'html.cw-story-reflow .main-story .body ul, html.cw-story-reflow .main-story .body ol {',
      '  display: block;',
      '  list-style: revert;',
      '  margin: 1.1em 0 1.45em;',
      '  padding-left: 1.35em;',
      '}',
      'html.cw-story-reflow .main-story .body li { margin-bottom: .58em; line-height: 1.78; }',

      'html.cw-story-reflow .main-story .highlights {',
      '  order: -1;',
      '  max-width: 780px;',
      '  margin: 0 auto clamp(28px, 4vw, 44px);',
      '  padding: clamp(18px, 3vw, 28px);',
      '  border-radius: 28px;',
      '  border: 1px solid rgba(125,177,224,.24);',
      '  background: linear-gradient(135deg, rgba(255,255,255,.76), rgba(235,248,255,.54));',
      '  box-shadow: 0 18px 60px rgba(15,23,42,.07);',
      '  backdrop-filter: blur(22px) saturate(150%);',
      '  -webkit-backdrop-filter: blur(22px) saturate(150%);',
      '}',
      'html.cw-story-reflow .main-story .highlights h2 {',
      '  margin: 0 0 12px;',
      '  color: #0f2748;',
      '  font: 850 13px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .12em;',
      '  text-transform: uppercase;',
      '}',
      'html.cw-story-reflow .main-story .highlights ul { display: grid; gap: 10px; list-style: none; margin: 0; padding: 0; }',
      'html.cw-story-reflow .main-story .highlights li {',
      '  position: relative;',
      '  padding-left: 18px;',
      '  color: #334155;',
      '  font: 500 .98rem/1.58 var(--sans, Inter, system-ui, sans-serif);',
      '}',
      'html.cw-story-reflow .main-story .highlights li::before {',
      '  content: "";',
      '  position: absolute;',
      '  left: 0;',
      '  top: .72em;',
      '  width: 6px;',
      '  height: 6px;',
      '  border-radius: 999px;',
      '  background: rgba(29,110,216,.58);',
      '}',

      'html.cw-story-reflow .body .preview-gallery, html.cw-story-reflow .main-story > .preview-gallery {',
      '  max-width: min(980px, 100%);',
      '  margin: clamp(26px, 5vw, 48px) auto;',
      '  display: grid;',
      '  grid-template-columns: 1fr;',
      '  gap: clamp(18px, 3vw, 28px);',
      '}',
      'html.cw-story-reflow .preview-inline-figure {',
      '  overflow: hidden;',
      '  border-radius: 26px;',
      '  border: 1px solid rgba(255,255,255,.72);',
      '  background: rgba(255,255,255,.66);',
      '  box-shadow: 0 22px 70px rgba(15,23,42,.11);',
      '}',
      'html.cw-story-reflow .preview-inline-figure img { width: 100%; height: auto; display: block; }',
      'html.cw-story-reflow .preview-inline-figure figcaption {',
      '  max-width: 78ch;',
      '  margin: 0;',
      '  padding: 13px 16px 16px;',
      '  color: #667085;',
      '  font: 500 .84rem/1.55 var(--sans, Inter, system-ui, sans-serif);',
      '  text-align: left;',
      '}',
      'html.cw-story-reflow .preview-video { max-width: 880px; margin: 28px auto; }',
      'html.cw-story-reflow .preview-video-frame { overflow: hidden; border-radius: 26px; box-shadow: 0 22px 70px rgba(15,23,42,.11); border: 1px solid rgba(255,255,255,.72); }',

      'html.cw-story-reflow .after-story-stack {',
      '  display: grid;',
      '  gap: 18px;',
      '  max-width: 780px;',
      '  margin: clamp(34px, 6vw, 58px) auto 0;',
      '}',
      'html.cw-story-reflow .after-story-stack > .source-link {',
      '  margin: 0;',
      '  padding: 14px 16px;',
      '  border-radius: 18px;',
      '  border: 1px solid rgba(125,177,224,.22);',
      '  background: rgba(255,255,255,.58);',
      '  color: #536579;',
      '  font: 650 .9rem/1.45 var(--sans, Inter, system-ui, sans-serif);',
      '}',
      'html.cw-story-reflow .after-story-stack > .source-link a { color: var(--cw-blue-dark); font-weight: 760; }',
      'html.cw-story-reflow .after-story-stack > .footer-links { display: none !important; }',
      'html.cw-story-reflow .after-story-stack > .article-footer-note { display: none !important; }',

      'html.cw-story-reflow .sidebar { display: block; position: static; max-width: 780px; margin: 22px auto 0; }',
      'html.cw-story-reflow .sidebar .editorial-panel, html.cw-story-reflow .sidebar .context-box {',
      '  border-radius: 24px;',
      '  border: 1px solid rgba(125,177,224,.22);',
      '  background: rgba(255,255,255,.58);',
      '  box-shadow: 0 16px 55px rgba(15,23,42,.055);',
      '}',
      'html.cw-story-reflow .sidebar .cw-remove-panel { display: none !important; }',
      'html.cw-story-reflow .sidebar:empty { display: none !important; }',

      'html.cw-story-reflow .cw-action-dock {',
      '  position: fixed;',
      '  right: max(18px, calc((100vw - 1180px) / 2 + 18px));',
      '  bottom: 22px;',
      '  z-index: 1000;',
      '  width: auto;',
      '  max-width: calc(100vw - 36px);',
      '  padding: 7px;',
      '  border-radius: 999px;',
      '  border: 1px solid rgba(125,177,224,.28);',
      '  background: rgba(255,255,255,.70);',
      '  box-shadow: 0 18px 60px rgba(15,23,42,.13);',
      '  backdrop-filter: blur(24px) saturate(160%);',
      '  -webkit-backdrop-filter: blur(24px) saturate(160%);',
      '}',
      'html.cw-story-reflow .cw-action-dock h2 { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }',
      'html.cw-story-reflow .cw-action-dock .story-tools { display: flex; align-items: center; justify-content: center; gap: 5px; }',
      'html.cw-story-reflow .cw-action-dock .story-tool-btn, html.cw-story-reflow .cw-action-dock .story-link-btn {',
      '  width: auto;',
      '  min-width: 0;',
      '  min-height: 34px;',
      '  display: inline-flex;',
      '  align-items: center;',
      '  justify-content: center;',
      '  padding: 8px 12px;',
      '  border-radius: 999px;',
      '  border: 1px solid transparent;',
      '  background: transparent;',
      '  color: #35546e;',
      '  box-shadow: none;',
      '  text-decoration: none;',
      '  font: 780 11px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .055em;',
      '  text-transform: uppercase;',
      '}',
      'html.cw-story-reflow .cw-action-dock .story-tool-btn:hover, html.cw-story-reflow .cw-action-dock .story-link-btn:hover { background: rgba(237,249,255,.88); border-color: rgba(125,177,224,.24); transform: translateY(-1px); }',
      'html.cw-story-reflow .cw-action-dock .story-tool-btn.primary { background: rgba(29,110,216,.10); color: var(--cw-blue-dark); border-color: rgba(29,110,216,.16); }',
      'html.cw-story-reflow .cw-action-dock .story-tool-status {',
      '  position: absolute;',
      '  right: 12px;',
      '  bottom: calc(100% + 8px);',
      '  min-height: 0;',
      '  padding: 6px 9px;',
      '  border-radius: 999px;',
      '  background: rgba(15,23,42,.82);',
      '  color: white;',
      '  opacity: 0;',
      '  transform: translateY(4px);',
      '  pointer-events: none;',
      '  transition: opacity .2s ease, transform .2s ease;',
      '  font: 700 11px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  white-space: nowrap;',
      '}',
      'html.cw-story-reflow .cw-action-dock .story-tool-status:not(:empty) { opacity: 1; transform: translateY(0); }',

      'html.cw-story-reflow .article-trust-footer {',
      '  max-width: 780px;',
      '  margin: 26px auto 0;',
      '  padding: 16px;',
      '  border-radius: 22px;',
      '  border: 1px solid rgba(125,177,224,.20);',
      '  background: rgba(255,255,255,.50);',
      '  box-shadow: none;',
      '  text-align: left;',
      '}',
      'html.cw-story-reflow .article-trust-footer strong {',
      '  display: block;',
      '  margin: 0 0 10px;',
      '  color: #667085;',
      '  font: 800 11px/1.15 var(--sans, Inter, system-ui, sans-serif);',
      '  letter-spacing: .11em;',
      '  text-transform: uppercase;',
      '}',
      'html.cw-story-reflow .article-trust-footer nav { display: flex; flex-wrap: wrap; gap: 8px; }',
      'html.cw-story-reflow .article-trust-footer a {',
      '  min-height: 32px;',
      '  display: inline-flex;',
      '  align-items: center;',
      '  justify-content: center;',
      '  padding: 7px 11px;',
      '  border-radius: 999px;',
      '  border: 1px solid rgba(125,177,224,.20);',
      '  background: rgba(255,255,255,.52);',
      '  color: var(--cw-blue-dark);',
      '  font: 700 11px/1.1 var(--sans, Inter, system-ui, sans-serif);',
      '  text-decoration: none;',
      '}',

      '@media (max-width: 820px) {',
      '  html.cw-story-reflow main.wrap { padding-top: 14px; padding-bottom: 116px; }',
      '  html.cw-story-reflow .top { border-radius: 24px; align-items: flex-start; }',
      '  html.cw-story-reflow .top .brand { width: 100%; padding: 2px 0 0; text-align: center; }',
      '  html.cw-story-reflow .top { flex-direction: column; }',
      '  html.cw-story-reflow .top .utility-links { width: 100%; justify-content: center; }',
      '  html.cw-story-reflow article.card { border-radius: 28px; }',
      '  html.cw-story-reflow .article-lead-block { padding: 24px 20px 18px; }',
      '  html.cw-story-reflow .article-lead-block .breadcrumbs { justify-content: center; text-align: center; margin-bottom: 22px; }',
      '  html.cw-story-reflow .article-lead-block .hero-head { justify-items: center; text-align: center; }',
      '  html.cw-story-reflow .article-lead-block h1 { font-size: clamp(2rem, 10vw, 3.05rem); line-height: 1.02; letter-spacing: -.045em; text-align: center; }',
      '  html.cw-story-reflow .article-lead-block .dek { text-align: center; }',
      '  html.cw-story-reflow .cw-article-byline { justify-content: center; text-align: center; }',
      '  html.cw-story-reflow .cw-topic-row { justify-content: center; }',
      '  html.cw-story-reflow article.card > img.hero { width: calc(100% - 28px); border-radius: 22px; max-height: 52vh; }',
      '  html.cw-story-reflow .content { padding-left: 16px; padding-right: 16px; }',
      '  html.cw-story-reflow .main-story .body-label { margin-left: auto; margin-right: auto; }',
      '  html.cw-story-reflow .main-story .body { font-size: 1.02rem; line-height: 1.82; max-width: 100%; }',
      '  html.cw-story-reflow .main-story .body p { text-align: left; text-indent: 0; margin-bottom: 1.16em; }',
      '  html.cw-story-reflow .main-story .body p:first-of-type::first-letter { float: none; font-size: inherit; line-height: inherit; font-weight: inherit; margin: 0; color: inherit; }',
      '  html.cw-story-reflow .main-story .highlights { border-radius: 22px; margin-bottom: 26px; }',
      '  html.cw-story-reflow .preview-inline-figure, html.cw-story-reflow .preview-video-frame { border-radius: 20px; }',
      '  html.cw-story-reflow .cw-action-dock { left: 14px; right: 14px; bottom: 14px; border-radius: 24px; }',
      '  html.cw-story-reflow .cw-action-dock .story-tools { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }',
      '  html.cw-story-reflow .cw-action-dock .story-tool-btn, html.cw-story-reflow .cw-action-dock .story-link-btn { min-height: 38px; padding: 9px 6px; font-size: 10.5px; letter-spacing: .03em; }',
      '  html.cw-story-reflow .cw-action-dock .story-tool-status { right: 50%; transform: translate(50%, 4px); }',
      '  html.cw-story-reflow .cw-action-dock .story-tool-status:not(:empty) { transform: translate(50%, 0); }',
      '}',
      '@media (prefers-reduced-motion: reduce) {',
      '  html.cw-story-reflow * { transition: none !important; scroll-behavior: auto !important; }',
      '}'
    ].join('\n');

    document.head.appendChild(style);
  }

  function injectArticleRefinementStyles() {
    if (document.getElementById('cw-article-refinement-styles')) return;

    var style = document.createElement('style');
    style.id = 'cw-article-refinement-styles';
    style.textContent = [
      'html.cw-story-reflow main.wrap { padding-top: clamp(34px, 4vw, 54px) !important; }',
      'html.cw-story-reflow .article-lead-block { padding-top: clamp(42px, 6vw, 78px) !important; padding-bottom: clamp(22px, 3.4vw, 34px) !important; }',
      'html.cw-story-reflow .article-lead-block .breadcrumbs { justify-content: center !important; text-align: center !important; margin-bottom: clamp(24px, 3.6vw, 40px) !important; }',
      'html.cw-story-reflow .article-lead-block .hero-head { justify-items: center !important; text-align: center !important; max-width: 980px !important; margin: 0 auto !important; }',
      'html.cw-story-reflow .article-lead-block h1 { max-width: 920px !important; margin-left: auto !important; margin-right: auto !important; text-align: center !important; }',
      'html.cw-story-reflow .article-lead-block .dek { max-width: 780px !important; margin-left: auto !important; margin-right: auto !important; text-align: center !important; }',
      'html.cw-story-reflow .cw-article-byline { justify-content: center !important; text-align: center !important; margin-left: auto !important; margin-right: auto !important; }',
      'html.cw-story-reflow .cw-topic-row { justify-content: center !important; }',
      'html.cw-story-reflow article.card > img.hero { display: block !important; margin-left: auto !important; margin-right: auto !important; }',
      'html.cw-story-reflow .main-story .body-label { margin-left: auto !important; margin-right: auto !important; text-align: center !important; }',
      'html.cw-story-reflow .body .preview-gallery, html.cw-story-reflow .main-story > .preview-gallery { justify-items: center !important; }',
      'html.cw-story-reflow .preview-inline-figure { width: 100%; margin-left: auto !important; margin-right: auto !important; }',

      'html.cw-story-reflow .cw-action-dock {',
      '  position: fixed !important;',
      '  left: auto !important;',
      '  right: max(14px, calc((100vw - 1180px) / 2 + 14px)) !important;',
      '  top: 50% !important;',
      '  bottom: auto !important;',
      '  transform: translateY(-50%) !important;',
      '  max-width: 132px !important;',
      '  padding: 6px !important;',
      '  border-radius: 24px !important;',
      '  background: rgba(255,255,255,.62) !important;',
      '  box-shadow: 0 18px 60px rgba(15,23,42,.11) !important;',
      '  opacity: .78;',
      '  transition: opacity .18s ease, transform .18s ease, background .18s ease;',
      '}',
      'html.cw-story-reflow .cw-action-dock:hover, html.cw-story-reflow .cw-action-dock:focus-within { opacity: 1; background: rgba(255,255,255,.80) !important; transform: translateY(-50%) translateX(-2px) !important; }',
      'html.cw-story-reflow .cw-action-dock .story-tools { display: flex !important; flex-direction: column !important; align-items: stretch !important; justify-content: center !important; gap: 6px !important; }',
      'html.cw-story-reflow .cw-action-dock .story-tool-btn, html.cw-story-reflow .cw-action-dock .story-link-btn { width: 100% !important; min-width: 104px !important; min-height: 36px !important; padding: 8px 11px !important; font-size: 10.5px !important; letter-spacing: .045em !important; }',
      'html.cw-story-reflow .cw-action-dock .story-tool-status { right: calc(100% + 8px) !important; bottom: auto !important; top: 50% !important; transform: translateY(-50%) translateX(4px) !important; }',
      'html.cw-story-reflow .cw-action-dock .story-tool-status:not(:empty) { transform: translateY(-50%) translateX(0) !important; }',

      '@media (max-width: 820px) {',
      '  html.cw-story-reflow main.wrap { padding-top: 24px !important; padding-bottom: 96px !important; }',
      '  html.cw-story-reflow .article-lead-block { padding-top: 34px !important; padding-bottom: 20px !important; }',
      '  html.cw-story-reflow article.card > img.hero { display: block !important; margin-left: auto !important; margin-right: auto !important; }',
      '  html.cw-story-reflow .cw-action-dock { left: auto !important; right: 10px !important; top: auto !important; bottom: max(18px, env(safe-area-inset-bottom)) !important; transform: none !important; max-width: 52px !important; border-radius: 18px !important; padding: 5px !important; opacity: .72; }',
      '  html.cw-story-reflow .cw-action-dock:hover, html.cw-story-reflow .cw-action-dock:focus-within { transform: none !important; opacity: .96; }',
      '  html.cw-story-reflow .cw-action-dock .story-tools { display: flex !important; flex-direction: column !important; gap: 5px !important; }',
      '  html.cw-story-reflow .cw-action-dock .story-tool-btn, html.cw-story-reflow .cw-action-dock .story-link-btn { min-width: 42px !important; width: 42px !important; min-height: 38px !important; padding: 0 4px !important; font-size: 0 !important; letter-spacing: 0 !important; }',
      '  html.cw-story-reflow .cw-action-dock .story-tool-btn::before, html.cw-story-reflow .cw-action-dock .story-link-btn::before { content: attr(data-cw-short-label); font: 800 10px/1 var(--sans, Inter, system-ui, sans-serif); letter-spacing: .02em; text-transform: none; }',
      '  html.cw-story-reflow .cw-action-dock .story-tool-status { right: calc(100% + 8px) !important; top: 50% !important; transform: translateY(-50%) translateX(4px) !important; }',
      '  html.cw-story-reflow .cw-action-dock .story-tool-status:not(:empty) { transform: translateY(-50%) translateX(0) !important; }',
      '  html.cw-story-reflow .main-story .body { padding-right: 44px !important; box-sizing: border-box; }',
      '}',
      '@media (max-width: 430px) {',
      '  html.cw-story-reflow .main-story .body { padding-right: 48px !important; }',
      '  html.cw-story-reflow .article-lead-block .breadcrumbs { margin-bottom: 24px !important; }',
      '}'
    ].join(String.fromCharCode(10));

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

  function normalizeText(text) {
    return (text || '').replace(/\s+/g, ' ').trim();
  }

  function getChipValue(metaGrid, labelMatcher) {
    if (!metaGrid) return '';
    var chips = metaGrid.querySelectorAll('.meta-chip');
    for (var i = 0; i < chips.length; i += 1) {
      var span = chips[i].querySelector('span');
      var strong = chips[i].querySelector('strong');
      var label = normalizeText(span ? span.textContent : '').toLowerCase();
      if (labelMatcher(label)) return normalizeText(strong ? strong.textContent : chips[i].textContent);
    }
    return '';
  }

  function makeByline(metaGrid, isEnglish) {
    var author = getChipValue(metaGrid, function(label) {
      return label.indexOf('assinatura') !== -1 || label.indexOf('byline') !== -1 || label.indexOf('editorial') !== -1;
    });
    var published = getChipValue(metaGrid, function(label) {
      return label.indexOf('publicado') !== -1 || label.indexOf('published') !== -1;
    });
    var reading = getChipValue(metaGrid, function(label) {
      return label.indexOf('leitura') !== -1 || label.indexOf('read') !== -1;
    });

    var values = [];
    if (author) values.push(author);
    if (published) values.push(published);
    if (reading) values.push(reading);

    if (!values.length) return null;

    var byline = document.createElement('div');
    byline.className = 'cw-article-byline';
    byline.setAttribute('aria-label', isEnglish ? 'Article information' : 'Informações da matéria');

    values.forEach(function(value) {
      var span = document.createElement('span');
      span.textContent = value;
      byline.appendChild(span);
    });

    return byline;
  }

  function refineHeroHead(heroHead, metaGrid, isEnglish) {
    if (!heroHead) return;

    var h1 = heroHead.querySelector('h1');
    var dek = heroHead.querySelector('.dek');
    var kickerRow = heroHead.querySelector('.kicker-row');
    var editorialStrap = heroHead.querySelector('.editorial-strap');
    var byline = makeByline(metaGrid, isEnglish);

    if (editorialStrap && editorialStrap.parentElement) {
      editorialStrap.parentElement.removeChild(editorialStrap);
    }

    if (h1 && heroHead.firstElementChild !== h1) {
      heroHead.insertBefore(h1, heroHead.firstElementChild || null);
    }

    if (dek && h1 && dek.previousElementSibling !== h1) {
      heroHead.insertBefore(dek, h1.nextSibling);
    }

    if (byline) {
      if (dek) {
        dek.insertAdjacentElement('afterend', byline);
      } else if (h1) {
        h1.insertAdjacentElement('afterend', byline);
      } else {
        heroHead.appendChild(byline);
      }
    }

    if (kickerRow) {
      kickerRow.classList.add('cw-topic-row');
      if (byline) {
        byline.insertAdjacentElement('afterend', kickerRow);
      } else if (dek) {
        dek.insertAdjacentElement('afterend', kickerRow);
      } else if (h1) {
        h1.insertAdjacentElement('afterend', kickerRow);
      }
    }
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
      if (child.tagName === 'P' && !child.classList.contains('art-source')) paragraphs.push(child);
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

    if (copyBtn) {
      copyBtn.textContent = isEnglish ? 'Copy' : 'Copiar';
      copyBtn.setAttribute('data-cw-short-label', 'Link');
      copyBtn.setAttribute('aria-label', isEnglish ? 'Copy article link' : 'Copiar link da notícia');
    }
    if (shareBtn) {
      shareBtn.textContent = isEnglish ? 'Share' : 'Compartilhar';
      shareBtn.setAttribute('data-cw-short-label', isEnglish ? 'Share' : 'Enviar');
      shareBtn.setAttribute('aria-label', isEnglish ? 'Share article' : 'Compartilhar notícia');
    }
    if (sourceBtn) {
      sourceBtn.textContent = isEnglish ? 'Source' : 'Fonte';
      sourceBtn.setAttribute('data-cw-short-label', isEnglish ? 'Source' : 'Fonte');
      sourceBtn.setAttribute('aria-label', isEnglish ? 'Open original source' : 'Abrir fonte original');
    }
  }

  function refineTopUtilityLinks() {
    var links = document.querySelectorAll('.top .pill-link');
    links.forEach(function(link) {
      var text = normalizeText(link.textContent).toLowerCase();
      if (text.indexOf('voltar ao cosmos week') !== -1 || text.indexOf('back to cosmos week') !== -1) {
        link.textContent = '← Cosmos Week';
      } else if (text.indexOf('read in english') !== -1) {
        link.textContent = 'English';
      } else if (text.indexOf('read in portuguese') !== -1) {
        link.textContent = 'Português';
      }
    });
  }

  function panelTitle(panel) {
    var h2 = panel ? panel.querySelector('h2') : null;
    return normalizeText(h2 ? h2.textContent : '').toLowerCase();
  }

  function isClutterPanel(panel) {
    var title = panelTitle(panel);
    return title.indexOf('fonte e enquadramento') !== -1 ||
      title.indexOf('source and framing') !== -1 ||
      title.indexOf('contexto editorial') !== -1 ||
      title.indexOf('editorial context') !== -1 ||
      title.indexOf('padrões editoriais') !== -1 ||
      title.indexOf('editorial standards') !== -1;
  }

  function isRelatedPanel(panel) {
    var title = panelTitle(panel);
    return title.indexOf('leitura relacionada') !== -1 || title.indexOf('related') !== -1;
  }

  function removeEditorialClutter(sidebar) {
    if (!sidebar) return;
    var panels = sidebar.querySelectorAll('.editorial-panel, .context-box');
    panels.forEach(function(panel) {
      if (isClutterPanel(panel)) panel.classList.add('cw-remove-panel');
    });
  }

  function addArticleTrustFooter(article, content) {
    if (!article || article.querySelector('.article-trust-footer')) return;

    var lang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    var isEnglish = lang.indexOf('en') === 0 || location.pathname.indexOf('/en/') === 0;

    var labels = isEnglish
      ? { title: 'Editorial transparency', about: 'About', standards: 'Standards', privacy: 'Privacy', terms: 'Terms', contact: 'Contact' }
      : { title: 'Transparência editorial', about: 'Sobre', standards: 'Padrões', privacy: 'Privacidade', terms: 'Termos', contact: 'Contato' };

    var links = isEnglish
      ? [['/en/about/', labels.about], ['/en/standards/', labels.standards], ['/en/privacy/', labels.privacy], ['/en/terms/', labels.terms], ['/en/contact/', labels.contact]]
      : [['/sobre/', labels.about], ['/padroes/', labels.standards], ['/politica-de-privacidade.html', labels.privacy], ['/termos-de-uso.html', labels.terms], ['/contato/', labels.contact]];

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

    var lang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    var isEnglish = lang.indexOf('en') === 0 || location.pathname.indexOf('/en/') === 0;

    var breadcrumbs = firstDirectChildByClass(content, 'breadcrumbs');
    var heroHead = firstDirectChildByClass(content, 'hero-head');
    var metaGrid = firstDirectChildByClass(content, 'meta-grid');
    var articleGrid = firstDirectChildByClass(content, 'article-grid');
    if (!articleGrid) return;

    var mainStory = articleGrid.querySelector('.main-story');
    var sidebar = articleGrid.querySelector('.sidebar');
    if (!mainStory) return;

    refineHeroHead(heroHead, metaGrid, isEnglish);

    var leadBlock = null;
    if (breadcrumbs || heroHead) {
      leadBlock = document.createElement('div');
      leadBlock.className = 'content article-lead-block';
      if (breadcrumbs) leadBlock.appendChild(breadcrumbs);
      if (heroHead) leadBlock.appendChild(heroHead);
      article.insertBefore(leadBlock, hero);
    }

    if (metaGrid && metaGrid.parentElement) metaGrid.parentElement.removeChild(metaGrid);

    var bodyLabel = mainStory.querySelector('.body-label');
    var body = mainStory.querySelector('.body');
    var highlights = mainStory.querySelector('.highlights');
    if (highlights && highlights.parentElement) {
      highlights.parentElement.removeChild(highlights);
      highlights = null;
    }

    var previewGallery = mainStory.querySelector('.preview-gallery');
    var sourceLink = mainStory.querySelector('.source-link');
    var footerLinks = mainStory.querySelector('.footer-links');
    var footerNote = mainStory.querySelector('.article-footer-note');

    var toolsPanel = sidebar ? sidebar.querySelector('.story-tools') : null;
    var toolsSection = toolsPanel ? toolsPanel.closest('.editorial-panel') : null;
    if (toolsSection) {
      toolsSection.classList.add('cw-action-dock');
      compactArticleActions(toolsSection);
      document.body.appendChild(toolsSection);
    }

    refineTopUtilityLinks();
    removeEditorialClutter(sidebar);

    if (body) {
      var inlineMedia = previewGallery || buildInlineHeroFigure(hero);
      if (inlineMedia) insertGalleryIntoBody(body, inlineMedia);
    }

    if (body) {
      if (bodyLabel && mainStory.firstElementChild !== bodyLabel) {
        mainStory.insertBefore(bodyLabel, mainStory.firstElementChild || null);
      }
      if (bodyLabel && body && body.previousElementSibling !== bodyLabel) {
        bodyLabel.insertAdjacentElement('afterend', body);
      } else if (!bodyLabel && mainStory.firstElementChild !== body) {
        mainStory.insertBefore(body, mainStory.firstElementChild || null);
      }
    }

    var afterStory = document.createElement('div');
    afterStory.className = 'after-story-stack';
    moveAll([sourceLink, footerLinks, footerNote], afterStory);
    if (afterStory.children.length) mainStory.appendChild(afterStory);

    if (sidebar) {
      var relatedPanel = null;
      var panels = sidebar.querySelectorAll('.editorial-panel, .context-box');
      for (var i = 0; i < panels.length; i += 1) {
        if (isRelatedPanel(panels[i])) {
          relatedPanel = panels[i];
          break;
        }
      }
      if (relatedPanel && afterStory.parentElement) afterStory.appendChild(relatedPanel);
      if (sidebar.parentElement !== content) content.appendChild(sidebar);
    }

    addArticleTrustFooter(article, content);

    document.documentElement.classList.add('cw-story-reflow');
    article.dataset.articleFlowApplied = 'true';
  }

  injectStyles();
  injectArticleRefinementStyles();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyLayout, { once: true });
  } else {
    applyLayout();
  }
})();
