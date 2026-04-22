const RUNTIME_BASE_PATH = (() => {
    const path = window.location.pathname || '/';
    if (/\/index(?:\([^\/]+\))?\.html$/i.test(path)) {
      const cleaned = path.replace(/index(?:\([^\/]+\))?\.html$/i, '');
      return cleaned || '/';
    }
    return path || '/';
  })();

  const SITE = {
    canonicalBaseUrl: 'https://www.cosmosweek.com/',
    runtimeBasePath: RUNTIME_BASE_PATH,
    title: 'Cosmos Week',
    homeTitlePt: 'Cosmos Week — Notícias Científicas do universo',
    homeTitleEn: 'Cosmos Week — Science journalism for the universe',
    homeDescriptionPt: 'Portal de Notícias Científicas em português com foco em astronomia, astrofísica, cosmologia e ciência em geral.',
    homeDescriptionEn: 'Science journalism portal focused on astronomy, astrophysics, cosmology and frontier research.'
  };


const PAGE_ROUTE_MAP = {
  pt: { home: '/', archive: '/arquivo/', about: '/sobre/', standards: '/padroes/', search: '/' },
  en: { home: '/en/', archive: '/en/archive/', about: '/en/about/', standards: '/en/standards/', search: '/en/' }
};

const EXTRA_UI = {
  pt: {
    visualLeadTitle: 'Edição em destaque',
    visualLeadKicker: 'A homepage passa a abrir com prioridade visual. Imagens e vídeos puxam a atenção; o aprofundamento fica dentro da matéria.',
    archiveHeroTitle: 'Arquivo de notícias',
    archiveHeroKicker: 'O arquivo deixa de ser depósito cronológico opaco e vira página de descoberta, com entrada por tema e destaques visuais.',
    archiveStatsStories: 'matérias visíveis',
    archiveStatsTopics: 'áreas de cobertura',
    archiveStatsLanguages: 'idiomas',
    archiveLoading: 'Expandindo o arquivo completo...',
    archiveLoaded: 'Arquivo completo carregado.',
    archiveNoItems: 'Nenhuma matéria encontrada nesta área no momento.',
    topicNavTitle: 'Navegue por tema',
    topicNavKicker: 'Escolha a porta de entrada editorial antes de cair no fluxo cronológico.',
    localNavAbout: 'Sobre',
    localNavStandards: 'Padrões',
    localNavArchive: 'Arquivo',
    aboutEyebrow: 'Institucional',
    aboutHeadline: 'Cosmos Week como portal de notícias científicas, não como espelho automático de releases',
    aboutIntro2: 'A arquitetura desta fase reorganiza navegação, arquivo e páginas institucionais para leitura editorial real.',
    aboutCards: [
      { title: 'Missão editorial', body: 'Cobrir ciência com hierarquia de informação, contexto e distinção visível entre anúncio institucional, paper revisado, jornalismo científico e preprint.' },
      { title: 'Arquitetura de descoberta', body: 'A navegação agora privilegia home, arquivo e temas persistentes. O leitor não depende apenas de uma fila cronológica.' },
      { title: 'Estrutura bilíngue', body: 'Português e inglês ganham rotas limpas próprias para home, arquivo e páginas institucionais.' },
      { title: 'Prioridade visual', body: 'Na tela principal, cards visuais puxam a atenção. Texto mais longo fica dentro da notícia, onde faz sentido.' }
    ],
    aboutChecklistTitle: 'Compromissos desta fase',
    aboutChecklist: [
      'home com hierarquia editorial mais clara',
      'arquivo com destaque visual e navegação por tema',
      'páginas institucionais com propósito definido',
      'compatibilidade com a base estabilizada na fase anterior'
    ],
    standardsEyebrow: 'Método',
    standardsHeadline: 'Padrões editoriais visíveis na arquitetura, não escondidos no rodapé',
    standardsIntro2: 'Menos ruído institucional, menos espetáculo vazio, mais rastreabilidade do que está sendo publicado.',
    standardsCards2: [
      { title: 'Fonte identificada', body: 'A origem do material continua visível e integrada aos cards e às matérias.' },
      { title: 'Preprint tratado como provisório', body: 'Resultados sem revisão por pares entram com aviso explícito, sem maquiagem de certeza.' },
      { title: 'Home para chamar atenção, artigo para aprofundar', body: 'A capa favorece entrada visual e escaneabilidade. O contexto denso fica concentrado dentro da matéria.' },
      { title: 'Arquivo como produto editorial', body: 'O acervo deixa de ser sobra da home e passa a funcionar como página central de descoberta.' },
      { title: 'Rotas limpas PT/EN', body: 'A experiência institucional e de navegação usa caminhos reais em português e inglês.' },
      { title: 'Componentes reutilizáveis', body: 'Header, navegação principal, faixa temática, widgets laterais e navegação contextual passam a ser reutilizados.' }
    ],
    standardsWorkflowTitle: 'Fluxo editorial resumido',
    standardsWorkflow: [
      'triagem e curadoria do material disponível',
      'seleção de home com peso visual e relevância científica',
      'preservação do acervo no arquivo, sem apagar cobertura anterior',
      'sinalização de tipo de fonte, maturidade e contexto'
    ],
    visualLabelVideo: 'Vídeo',
    visualLabelGallery: 'Galeria'
  },
  en: {
    visualLeadTitle: 'Featured edition',
    visualLeadKicker: 'The homepage now opens with visual priority. Images and video do the grabbing; the deeper reading happens inside each story.',
    archiveHeroTitle: 'News archive',
    archiveHeroKicker: 'The archive stops behaving like an opaque chronological dump and becomes a discovery page with topical entry points and visual highlights.',
    archiveStatsStories: 'visible stories',
    archiveStatsTopics: 'coverage areas',
    archiveStatsLanguages: 'languages',
    archiveLoading: 'Loading the complete archive...',
    archiveLoaded: 'Complete archive loaded.',
    archiveNoItems: 'No stories found in this area right now.',
    topicNavTitle: 'Browse by topic',
    topicNavKicker: 'Choose the editorial doorway before falling into the chronological stream.',
    localNavAbout: 'About',
    localNavStandards: 'Standards',
    localNavArchive: 'Archive',
    aboutEyebrow: 'Institutional',
    aboutHeadline: 'Cosmos Week as a science news portal, not as an automatic release mirror',
    aboutIntro2: 'This phase reorganizes navigation, archive and institutional pages for actual editorial reading.',
    aboutCards: [
      { title: 'Editorial mission', body: 'Cover science with information hierarchy, context and visible distinction between institutional announcement, peer-reviewed paper, science reporting and preprint.' },
      { title: 'Discovery architecture', body: 'Navigation now privileges home, archive and persistent topics. Readers are no longer trapped in a single chronological rail.' },
      { title: 'Bilingual structure', body: 'Portuguese and English now have clean dedicated routes for home, archive and institutional pages.' },
      { title: 'Visual priority', body: 'On the main screen, visual cards pull attention first. Longer text is saved for inside the story.' }
    ],
    aboutChecklistTitle: 'Commitments in this phase',
    aboutChecklist: [
      'homepage with clearer editorial hierarchy',
      'archive with visual highlights and topical entry points',
      'institutional pages with defined roles',
      'compatibility with the stabilized base from the previous phase'
    ],
    standardsEyebrow: 'Method',
    standardsHeadline: 'Editorial standards visible in the architecture, not buried in the footer',
    standardsIntro2: 'Less institutional noise, less empty spectacle, more traceability around what is being published.',
    standardsCards2: [
      { title: 'Source identified', body: 'The source remains visible and integrated into cards and stories.' },
      { title: 'Preprints treated as provisional', body: 'Non-peer-reviewed results enter with explicit warnings rather than fake certainty.' },
      { title: 'Homepage to attract, article to deepen', body: 'The front page favors visual entry and scanability. Dense context lives inside the story.' },
      { title: 'Archive as editorial product', body: 'The collection stops being residue from the homepage and becomes a central discovery page.' },
      { title: 'Clean PT/EN routes', body: 'Institutional and navigation experiences now use real Portuguese and English paths.' },
      { title: 'Reusable components', body: 'Header, main navigation, topical strip, sidebar widgets and contextual navigation are reused.' }
    ],
    standardsWorkflowTitle: 'Condensed editorial flow',
    standardsWorkflow: [
      'triage and curation of available material',
      'homepage selection driven by visual weight and scientific relevance',
      'archive preservation without erasing older coverage',
      'clear signaling of source type, maturity and context'
    ],
    visualLabelVideo: 'Video',
    visualLabelGallery: 'Gallery'
  }
};

const FULL_ARCHIVE_FEED = '/all_posts.json';

  const IMG = {
    pillars:         'https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Pillars_of_creation_2014_HST_WFC3-UVIS_full-res_denoised.jpg/1280px-Pillars_of_creation_2014_HST_WFC3-UVIS_full-res_denoised.jpg',
    andromeda:       'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Andromeda_Galaxy_%28with_h-alpha%29.jpg/1280px-Andromeda_Galaxy_%28with_h-alpha%29.jpg',
    hubbledeep:      'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Hubble_ultra_deep_field.jpg/1280px-Hubble_ultra_deep_field.jpg',
    blackhole:       'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Black_hole_-_Messier_87_crop_max_res.jpg/1280px-Black_hole_-_Messier_87_crop_max_res.jpg',
    exoplanet:       'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Transiting_Exoplanet_Artist%27s_Impression.jpg/1280px-Transiting_Exoplanet_Artist%27s_Impression.jpg',
    earth:           'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/1280px-The_Earth_seen_from_Apollo_17.jpg',
    cern:            'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/CERN_Globe_and_Main_Building.jpg/1280px-CERN_Globe_and_Main_Building.jpg',
    milkyway:        'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg/1280px-Milky_Way%2C_above_Mauna_Kea_-_by_Luc_Viatour.jpg',
    supernova:       'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Cassiopeia_A.jpg/1280px-Cassiopeia_A.jpg',
  };

  const UI = {
    pt: {
      logoSub: 'Notícias Científicas em português',
      home: 'Início', archive: 'Arquivo', about: 'Sobre', standards: 'Padrões',
      methodology: 'Metodologia', advertise: 'Anuncie', mediaKit: 'Media kit', privacy: 'Política de privacidade', terms: 'Termos de uso', update: 'Atualizar',
      searchPlaceholder: 'Buscar notícias, temas ou fontes...',
      ticker: 'Destaques',
      latestTitle: 'Últimas publicações',
      latestKicker: 'Cobertura recente organizada para leitura rápida, sem perder contexto editorial.',
      essentialTitle: 'Leitura essencial',
      essentialKicker: 'Seleção principal da edição atual, priorizando impacto científico, contexto e legibilidade.',
      monitorTitle: 'Em observação',
      monitorKicker: 'Sinais, missões, instrumentos e resultados que seguem sob acompanhamento mais próximo na cobertura.',
      topicShelfTitle: 'Navegação temática',
      topicShelfKicker: 'Áreas permanentes de cobertura para entrar no arquivo pela porta certa, não pelo acaso cronológico.',
      archiveLink: 'Ver arquivo completo',
      preprintsTitle: 'Radar de preprints',
      preprintsKicker: 'Resultados provisórios em circulação técnica, identificados como não revisados por pares.',
      trending: 'Em alta',
      latestUpdatesTitle: 'Últimas atualizações',
      topicNavTitle: 'Navegue por tema',
      sourceMixTitle: 'Mapa editorial',
      quickLinksTitle: 'Acesso rápido',
      archivePicksTitle: 'Do arquivo',
      quickArchive: 'Abrir arquivo',
      quickRSS: 'Abrir RSS',
      quickStandards: 'Ver padrões',
      quickSearch: 'Buscar no site',
      archiveTitle: 'Arquivo editorial',
      archiveKicker: 'Todas as matérias disponíveis do arquivo no portal.',
      searchTitle: 'Busca', noSearch: 'Nenhum resultado encontrado.',
      trySearch: 'Experimente termos como JWST, matéria escura, exoplaneta, buraco negro ou Euclid.',
      topbarCopy: 'Portal de <strong>Notícias Científicas</strong> com cobertura contínua e rigor na apuração.',
      footerDescription: 'Portal de Notícias Científicas em português, com cobertura de astronomia, física e ciência em geral.',
      footerNavTitle: 'Navegação', footerSourcesTitle: 'Transparência',
      footerFeed: 'RSS do portal', footerSitemap: 'Sitemap',
      footerCorrections: 'Correções e metodologia',
      footerBottomLeft: '© 2026 Cosmos Week',
      footerBottomCenter: 'Notícias científicas com contexto e compromisso com a evidência.',
      footerBottomRight: '',
      newsletterTitle: 'Newsletter', newsletterLabel: 'Seu e-mail',
      newsletterDescription: 'Receba Notícias semanais do Cosmos Week no seu e-mail.',
      newsletterPlaceholder: 'Seu e-mail', newsletterButton: 'Inscrever',
      newsletterNote: 'Sem spam. Apenas atualizações editoriais relevantes.',
      newsletterSuccess: 'E-mail salvo neste navegador.',
      cookieTitle: 'Privacidade', cookieText: 'Usamos analytics para medir audiência e podemos exibir anúncios no futuro. Você pode aceitar tudo, liberar só analytics ou recusar. Os detalhes estão na política de privacidade.',
      cookiePolicy: 'política de privacidade', cookieDeny: 'Recusar', cookieAnalytics: 'Só analytics', cookieAccept: 'Aceitar tudo', cookieAria: 'Aviso de cookies', newsletterInvalid: 'Digite um e-mail válido.',
      lastUpdatedPrefix: 'Atualização:', latestFeed: 'feed carregado',
      resultsFor: 'resultado(s) para',
      newsroom: 'Redação Cosmos Week',
      articleHighlights: 'Pontos-chave', articleSource: 'Fonte original',
      articleShare: 'Compartilhar', articleReadOriginal: 'Ler fonte original',
      relatedTitle: 'Leia também',
      warningTitle: 'Resultado provisório',
      standardsPageTitle: 'Padrões editoriais',
      aboutPageTitle: 'Sobre o Cosmos Week',
      aboutIntro: 'O Cosmos Week foi desenhado como um portal de Notícias Científicas, não como um espelho automático de releases institucionais. A automação existe para acelerar a triagem, a organização e a transparência, mas a arquitetura do site foi reformulada para deixar explícito o tipo de fonte, o grau de maturidade do resultado e a diferença entre anúncio, paper e preprint.',
      aboutBody: 'A linha editorial privilegia astronomia, astrofísica, cosmologia e ciência em geral, com abertura controlada para física, biologia, química e ciências da Terra quando o material tem relevância científica real. O objetivo não é despejar volume. É construir um arquivo navegável de notícias curtas e médias que preservem contexto, cautela e legibilidade.',
      standardsIntro: 'O portal segue um conjunto fixo de regras para evitar dois vícios comuns da divulgação online: transformar comunicado institucional em matéria autônoma sem transparência, e apresentar preprint como se fosse ciência consolidada. Sem maquiagem editorial, mais distinção entre o que foi medido, o que foi inferido e o que continua em aberto.',
      standardsCards: [
        { title: '1. Fonte real identificada', body: 'Toda matéria carrega o tipo de fonte. Um paper revisado por pares não recebe o mesmo tratamento visual de um preprint ou de um release institucional.' },
        { title: '2. Preprint não vira verdade', body: 'Conteúdo vindo do arXiv é rotulado como provisório. Ele pode entrar no portal, mas sempre como resultado em avaliação e nunca como conclusão definitiva.' },
        { title: '3. Curadoria contra ruído institucional', body: 'Galerias de imagem, vídeos, perfis pessoais, prêmios e chamadas burocráticas são filtrados antes de chegar à home.' },
        { title: '4. Contexto antes de rotular', body: 'Nossos textos respondem três perguntas na seguinte ordem: o que aconteceu, por que isso importa e o que ainda não sabemos.' }
      ],
      sourceMixLine: 'item(ns)', clickToRead: 'Abrir matéria', copyLink: 'Copiar link', shareNow: 'Compartilhar',
      copied: 'Link copiado.', shareFallback: 'Link copiado para compartilhamento.', updateDone: 'Feed atualizado.', updateFail: 'Não foi possível atualizar agora.',
      welcome: 'Feed carregado. Cobertura atualizada.',
      backHome: 'Voltar ao início', allCategories: 'Todas',
      scoreLabel: 'Relevância editorial', evidenceLabel: 'Evidência', noveltyLabel: 'Novidade',
      sourceLabel: 'Fonte', accessLabel: 'Acessibilidade',
      preprintWarning: 'Este trabalho é um preprint — resultado em circulação técnica ainda não submetido a revisão por pares formal. Trate-o como evidência em teste, não como conclusão encerrada.'
    },
    en: {
      logoSub: 'Science journalism',
      home: 'Home', archive: 'Archive', about: 'About', standards: 'Standards',
      methodology: 'Methodology', advertise: 'Advertise', mediaKit: 'Media kit', privacy: 'Privacy policy', terms: 'Terms of use', update: 'Refresh',
      searchPlaceholder: 'Search stories, topics or sources...',
      ticker: 'Highlights',
      latestTitle: 'Latest stories',
      latestKicker: 'Recent coverage arranged for faster scanning without flattening editorial context.',
      essentialTitle: 'Essential reading',
      essentialKicker: 'The core stories of the current edition, selected for scientific weight, context and staying power.',
      monitorTitle: 'Under observation',
      monitorKicker: 'Signals, missions, instruments and results that remain under closer editorial watch.',
      topicShelfTitle: 'Topic map',
      topicShelfKicker: 'Persistent coverage areas that let readers enter the archive by subject, not by chance.',
      archiveLink: 'View full archive',
      preprintsTitle: 'Preprint radar',
      preprintsKicker: 'Provisional results in technical circulation, explicitly marked as not peer reviewed.',
      trending: 'Trending',
      latestUpdatesTitle: 'Latest updates',
      topicNavTitle: 'Browse by topic',
      sourceMixTitle: 'Editorial map',
      quickLinksTitle: 'Quick access',
      archivePicksTitle: 'From the archive',
      quickArchive: 'Open archive',
      quickRSS: 'Open RSS',
      quickStandards: 'View standards',
      quickSearch: 'Search the site',
      archiveTitle: 'Editorial archive',
      archiveKicker: 'Every story currently available in the editorial archive.',
      searchTitle: 'Search', noSearch: 'No results found.',
      trySearch: 'Try terms such as JWST, dark matter, exoplanet, black hole or Euclid.',
      topbarCopy: 'A <strong>science journalism</strong> portal built around continuous coverage, editorial writing and rigorous reporting.',
      footerDescription: 'Portuguese-first science journalism with editorial writing across astronomy, physics and frontier research.',
      footerNavTitle: 'Navigation', footerSourcesTitle: 'Transparency',
      footerFeed: 'Portal RSS', footerSitemap: 'Sitemap',
      footerCorrections: 'Corrections and methodology',
      footerBottomLeft: '© 2026 Cosmos Week',
      footerBottomCenter: 'Science reporting built around context, hierarchy of information and evidence.',
      footerBottomRight: '',
      newsletterTitle: 'Newsletter', newsletterLabel: 'Your email',
      newsletterDescription: 'Get Cosmos Week editorial highlights in your inbox.',
      newsletterPlaceholder: 'Your email', newsletterButton: 'Subscribe',
      newsletterNote: 'No spam. Only relevant editorial updates.',
      newsletterSuccess: 'Email saved in this browser.',
      cookieTitle: 'Privacy', cookieText: 'We use analytics to measure audience and may show advertising in the future. You can accept everything, allow analytics only or decline. Details are in the privacy policy.',
      cookiePolicy: 'privacy policy', cookieDeny: 'Decline', cookieAnalytics: 'Analytics only', cookieAccept: 'Accept all', cookieAria: 'Cookie notice', newsletterInvalid: 'Enter a valid email address.',
      lastUpdatedPrefix: 'Auto update:', latestFeed: 'feed loaded',
      resultsFor: 'result(s) for',
      newsroom: 'Cosmos Week Desk',
      articleHighlights: 'Key points', articleSource: 'Original source',
      articleShare: 'Share', articleReadOriginal: 'Read source story',
      relatedTitle: 'Read also',
      warningTitle: 'Provisional result',
      standardsPageTitle: 'Editorial standards',
      aboutPageTitle: 'About Cosmos Week',
      aboutIntro: 'Cosmos Week was built as a science journalism portal, not as an automatic mirror of institutional releases. Automation is there to speed up triage, organization and transparency, but the site architecture was redesigned to make source type, result maturity and the gap between announcement, paper and preprint explicit.',
      aboutBody: 'The editorial line prioritizes astronomy, astrophysics, cosmology and frontier research, with controlled space for physics, biology, chemistry and Earth science when the material carries real scientific relevance. The goal is not to dump volume. It is to build a navigable archive of short and medium-length stories that preserve context, caution and readability.',
      standardsIntro: 'The portal follows a fixed ruleset to avoid two common online-science traps: turning institutional communications into apparently independent reporting without transparency, and presenting a preprint as if it were settled science. Less editorial makeup, more distinction between what was measured, what was inferred and what remains open.',
      standardsCards: [
        { title: '1. Source type stays visible', body: 'Every story carries its source type. A peer-reviewed paper does not receive the same visual treatment as a preprint or an institutional release.' },
        { title: '2. Preprints are not magic truths', body: 'Content from arXiv is labeled as provisional. It can appear in the portal, but only as work under evaluation, never as a final answer.' },
        { title: '3. Curation filters institutional noise', body: 'Image galleries, videos, personal profiles, awards and bureaucratic calls are filtered before they can reach the homepage.' },
        { title: '4. Context comes before adjectives', body: 'The reporting structure tries to answer three questions in order: what happened, why it matters and what we still do not know.' }
      ],
      sourceMixLine: 'item(s)', clickToRead: 'Open story', copyLink: 'Copy link', shareNow: 'Share',
      copied: 'Link copied.', shareFallback: 'Link copied for sharing.', updateDone: 'Feed refreshed.', updateFail: 'Could not refresh right now.',
      welcome: 'Feed loaded. Broader editorial coverage with stronger section balance.',
      backHome: 'Back to home', allCategories: 'All',
      scoreLabel: 'Editorial relevance', evidenceLabel: 'Evidence', noveltyLabel: 'Novelty',
      sourceLabel: 'Source', accessLabel: 'Accessibility',
      preprintWarning: 'This work is a preprint — a result in technical circulation not yet submitted to formal peer review. Treat it as evidence under test, not as a closed conclusion.'
    }
  };

  const CLIENT_NOISE_PATTERNS = [
    /week in images/i, /^image:/i, /^earth from space/i,
    /^i am artemis/i, /audio excerpt/i, /awards categories/i, /crew.?s suits/i,
    /\/image-article\//i, /\/week_in_images\//i, /\/photojournal\//i
  ];

  function isClientNoise(post) {
    const haystack = [post?.title, post?.title_pt, post?.title_en, post?.excerpt, post?.excerpt_pt, post?.excerpt_en, post?.srcUrl]
      .filter(Boolean).join(' ');
    return CLIENT_NOISE_PATTERNS.some(p => p.test(haystack));
  }

  function normalizePosts(rawPosts) {
    if (!Array.isArray(rawPosts)) return [];
    return rawPosts
      .filter(post => post && post.slug)
      .filter(post => !isClientNoise(post))
      .sort((a, b) => String(b.publishedIso || '').localeCompare(String(a.publishedIso || '')));
  }

  const ARCHIVE_CACHE_KEY = 'cw_archive_cache_v3';
  const FRONT_HISTORY_KEY = 'cw_front_history_v1';
  const FRONT_ROTATION_COUNTER_KEY = 'cw_front_rotation_counter_v1';
  const frontLayoutCache = new Map();

  function readFrontHistory() {
    try {
      const parsed = JSON.parse(localStorage.getItem(FRONT_HISTORY_KEY) || '{}');
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (e) {
      return {};
    }
  }

  function writeFrontHistory(history) {
    try { localStorage.setItem(FRONT_HISTORY_KEY, JSON.stringify(history || {})); } catch (e) {}
  }

  function rememberFrontSelection(bucket, slugs, limit = 24) {
    const history = readFrontHistory();
    const previous = Array.isArray(history[bucket]) ? history[bucket] : [];
    const incoming = (Array.isArray(slugs) ? slugs : []).filter(Boolean);
    history[bucket] = [...incoming, ...previous.filter(slug => !incoming.includes(slug))].slice(0, limit);
    writeFrontHistory(history);
  }

  function nextPersistentRotationSeed() {
    let seed = 0;
    try {
      seed = Number(localStorage.getItem(FRONT_ROTATION_COUNTER_KEY) || '0') || 0;
      seed = (seed + 1) % 1000000;
      localStorage.setItem(FRONT_ROTATION_COUNTER_KEY, String(seed));
    } catch (e) {
      seed = Math.floor(Date.now() / 1000) % 1000000;
    }
    return seed;
  }

  function postRichnessScore(post) {
    return [
      post?.title, post?.title_pt, post?.title_en,
      post?.excerpt, post?.excerpt_pt, post?.excerpt_en,
      post?.body, post?.body_pt, post?.body_en
    ].filter(Boolean).join(' ').length;
  }

  function pickBestPost(existing, candidate) {
    if (!existing) return candidate;
    const existingStamp = Date.parse(existing.lastModifiedIso || existing.publishedIso || '') || 0;
    const candidateStamp = Date.parse(candidate.lastModifiedIso || candidate.publishedIso || '') || 0;
    if (candidateStamp > existingStamp) return candidate;
    if (candidateStamp < existingStamp) return existing;
    return postRichnessScore(candidate) >= postRichnessScore(existing) ? candidate : existing;
  }

  function mergePostCollections(primary = [], secondary = []) {
    const map = new Map();
    [...secondary, ...primary].forEach(post => {
      if (!post || !post.slug) return;
      map.set(post.slug, pickBestPost(map.get(post.slug), post));
    });
    return normalizePosts([...map.values()]);
  }

  function persistArchiveCache() {
    try { localStorage.setItem(ARCHIVE_CACHE_KEY, JSON.stringify(DB)); } catch (e) {}
  }

  function hydrateArchive(rawPosts) {
    let cached = [];
    try {
      const parsed = JSON.parse(localStorage.getItem(ARCHIVE_CACHE_KEY) || '[]');
      if (Array.isArray(parsed)) cached = parsed;
    } catch (e) {}
    const merged = mergePostCollections(rawPosts, cached);
    try { localStorage.setItem(ARCHIVE_CACHE_KEY, JSON.stringify(merged)); } catch (e) {}
    return merged;
  }

  let DB = hydrateArchive(window.postsData || []);

  function ensureFullArchiveLoaded(force = false) {
    if (fullArchiveLoaded && !force) return Promise.resolve(DB);
    if (fullArchivePromise && !force) return fullArchivePromise;
    fullArchivePromise = fetch(`${FULL_ARCHIVE_FEED}?cb=${Date.now()}`, { cache: 'no-store' })
      .then(resp => {
        if (!resp.ok) throw new Error('archive fetch failed');
        return resp.json();
      })
      .then(payload => {
        if (Array.isArray(payload) && payload.length) {
          DB = mergePostCollections(payload, DB);
          fullArchiveLoaded = DB.length >= payload.length || DB.length >= 100;
          frontLayoutCache.clear();
          persistArchiveCache();
        }
        return DB;
      })
      .catch(() => DB)
      .finally(() => {
        fullArchivePromise = null;
      });
    return fullArchivePromise;
  }

  let currentLang = localStorage.getItem('cw_lang') === 'en' ? 'en' : 'pt';
  try {
    const _params = new URLSearchParams(window.location.search);
    const _path = window.location.pathname || '';
    const _bodyLang = (document.body?.dataset?.cwLang || '').toLowerCase();
    if ((_params.get('lang') || '').toLowerCase() === 'en' || /^\/en(?:\/|$)/i.test(_path) || _bodyLang === 'en') currentLang = 'en';
    if ((_params.get('lang') || '').toLowerCase() === 'pt' || /^\/noticia\/[^\/]+\/?$/i.test(_path) || _bodyLang === 'pt') currentLang = 'pt';
  } catch (err) {}
  let currentPage = 'home';
  let currentArticleSlug = null;
  let currentCategory = 'all';
  let fullArchiveLoaded = DB.length >= 100;
  let fullArchivePromise = null;
  let searchTimer = null;
  let toastTimer = null;
  let heroRotationSeed = nextPersistentRotationSeed();

  function persistHeroRotationSeed() {
    try { sessionStorage.setItem('cw_hero_rotation_seed', String(heroRotationSeed)); } catch (e) {}
  }
  persistHeroRotationSeed();

  function bumpHeroRotationSeed(step = 1) {
    heroRotationSeed = (heroRotationSeed + Math.max(1, step|0)) % 1000000;
    frontLayoutCache.clear();
    persistHeroRotationSeed();
  }

  function tr(key) { return UI[currentLang][key] ?? UI.pt[key] ?? key; }

  function decodeEntitiesLoose(value = '') {
    let text = String(value ?? '');
    for (let i = 0; i < 3; i += 1) {
      const textarea = document.createElement('textarea');
      textarea.innerHTML = text;
      const decoded = textarea.value;
      if (decoded === text) break;
      text = decoded;
    }
    return text;
  }

  function sanitizeDisplayText(value = '') {
    let text = decodeEntitiesLoose(String(value ?? ''));
    text = text
      .replace(/\u00a0/g, ' ')
      .replace(/&\s*nbsp\s*;?/gi, ' ')
      .replace(/\bnbsp\b\.?/gi, ' ')
      .replace(/&\s*amp\s*;?/gi, '&');
    text = text
      .replace(/\s+([,;:.!?])/g, '$1')
      .replace(/([\(\[{])\s+/g, '$1')
      .replace(/\s+([\)\]}])/g, '$1')
      .replace(/([,;:!?])([^\s"'”’\)\]}])/g, '$1 $2')
      .replace(/(^|[^\d])\.([^\s\d])/g, '$1. $2')
      .replace(/\s{2,}/g, ' ')
      .trim();
    return text;
  }

  function sanitizeDisplayList(items = []) {
    if (!Array.isArray(items)) return [];
    return items
      .map(item => sanitizeDisplayText(item))
      .filter(Boolean);
  }

  function textFor(post, field) {
    if (!post) return '';
    const value = (currentLang === 'en' && post[`${field}_en`])
      ? post[`${field}_en`]
      : (currentLang === 'pt' && post[`${field}_pt`])
        ? post[`${field}_pt`]
        : (post[field] || '');
    return typeof value === 'string' ? sanitizeDisplayText(value) : value;
  }

  function listFor(post, field) {
    if (!post) return [];
    const value = (currentLang === 'en' && post[`${field}_en`])
      ? post[`${field}_en`]
      : (currentLang === 'pt' && post[`${field}_pt`])
        ? post[`${field}_pt`]
        : (post[field] || []);
    return Array.isArray(value) ? sanitizeDisplayList(value) : value;
  }

  function normalizarTexto(t = '') {
    return String(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  }

  function prettyCategory(cat = '') {
    const labels = {
      pt: { Astronomia:'Astronomia', Cosmologia:'Cosmologia', 'Astrofísica':'Astrofísica', Exoplanetas:'Exoplanetas', Física:'Física', Biologia:'Biologia', Química:'Química', 'Ciências da Terra':'Ciências da Terra' },
      en: { Astronomia:'Astronomy', Cosmologia:'Cosmology', 'Astrofísica':'Astrophysics', Exoplanetas:'Exoplanets', Física:'Physics', Biologia:'Biology', Química:'Chemistry', 'Ciências da Terra':'Earth Science' }
    };
    return (labels[currentLang] && labels[currentLang][cat]) || cat;
  }

  function formatMeta(post) {
    return {
      date: currentLang === 'en' ? (post.date_en || post.date) : (post.date_pt || post.date),
      time: currentLang === 'en' ? (post.time_en || post.time) : (post.time_pt || post.time),
      read: currentLang === 'en' ? (post.read_en || post.read) : (post.read_pt || post.read)
    };
  }

  function fallbackImage(post) {
    const text = `${post?.title||''} ${post?.title_en||''} ${post?.excerpt||''} ${post?.cat||''}`.toLowerCase();
    if (/gravitational wave|kilonova|black hole|neutron star|astrofísica/.test(text)) return IMG.blackhole;
    if (/particle|lhc|cern|muon|physics|física/.test(text)) return IMG.cern;
    if (/exoplanet|exoplaneta|biosignature|habitable/.test(text)) return IMG.exoplanet;
    if (/cosmolog|dark energy|dark matter|cmb/.test(text)) return IMG.hubbledeep;
    if (/galaxy|galáxia|spiral|milky way/.test(text)) return IMG.andromeda;
    if (/earth|clima|climate|ocean|atmosphere/.test(text)) return IMG.earth;
    if (/supernova/.test(text)) return IMG.supernova;
    return ({ 'Astrofísica':IMG.blackhole, 'Física':IMG.cern, 'Exoplanetas':IMG.exoplanet,
               'Ciências da Terra':IMG.earth, 'Cosmologia':IMG.hubbledeep,
               'Astronomia':IMG.milkyway, 'Química':IMG.pillars, 'Biologia':IMG.earth })[post?.cat] || IMG.pillars;
  }

  function primaryImage(post) {
    const src = String(post?.img || '').trim();
    return src || fallbackImage(post);
  }

  function escapeAttr(v = '') { return String(v).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  function imageAttrs(post, loading = 'lazy') {
    const primary  = escapeAttr(primaryImage(post));
    const fallback = escapeAttr(fallbackImage(post));
    const alt      = escapeAttr(textFor(post, 'title'));
    const decode   = loading === 'eager' ? 'sync' : 'async';
    return `src="${primary}" alt="${alt}" loading="${loading}" decoding="${decode}" onerror="if(this.src!=='${fallback}'){this.src='${fallback}'}"`;
  }

  function withLanguageParam(url, lang = currentLang) {
    try {
      const resolved = new URL(url, window.location.origin);
      const path = resolved.pathname || '/';
      const pageFromQuery = normalizePageKey(resolved.searchParams.get('page') || '');
      const article = resolved.searchParams.get('article');
      if (article) {
        const post = DB.find(item => item.slug === article);
        if (post) return getURLForArticle(post, lang);
      }
      if (pageFromQuery !== 'home' || /^\/(?:en(?:\/archive|\/about|\/standards)?|arquivo|sobre|padroes)\/?$/i.test(path) || path === '/') {
        const inferred = pageFromQuery !== 'home' ? pageFromQuery : routePageFromPath(path);
        return new URL(primaryPageHref(inferred, lang).replace(/^\//, ''), SITE.canonicalBaseUrl).toString();
      }
      if (lang === 'en') resolved.searchParams.set('lang', 'en');
      else resolved.searchParams.delete('lang');
      return resolved.toString();
    } catch {
      return url;
    }
  }

  function articleAlternateUrls(post) {
    const slug = encodeURIComponent(post?.slug || '');
    return {
      pt: post?.canonicalUrl_pt || post?.shareUrl_pt || `${SITE.canonicalBaseUrl}noticia/${slug}/`,
      en: post?.canonicalUrl_en || post?.shareUrl_en || `${SITE.canonicalBaseUrl}en/news/${slug}/`,
      xDefault: post?.canonicalUrl_pt || post?.shareUrl_pt || `${SITE.canonicalBaseUrl}noticia/${slug}/`
    };
  }

  function getURLForArticle(post, lang = currentLang) {
    const urls = articleAlternateUrls(post);
    return lang === 'en' ? urls.en : urls.pt;
  }

  function getRealURLForArticle(post, lang = currentLang) {
    if (lang === 'en' && post?.realUrl_en) return post.realUrl_en;
    if (lang !== 'en' && post?.realUrl_pt) return post.realUrl_pt;
    if (post?.realUrl) return post.realUrl;
    return getURLForArticle(post, lang);
  }

  function getShareURLForArticle(post, lang = currentLang) {
    const urls = articleAlternateUrls(post);
    return lang === 'en' ? urls.en : urls.pt;
  }

  function getCanonicalURLForArticle(post, lang = currentLang) {
    const urls = articleAlternateUrls(post);
    return lang === 'en' ? urls.en : urls.pt;
  }

  function pageUrl(page, lang = currentLang) {
    return primaryPageHref(page, lang);
  }

  function canonicalPageUrl(page, lang = currentLang) {
    return new URL(primaryPageHref(page, lang).replace(/^\//, ''), SITE.canonicalBaseUrl).toString();
  }

  function auxiliaryPageHref(kind, lang = currentLang) {
    const table = {
      pt: { advertise: '/anuncie.html', mediaKit: '/media-kit.html', privacy: '/politica-de-privacidade.html', terms: '/termos-de-uso.html' },
      en: { advertise: '/en/advertise/', mediaKit: '/en/media-kit/', privacy: '/en/privacy/', terms: '/en/terms/' }
    };
    const selected = table[lang === 'en' ? 'en' : 'pt'];
    return selected[kind] || pageUrl('home', lang);
  }

  function syncAuxiliaryLinks() {
    const ids = { adsBtn: 'advertise', footerAdvertise: 'advertise', footerMediaKit: 'mediaKit', footerPrivacy: 'privacy', footerTerms: 'terms' };
    for (const [id, key] of Object.entries(ids)) {
      const el = document.getElementById(id);
      if (el) el.setAttribute('href', auxiliaryPageHref(key));
    }
    const cookieLink = document.getElementById('cookiePolicyLink');
    if (cookieLink) cookieLink.setAttribute('href', auxiliaryPageHref('privacy'));
    syncPrimaryNavigationLinks();
  }

  function extraTr(key) {
    return (EXTRA_UI[currentLang] && EXTRA_UI[currentLang][key]) || (EXTRA_UI.pt && EXTRA_UI.pt[key]) || key;
  }

  function normalizePageKey(value = '') {
    const page = String(value || '').toLowerCase().trim();
    const map = {
      home: 'home', inicio: 'home',
      archive: 'archive', arquivo: 'archive',
      about: 'about', sobre: 'about',
      standards: 'standards', padroes: 'standards', padrões: 'standards',
      search: 'search', busca: 'search'
    };
    return map[page] || 'home';
  }

  function routePageFromPath(path = window.location.pathname || '/') {
    const cleaned = String(path || '/').replace(/\/+$/, '') || '/';
    if (/^\/arquivo$/i.test(cleaned) || /^\/en\/archive$/i.test(cleaned)) return 'archive';
    if (/^\/sobre$/i.test(cleaned) || /^\/en\/about$/i.test(cleaned)) return 'about';
    if (/^\/padroes$/i.test(cleaned) || /^\/en\/standards$/i.test(cleaned)) return 'standards';
    return 'home';
  }

  function primaryPageHref(page, lang = currentLang) {
    const selected = PAGE_ROUTE_MAP[lang === 'en' ? 'en' : 'pt'];
    return selected[normalizePageKey(page)] || selected.home;
  }

  function syncPrimaryNavigationLinks() {
    const navTargets = {
      navHome: 'home',
      navArchive: 'archive',
      navAbout: 'about',
      navStandards: 'standards',
      footerHome: 'home',
      footerArchive: 'archive',
      footerAbout: 'about',
      footerStandards: 'standards',
      archiveLinkTop: 'archive'
    };
    Object.entries(navTargets).forEach(([id, page]) => {
      const el = document.getElementById(id);
      if (el) el.setAttribute('href', primaryPageHref(page));
    });

    const ptSwitcher = document.getElementById('langPt');
    const enSwitcher = document.getElementById('langEn');
    if (currentPage === 'article' && currentArticleSlug) {
      const post = DB.find(item => item.slug === currentArticleSlug);
      if (post) {
        if (ptSwitcher) ptSwitcher.setAttribute('href', getURLForArticle(post, 'pt'));
        if (enSwitcher) enSwitcher.setAttribute('href', getURLForArticle(post, 'en'));
        return;
      }
    }
    const targetPage = normalizePageKey(currentPage);
    if (ptSwitcher) ptSwitcher.setAttribute('href', primaryPageHref(targetPage, 'pt'));
    if (enSwitcher) enSwitcher.setAttribute('href', primaryPageHref(targetPage, 'en'));
  }

  function contextualNavMarkup(activePage = currentPage) {
    const links = [
      ['about', extraTr('localNavAbout')],
      ['standards', extraTr('localNavStandards')],
      ['archive', extraTr('localNavArchive')]
    ];
    return `
      <nav class="local-page-nav" aria-label="${currentLang === 'en' ? 'Contextual navigation' : 'Navegação contextual'}">
        ${links.map(([page, label]) => `
          <a class="local-page-link${normalizePageKey(activePage) === page ? ' on' : ''}" href="${primaryPageHref(page)}" onclick="event.preventDefault(); openPage('${page}')">${label}</a>
        `).join('')}
      </nav>`;
  }

  function renderChecklist(items = []) {
    return `
      <ul class="institution-list">
        ${items.map(item => `<li>${sanitizeDisplayText(item)}</li>`).join('')}
      </ul>`;
  }

  function keywordListFor(post) {
    const kws = currentLang === 'en' ? (post.keywords_en || post.keywords || []) : (post.keywords_pt || post.keywords || []);
    return Array.isArray(kws) ? kws : [];
  }

  function sourceDomainFor(post) {
    return post.sourceDomain || (() => { try { return new URL(post.srcUrl).hostname; } catch { return ''; } })();
  }

  function averageVisibleScore(key, filterFn = null) {
    const posts = (filterFn ? DB.filter(filterFn) : DB).filter(p => !p.isPreprint || key === 'overall');
    if (!posts.length) return 0;
    const total = posts.reduce((acc, p) => acc + (key === 'overall' ? (p.score||0) : ((p.scoreBreakdown||{})[key]||0)), 0);
    return Math.round(total / posts.length);
  }

  function filteredRegularPosts() {
    return DB.filter(p => !p.isPreprint && (currentCategory === 'all' || p.cat === currentCategory));
  }

  function filteredPreprints() {
    return DB.filter(p => p.isPreprint && (currentCategory === 'all' || p.cat === currentCategory));
  }

  // ── Badge row ─────────────────────────────────────────────────────────────
  function renderBadgeRow(post, extra = '') {
    const catCls = (post.catCls || normalizarTexto(post.cat || '').replace(/\s+/g,'-'));
    const catLabel = prettyCategory(post.cat);
    let chips = `<span class="label ${catCls}">${catLabel}</span>`;
    if (post.isPreprint) chips += `<span class="status-chip preprint">Preprint</span>`;
    else if (post.editorialBand === 'flagship') chips += `<span class="status-chip">${currentLang === 'en' ? 'Top story' : 'Destaque'}</span>`;
    if (extra) chips += extra;
    return `<div class="label-row">${chips}</div>`;
  }

  // ── Card markup ────────────────────────────────────────────────────────────
  function cardMarkup(post) {
    const meta = formatMeta(post);
    return `
      <article class="story-card" onclick="openArticle('${escapeAttr(post.slug)}')">
        <div class="card-cover"><img ${imageAttrs(post)}></div>
        <div class="card-body">
          ${renderBadgeRow(post)}
          <h3 class="headline-md">${textFor(post,'title')}</h3>
          <p class="deck small">${textFor(post,'excerpt')}</p>
          <div class="meta-row"><span>${meta.date}</span><span>${meta.read}</span><span>${post.source}</span></div>
        </div>
      </article>`;
  }

  function compactMarkup(post) {
    const meta = formatMeta(post);
    return `
      <article class="compact-item" onclick="openArticle('${escapeAttr(post.slug)}')">
        <div class="compact-cover"><img ${imageAttrs(post)}></div>
        <div class="compact-body">
          ${renderBadgeRow(post)}
          <h3 class="headline-md" style="font-size:1.05rem;">${textFor(post,'title')}</h3>
          <div class="compact-meta">${meta.date} · ${meta.read} · ${post.source}</div>
        </div>
      </article>`;
  }

  // ── Hero ───────────────────────────────────────────────────────────────────
  function hashString(input = '') {
    let h = 2166136261;
    for (let i = 0; i < input.length; i++) {
      h ^= input.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return Math.abs(h >>> 0);
  }

  function postTimestamp(post) {
    return Date.parse(post?.lastModifiedIso || post?.publishedIso || '') || 0;
  }

  function postFreshnessWeight(post) {
    const stamp = postTimestamp(post);
    if (!stamp) return 0;
    const ageDays = (Date.now() - stamp) / 86400000;
    if (ageDays <= 1) return 28;
    if (ageDays <= 3) return 23;
    if (ageDays <= 7) return 18;
    if (ageDays <= 14) return 12;
    if (ageDays <= 30) return 7;
    return 0;
  }

  function isFreshFrontPost(post) {
    const stamp = postTimestamp(post);
    if (!stamp) return false;
    const ageHours = (Date.now() - stamp) / 3600000;
    return ageHours <= 120;
  }

  function heroPriority(post) {
    let total = ((post?.score || 0) * 0.42) + postFreshnessWeight(post);
    if (post?.trending) total += 10;
    if (post?.featured) total += 6;
    if (post?.editorialBand === 'flagship') total += 4;
    if (isFreshFrontPost(post)) total += 24;
    return total;
  }

  function frontRegularPostsForCurrentCategory() {
    return [...filteredRegularPosts()].sort((a, b) => {
      const freshDiff = Number(isFreshFrontPost(b)) - Number(isFreshFrontPost(a));
      if (freshDiff) return freshDiff;
      const stampDiff = postTimestamp(b) - postTimestamp(a);
      if (stampDiff) return stampDiff;
      const byPriority = heroPriority(b) - heroPriority(a);
      if (byPriority) return byPriority;
      return String(b.slug || '').localeCompare(String(a.slug || ''));
    });
  }

  function frontHistoryPenalty(post, bucket) {
    const history = readFrontHistory();
    const seen = Array.isArray(history[bucket]) ? history[bucket] : [];
    const idx = seen.indexOf(post?.slug);
    return idx === -1 ? 0 : (seen.length - idx);
  }

  function pickRotatedSet(posts, count, bucket, seedOffset = 0) {
    if (!Array.isArray(posts) || !posts.length || count <= 0) return [];
    const ranked = [...posts].sort((a, b) => {
      const penaltyDiff = frontHistoryPenalty(a, bucket) - frontHistoryPenalty(b, bucket);
      if (penaltyDiff) return penaltyDiff;
      return 0;
    });
    const windowSize = Math.min(ranked.length, Math.max(count * 3, Math.min(12, ranked.length)));
    const head = ranked.slice(0, windowSize);
    const tail = ranked.slice(windowSize);
    const seedBase = `${bucket}|${currentCategory}|${heroRotationSeed + seedOffset}|${DB[0]?.slug || ''}`;
    const offset = head.length ? (hashString(seedBase) % head.length) : 0;
    const rotated = head.slice(offset).concat(head.slice(0, offset)).concat(tail);
    return rotated.slice(0, count);
  }

  function sectionPriority(post) {
    let total = heroPriority(post);
    if (post?.editorialBand === 'flagship') total += 12;
    else if (post?.editorialBand === 'high') total += 8;
    else if (post?.editorialBand === 'standard') total += 4;
    if (post?.coverageKind === 'journal') total += 7;
    if (post?.coverageKind === 'news') total += 4;
    if (post?.sourceType === 'agency') total += 2;
    return total;
  }

  function observationPriority(post) {
    let total = sectionPriority(post);
    const cat = String(post?.cat || '');
    const source = `${post?.source || ''} ${post?.sourceType || ''} ${post?.coverageKind || ''}`.toLowerCase();
    const title = `${post?.title || ''} ${post?.title_en || ''}`.toLowerCase();
    if (['Astronomia', 'Astrofísica', 'Cosmologia', 'Exoplanetas', 'Ciências da Terra'].includes(cat)) total += 12;
    if (/observ|telescope|jwst|hubble|alma|eso|nasa|esa|euclid|comet|sky|saturn|planet|moon|launch|solar|mars|space|landsat|weather/.test(source + ' ' + title)) total += 10;
    if (post?.trending) total += 3;
    return total;
  }

  function topicDescriptor(cat) {
    const map = currentLang === 'en'
      ? {
          all: 'A broad entry point into the full editorial archive.',
          'Astronomia': 'Skywatching, observatories, missions and celestial events.',
          'Cosmologia': 'The large-scale universe, dark sectors and cosmic history.',
          'Astrofísica': 'Stars, black holes, galaxies and high-energy processes.',
          'Exoplanetas': 'Planet formation, atmospheres and habitable-world searches.',
          'Física': 'Theory, experiments, quantum results and particle frontiers.',
          'Biologia': 'Biomedicine, evolution, ecology and life-science methods.',
          'Química': 'Molecules, materials, catalysis and laboratory technique.',
          'Ciências da Terra': 'Climate, oceans, geology and Earth observation.'
        }
      : {
          all: 'Uma porta ampla para entrar no arquivo editorial completo.',
          'Astronomia': 'Céu, observatórios, missões e eventos celestes.',
          'Cosmologia': 'O universo em grande escala, setores escuros e história cósmica.',
          'Astrofísica': 'Estrelas, buracos negros, galáxias e processos de alta energia.',
          'Exoplanetas': 'Formação planetária, atmosferas e busca por mundos habitáveis.',
          'Física': 'Teoria, experimentos, resultados quânticos e fronteiras de partículas.',
          'Biologia': 'Biomedicina, evolução, ecologia e métodos das ciências da vida.',
          'Química': 'Moléculas, materiais, catálise e técnica de laboratório.',
          'Ciências da Terra': 'Clima, oceanos, geologia e observação do planeta.'
        };
    return map[cat] || map.all;
  }

  function buildFrontLayout() {
    const regular = frontRegularPostsForCurrentCategory();
    const preprints = filteredPreprints();
    const heroSource = regular.length ? regular : [...preprints].sort((a, b) => postTimestamp(b) - postTimestamp(a));
    const hero = pickRotatedSet(heroSource, 3, 'hero');
    const used = new Set(hero.map(post => post.slug));

    const essentialSource = [...regular]
      .filter(post => !used.has(post.slug))
      .sort((a, b) => {
        const scoreDiff = sectionPriority(b) - sectionPriority(a);
        if (scoreDiff) return scoreDiff;
        return postTimestamp(b) - postTimestamp(a);
      });
    const essential = pickRotatedSet(essentialSource, 4, 'essential', 11);
    essential.forEach(post => used.add(post.slug));

    const watchPrimary = [...regular]
      .filter(post => !used.has(post.slug))
      .sort((a, b) => {
        const scoreDiff = observationPriority(b) - observationPriority(a);
        if (scoreDiff) return scoreDiff;
        return postTimestamp(b) - postTimestamp(a);
      });
    let watch = pickRotatedSet(watchPrimary, 4, 'watch', 23);
    if (watch.length < Math.min(2, watchPrimary.length)) {
      watch = watchPrimary.slice(0, Math.min(4, watchPrimary.length));
    }
    watch.forEach(post => used.add(post.slug));

    const latestSource = regular.filter(post => !used.has(post.slug));
    let latest = pickRotatedSet(latestSource, 6, 'latest', 17);
    if (!latest.length && regular.length) {
      latest = regular.filter(post => !hero.some(h => h.slug === post.slug)).slice(0, 6);
    }

    const trendingSource = filteredRegularPosts()
      .filter(p => p.trending)
      .sort((a, b) => {
        const freshA = isFreshFrontPost(a) ? 1 : 0;
        const freshB = isFreshFrontPost(b) ? 1 : 0;
        if (freshB !== freshA) return freshB - freshA;
        if ((b.score || 0) !== (a.score || 0)) return (b.score || 0) - (a.score || 0);
        return postTimestamp(b) - postTimestamp(a);
      });
    const trending = pickRotatedSet(trendingSource, 5, 'trending', 31);
    const rotatedPreprints = pickRotatedSet(preprints, 4, 'preprints', 47);

    rememberFrontSelection('hero', hero.map(post => post.slug), 18);
    rememberFrontSelection('essential', essential.map(post => post.slug), 30);
    rememberFrontSelection('watch', watch.map(post => post.slug), 30);
    rememberFrontSelection('latest', latest.map(post => post.slug), 36);
    rememberFrontSelection('trending', trending.map(post => post.slug), 20);

    return { hero, essential, watch, latest, trending, preprints: rotatedPreprints };
  }

  function currentFrontLayout() {
    const key = `${currentCategory}|${heroRotationSeed}|${DB.length}|${DB[0]?.slug || ''}`;
    if (!frontLayoutCache.has(key)) {
      frontLayoutCache.set(key, buildFrontLayout());
    }
    return frontLayoutCache.get(key);
  }

  function heroPostsForCurrentCategory() {
    return currentFrontLayout().hero || [];
  }

  function truncatePlainText(text = '', limit = 145) {
    const clean = String(text || '').replace(/\s+/g, ' ').trim();
    if (clean.length <= limit) return clean;
    const cut = clean.slice(0, limit);
    const lastSpace = cut.lastIndexOf(' ');
    const base = (lastSpace > Math.floor(limit * 0.55) ? cut.slice(0, lastSpace) : cut).trim();
    return `${base.replace(/[.,;:!?-]+$/, '')}…`;
  }

  function renderHero(layout = currentFrontLayout()) {
    const mount = document.getElementById('heroMount');
    if (!mount) return;
    const pool = layout.hero || heroPostsForCurrentCategory();
    if (!pool.length) { mount.innerHTML = ''; return; }

    const lead = pool[0];
    const sides = pool.slice(1, 3);
    const supplemental = dedupePostsBySlug([
      ...(layout.essential || []),
      ...(layout.watch || [])
    ]).filter(post => !pool.some(item => item.slug === post.slug)).slice(0, 2);

    const leadMeta = formatMeta(lead);
    mount.innerHTML = `
      <section class="featured-package">
        <div class="section-head">
          <div>
            <div class="section-title">${extraTr('visualLeadTitle')}</div>
            <div class="section-kicker">${extraTr('visualLeadKicker')}</div>
          </div>
        </div>
        <div class="hero-grid featured-hero-grid">
          <article class="hero-primary" onclick="openArticle('${escapeAttr(lead.slug)}')">
            <img ${imageAttrs(lead,'eager')}>
            <div class="hero-overlay"></div>
            <div class="hero-content">
              ${renderBadgeRow(lead, `<span class="meta-chip">${lead.source}</span>`)}
              <h1 class="headline-xl" style="margin-bottom:12px;">${textFor(lead,'title')}</h1>
              <p class="deck" style="max-width:700px;">${textFor(lead,'excerpt')}</p>
              <div class="meta-row" style="margin-top:18px;"><span>${leadMeta.date}</span><span>${leadMeta.read}</span><span>${tr('clickToRead')}</span></div>
            </div>
          </article>
          <div class="hero-side">
            ${sides.map(post => {
              const meta = formatMeta(post);
              return `
                <article class="hero-side-card" onclick="openArticle('${escapeAttr(post.slug)}')">
                  <img ${imageAttrs(post)}>
                  <div class="hero-overlay"></div>
                  <div class="hero-content">
                    ${renderBadgeRow(post)}
                    <h2 class="headline-lg">${textFor(post,'title')}</h2>
                    <div class="meta-row" style="margin-top:10px;"><span>${meta.date}</span><span>${meta.read}</span></div>
                  </div>
                </article>`;
            }).join('')}
          </div>
        </div>
        ${supplemental.length ? `
          <div class="featured-secondary">
            ${supplemental.map(post => visualCardMarkup(post, { compact: true })).join('')}
          </div>` : ''}
      </section>`;
  }


function visualSignalLabel(post) {
  if (post?.video?.embedUrl || post?.video?.fileUrl) return extraTr('visualLabelVideo');
  if (Array.isArray(post?.inline_images) && post.inline_images.length > 1) return extraTr('visualLabelGallery');
  return '';
}

function visualPriority(post) {
  let total = sectionPriority(post) + postFreshnessWeight(post);
  if (post?.video?.embedUrl || post?.video?.fileUrl) total += 30;
  if (Array.isArray(post?.inline_images) && post.inline_images.length) total += Math.min(12, post.inline_images.length * 3);
  if (post?.featured) total += 10;
  return total;
}

function dedupePostsBySlug(posts = []) {
  const seen = new Set();
  return posts.filter(post => {
    if (!post?.slug || seen.has(post.slug)) return false;
    seen.add(post.slug);
    return true;
  });
}

function visualCardMarkup(post, { compact = false } = {}) {
  if (!post) return '';
  const meta = formatMeta(post);
  const visualLabel = visualSignalLabel(post);
  return `
    <article class="visual-card${compact ? ' compact' : ''}" onclick="openArticle('${escapeAttr(post.slug)}')">
      <img ${imageAttrs(post)}>
      <div class="visual-card-overlay"></div>
      <div class="visual-card-body">
        <div class="visual-card-top">
          ${renderBadgeRow(post, visualLabel ? `<span class="status-chip">${visualLabel}</span>` : '')}
        </div>
        <div class="visual-card-bottom">
          <h3 class="headline-${compact ? 'md' : 'lg'}">${textFor(post,'title')}</h3>
          <div class="meta-row"><span>${prettyCategory(post.cat)}</span><span>${meta.date}</span><span>${post.source}</span></div>
        </div>
      </div>
    </article>`;
}

function renderVisualStrip(layout = currentFrontLayout()) {
  const mount = document.getElementById('visualStrip');
  if (mount) mount.innerHTML = '';
}

  function briefingStoryMarkup(post, { compact = false } = {}) {
    if (!post) return '';
    const meta = formatMeta(post);
    return `
      <button class="briefing-story${compact ? ' compact' : ''}" onclick="openArticle('${escapeAttr(post.slug)}')">
        <div class="briefing-story-kicker">${prettyCategory(post.cat)} · ${meta.date}</div>
        <div class="briefing-story-title">${textFor(post,'title')}</div>
        <div class="briefing-story-summary">${truncatePlainText(textFor(post,'excerpt'), compact ? 96 : 165)}</div>
        <div class="briefing-story-meta">${meta.read} · ${post.source}</div>
      </button>`;
  }

  function renderFrontBriefing(layout = currentFrontLayout()) {
    const mount = document.getElementById('frontBriefing');
    if (!mount) return;
    const panels = [];

    if (Array.isArray(layout?.essential) && layout.essential.length) {
      const [lead, ...rest] = layout.essential;
      panels.push(`
        <section class="briefing-panel">
          <div class="briefing-head">
            <div class="briefing-kicker">${tr('essentialTitle')}</div>
            <div class="briefing-title">${tr('essentialKicker')}</div>
          </div>
          <div class="briefing-body">
            ${briefingStoryMarkup(lead)}
            ${rest.map(post => briefingStoryMarkup(post, { compact: true })).join('')}
          </div>
        </section>`);
    }

    if (Array.isArray(layout?.watch) && layout.watch.length) {
      panels.push(`
        <section class="briefing-panel">
          <div class="briefing-head">
            <div class="briefing-kicker">${tr('monitorTitle')}</div>
            <div class="briefing-title">${tr('monitorKicker')}</div>
          </div>
          <div class="briefing-body">
            ${layout.watch.map((post, idx) => briefingStoryMarkup(post, { compact: idx > 0 })).join('')}
          </div>
        </section>`);
    }

    const topicCategories = ['all','Astronomia','Cosmologia','Astrofísica','Exoplanetas','Física','Biologia','Química','Ciências da Terra'];
    const counts = DB.reduce((acc, post) => {
      if (post?.cat) acc[post.cat] = (acc[post.cat] || 0) + 1;
      return acc;
    }, {});
    panels.push(`
      <section class="briefing-panel">
        <div class="briefing-head">
          <div class="briefing-kicker">${tr('topicShelfTitle')}</div>
          <div class="briefing-title">${tr('topicShelfKicker')}</div>
        </div>
        <div class="briefing-body">
          <div class="briefing-topic-list">
            ${topicCategories.map(cat => {
              const count = cat === 'all' ? DB.length : (counts[cat] || 0);
              const label = cat === 'all' ? tr('allCategories') : prettyCategory(cat);
              return `
                <button class="briefing-topic-card" onclick="setCategory('${escapeAttr(cat)}')">
                  <div>
                    <div class="briefing-topic-name">${label}</div>
                    <div class="briefing-topic-copy">${topicDescriptor(cat)}</div>
                  </div>
                  <span class="briefing-topic-count">${count}</span>
                </button>`;
            }).join('')}
          </div>
        </div>
      </section>`);

    mount.innerHTML = panels.join('');
  }

  // ── Home ───────────────────────────────────────────────────────────────────
  function renderHome() {
    const layout = currentFrontLayout();
    renderHero(layout);
    renderVisualStrip(layout);
    document.getElementById('latestGrid').innerHTML = layout.latest.map(post => visualCardMarkup(post, { compact: true })).join('');
    renderTopicNav('topicNav');
    const frontBriefing = document.getElementById('frontBriefing');
    if (frontBriefing) frontBriefing.innerHTML = '';

    const preprintMount = document.getElementById('preprintMount');
    if (layout.preprints.length) {
      preprintMount.innerHTML = `
        <div class="section-head preprint-section-head" style="margin-top:34px;">
          <div>
            <div class="section-title" style="color:#ffaaaa;">${tr('preprintsTitle')}</div>
            <div class="section-kicker">${tr('preprintsKicker')}</div>
          </div>
        </div>
        <div class="story-grid">${layout.preprints.map(cardMarkup).join('')}</div>`;
    } else {
      preprintMount.innerHTML = '';
    }

    renderTrending(layout.trending);
    renderLatestUpdates(layout);
    renderQuickLinks();
    renderArchivePicks(layout);
    renderSourceMix();
    renderTicker(layout);
    syncCategoryButtons();
    ensureFullArchiveLoaded();
    markNav('home');
    activatePage('home');
    updateMetaHome();
  }

  function renderLatestUpdates(layout = currentFrontLayout()) {
    const mount = document.getElementById('latestUpdates');
    if (!mount) return;
    const seen = new Set();
    const posts = [
      ...(Array.isArray(layout?.hero) ? layout.hero.slice(0, 1) : []),
      ...(Array.isArray(layout?.essential) ? layout.essential.slice(0, 2) : []),
      ...(Array.isArray(layout?.watch) ? layout.watch.slice(0, 2) : []),
      ...(Array.isArray(layout?.latest) ? layout.latest : [])
    ].filter(post => {
      if (!post || seen.has(post.slug)) return false;
      seen.add(post.slug);
      return true;
    }).slice(0, 5);

    if (!posts.length) { mount.innerHTML = ''; return; }

    mount.innerHTML = posts.map(post => {
      const meta = formatMeta(post);
      const kicker = meta.time || meta.date;
      return `
        <button class="sidebar-story-item" onclick="openArticle('${escapeAttr(post.slug)}')">
          <div class="sidebar-story-kicker">${kicker}</div>
          <div class="sidebar-story-title">${textFor(post,'title')}</div>
          <div class="sidebar-story-meta">${prettyCategory(post.cat)} · ${meta.read}</div>
        </button>`;
    }).join('');
  }

  function renderTopicNav(mountId = 'topicNav', options = {}) {
    const mount = document.getElementById(mountId);
    if (!mount) return;
    const categories = ['all','Astronomia','Cosmologia','Astrofísica','Exoplanetas','Física','Biologia','Química','Ciências da Terra'];
    const counts = DB.reduce((acc, post) => {
      if (post?.cat) acc[post.cat] = (acc[post.cat] || 0) + 1;
      return acc;
    }, {});
    const dense = !!options.dense;

    mount.innerHTML = `
      <section class="topic-map${dense ? ' dense' : ''}">
        <div class="section-head section-head--soft">
          <div>
            <div class="section-title">${extraTr('topicNavTitle')}</div>
            <div class="section-kicker">${extraTr('topicNavKicker')}</div>
          </div>
        </div>
        <div class="topic-map-grid">
          ${categories.map(cat => {
            const isAll = cat === 'all';
            const count = isAll ? DB.length : (counts[cat] || 0);
            const label = isAll ? tr('allCategories') : prettyCategory(cat);
            const active = currentCategory === cat ? ' on' : '';
            const descriptor = dense ? '' : `<span class="topic-map-copy">${sanitizeDisplayText(topicDescriptor(cat))}</span>`;
            return `
              <button class="topic-map-card${active}" onclick="setCategory('${escapeAttr(cat)}')">
                <span class="topic-map-top">
                  <span class="topic-map-name">${label}</span>
                  <span class="topic-count">${count}</span>
                </span>
                ${descriptor}
              </button>`;
          }).join('')}
        </div>
      </section>`;
  }

  function focusSearch() {
    goHome();
    const input = document.getElementById('searchInput');
    if (input) {
      input.focus();
      input.select();
      input.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function renderQuickLinks() {
    const mount = document.getElementById('quickLinks');
    if (!mount) return;
    mount.innerHTML = `
      <button class="sidebar-action" onclick="openPage('archive')">${tr('quickArchive')}</button>
      <a class="sidebar-action" href="feed.xml" target="_blank" rel="noopener">${tr('quickRSS')}</a>
      <button class="sidebar-action" onclick="openPage('standards')">${tr('quickStandards')}</button>
      <button class="sidebar-action" onclick="focusSearch()">${tr('quickSearch')}</button>`;
  }

  function renderArchivePicks(layout = currentFrontLayout()) {
    const mount = document.getElementById('archivePicks');
    if (!mount) return;
    const blocked = new Set([
      ...(layout?.hero || []),
      ...(layout?.essential || []),
      ...(layout?.watch || []),
      ...(layout?.latest || []),
      ...(layout?.trending || []),
      ...(layout?.preprints || [])
    ].filter(Boolean).map(post => post.slug));

    const picks = DB
      .filter(post => !post.isPreprint && !blocked.has(post.slug) && (currentCategory === 'all' || post.cat === currentCategory))
      .sort((a, b) => ((b.score || 0) - (a.score || 0)) || (postTimestamp(b) - postTimestamp(a)))
      ;

    mount.innerHTML = picks.map(post => {
      const meta = formatMeta(post);
      return `
        <button class="sidebar-story-item" onclick="openArticle('${escapeAttr(post.slug)}')">
          <div class="sidebar-story-kicker">${prettyCategory(post.cat)}</div>
          <div class="sidebar-story-title">${textFor(post,'title')}</div>
          <div class="sidebar-story-meta">${meta.date} · ${meta.read}</div>
        </button>`;
    }).join('');
  }

  // ── Trending ───────────────────────────────────────────────────────────────
  function renderTrending(postsOverride = null) {
    const mount = document.getElementById('trendingList');
    const posts = Array.isArray(postsOverride) ? postsOverride : currentFrontLayout().trending;
    mount.innerHTML = posts.map((post, i) => `
      <button class="trend-item" onclick="openArticle('${escapeAttr(post.slug)}')">
        <div class="trend-num">${i+1}</div>
        <div>
          <div class="trend-title">${textFor(post,'title')}</div>
          <div class="trend-meta">${prettyCategory(post.cat)} · ${formatMeta(post).read}</div>
        </div>
      </button>`).join('');
  }

  // ── Source mix ─────────────────────────────────────────────────────────────
  function renderSourceMix() {
    const mount = document.getElementById('sourceMix');
    if (!mount) return;
    const visible = currentCategory === 'all' ? DB : DB.filter(p => p?.cat === currentCategory);
    const kindFor = (p) => p.coverageKind || p.sourceType || 'agency';
    const counts = visible.reduce((acc,p) => { const key = kindFor(p); acc[key] = (acc[key]||0)+1; return acc; }, {});
    const rows = [
      ['agency',   currentLang==='en'?'Institutional':'Institucional',      averageVisibleScore('evidence', p=>kindFor(p)==='agency' && (currentCategory === 'all' || p?.cat === currentCategory))],
      ['news',     currentLang==='en'?'Science reporting':'Jornalismo científico', averageVisibleScore('relevance', p=>kindFor(p)==='news' && (currentCategory === 'all' || p?.cat === currentCategory))],
      ['journal',  currentLang==='en'?'Peer-reviewed':'Revisado por pares', averageVisibleScore('evidence', p=>kindFor(p)==='journal' && (currentCategory === 'all' || p?.cat === currentCategory))],
      ['preprint', currentLang==='en'?'Preprints':'Preprints',              averageVisibleScore('overall',   p=>kindFor(p)==='preprint' && (currentCategory === 'all' || p?.cat === currentCategory))]
    ];
    mount.innerHTML = rows.map(([key,label,metric]) => {
      const n = counts[key]||0;
      return `
        <div class="metric-row">
          <div class="metric-badge">${n}</div>
          <div>
            <div class="metric-label">${label}</div>
            <div class="metric-sub">${tr('sourceMixLine')}</div>
            <div class="score-bar-wrap"><div class="score-bar" style="width:${metric}%"></div></div>
          </div>
        </div>`;
    }).join('');
  }

  // ── Ticker ─────────────────────────────────────────────────────────────────
  function renderTicker(layout = currentFrontLayout()) {
    const mount = document.getElementById('tickerTrack');
    const source = [...(layout.hero || []), ...(layout.essential || []), ...(layout.watch || []), ...(layout.latest || []), ...(layout.preprints || [])].filter(Boolean);
    const items = source.slice(0,8).map(p => textFor(p,'title')).filter(Boolean);
    const loop = items.length ? [...items, ...items] : [];
    mount.innerHTML = loop.map(item => `<span class="ticker-item">${item}</span>`).join('');
  }

  // ── Archive ────────────────────────────────────────────────────────────────
  function renderArchive() {
    const posts = currentCategory === 'all' ? DB : DB.filter(p => p.cat === currentCategory);
    const hero = posts.slice(0, 4);
    const remaining = posts.slice(4);
    const archiveSummary = document.getElementById('archiveSummary');
    const archiveHighlights = document.getElementById('archiveHighlights');
    const archiveStatus = document.getElementById('archiveStatus');
    const listMount = document.getElementById('archiveList');

    document.getElementById('archiveKicker').textContent = currentLang === 'en'
      ? `${posts.length} stories available in the selected area. The archive preserves continuity instead of forcing everything through the homepage.`
      : `${posts.length} matérias disponíveis na área selecionada. O arquivo preserva continuidade em vez de empurrar tudo para a homepage.`;

    if (archiveSummary) {
      const topicCount = new Set(DB.map(post => post?.cat).filter(Boolean)).size;
      archiveSummary.innerHTML = `
        <div class="archive-stat"><span class="archive-stat-num">${posts.length}</span><span class="archive-stat-label">${extraTr('archiveStatsStories')}</span></div>
        <div class="archive-stat"><span class="archive-stat-num">${topicCount}</span><span class="archive-stat-label">${extraTr('archiveStatsTopics')}</span></div>
        <div class="archive-stat"><span class="archive-stat-num">2</span><span class="archive-stat-label">${extraTr('archiveStatsLanguages')}</span></div>`;
    }

    if (archiveHighlights) {
      archiveHighlights.innerHTML = hero.length
        ? hero.map((post, idx) => visualCardMarkup(post, { compact: idx > 0 })).join('')
        : `<div class="archive-empty">${extraTr('archiveNoItems')}</div>`;
    }

    if (listMount) listMount.innerHTML = remaining.length ? remaining.map(compactMarkup).join('') : '';

    if (archiveStatus) archiveStatus.textContent = fullArchiveLoaded ? extraTr('archiveLoaded') : extraTr('archiveLoading');

    renderTopicNav('archiveTopicNav', { dense: true });

    ensureFullArchiveLoaded().then(() => {
      if (currentPage !== 'archive') return;
      const activePosts = currentCategory === 'all' ? DB : DB.filter(p => p.cat === currentCategory);
      const activeHero = activePosts.slice(0, 4);
      if (archiveSummary) {
        const topicCount = new Set(DB.map(post => post?.cat).filter(Boolean)).size;
        archiveSummary.innerHTML = `
          <div class="archive-stat"><span class="archive-stat-num">${activePosts.length}</span><span class="archive-stat-label">${extraTr('archiveStatsStories')}</span></div>
          <div class="archive-stat"><span class="archive-stat-num">${topicCount}</span><span class="archive-stat-label">${extraTr('archiveStatsTopics')}</span></div>
          <div class="archive-stat"><span class="archive-stat-num">2</span><span class="archive-stat-label">${extraTr('archiveStatsLanguages')}</span></div>`;
      }
      if (archiveHighlights) archiveHighlights.innerHTML = activeHero.length
        ? activeHero.map((post, idx) => visualCardMarkup(post, { compact: idx > 0 })).join('')
        : `<div class="archive-empty">${extraTr('archiveNoItems')}</div>`;
      if (listMount) listMount.innerHTML = activePosts.slice(4).map(compactMarkup).join('');
      if (archiveStatus) archiveStatus.textContent = extraTr('archiveLoaded');
      renderTopicNav('archiveTopicNav', { dense: true });
    });

    markNav('archive');
    activatePage('archive');
    updateMetaStatic('archive');
  }

  // ── About / Standards ──────────────────────────────────────────────────────
  function renderAbout() {
    document.getElementById('pageAbout').innerHTML = `
      <div class="institution-shell">
        ${contextualNavMarkup('about')}
        <div class="about-grid">
          <div class="section-title">${extraTr('aboutEyebrow')}</div>
          <h1 class="headline-xl" style="max-width:920px;">${extraTr('aboutHeadline')}</h1>
          <p class="deck">${extraTr('aboutIntro2')}</p>
          <div class="institution-cards">
            ${EXTRA_UI[currentLang].aboutCards.map(card => `
              <article class="institution-card">
                <h3>${card.title}</h3>
                <p>${card.body}</p>
              </article>`).join('')}
          </div>
          <div class="institution-split">
            <div>
              <h2 class="institution-subtitle">${tr('aboutPageTitle')}</h2>
              <p class="deck">${tr('aboutIntro')}</p>
              <p class="deck">${tr('aboutBody')}</p>
            </div>
            <div class="institution-note">
              <h3>${extraTr('aboutChecklistTitle')}</h3>
              ${renderChecklist(EXTRA_UI[currentLang].aboutChecklist)}
            </div>
          </div>
        </div>
      </div>`;
    markNav('about'); activatePage('about'); updateMetaStatic('about');
  }

  function renderStandards() {
    document.getElementById('pageStandards').innerHTML = `
      <div class="institution-shell">
        ${contextualNavMarkup('standards')}
        <div class="about-grid">
          <div class="section-title">${extraTr('standardsEyebrow')}</div>
          <h1 class="headline-xl" style="max-width:960px;">${extraTr('standardsHeadline')}</h1>
          <p class="deck">${extraTr('standardsIntro2')}</p>
          <div class="standards-grid">
            ${EXTRA_UI[currentLang].standardsCards2.map(card => `
              <article class="standards-card">
                <h3>${card.title}</h3>
                <p>${card.body}</p>
              </article>`).join('')}
          </div>
          <div class="institution-split">
            <div>
              <h2 class="institution-subtitle">${tr('standardsPageTitle')}</h2>
              <p class="deck">${tr('standardsIntro')}</p>
            </div>
            <div class="institution-note">
              <h3>${extraTr('standardsWorkflowTitle')}</h3>
              ${renderChecklist(EXTRA_UI[currentLang].standardsWorkflow)}
            </div>
          </div>
        </div>
      </div>`;
    markNav('standards'); activatePage('standards'); updateMetaStatic('standards');
  }

  // ── Article helpers ────────────────────────────────────────────────────────
  const ARTICLE_BODY_NOISE_PATTERNS = [
    /^artigo \d+/i, /^missoes pesquisar/i, /^explorar pesquisa/i, /^observatorio da terra/i,
    /^terra observatorio da terra/i, /^research news and events/i, /^missions explore/i,
    /^image of the day/i, /^earth observatory/i, /^the post .* appeared first on/i,
    /^a atualização é resultado de um extenso período/i, /^o campo vinha se construindo em direção a momentos como este/i,
    /^para situar o resultado no contexto/i, /^o anúncio abre um caminho produtivo/i,
    /^observações independentes/i, /^a astronomia avança acumulando/i, /^a ciência progride/i,
    /^the update follows an extended period/i, /^astronomy advances by accumulating/i,
    /^to place the result in context/i, /^the announcement opens a productive path/i,
    /^independent observations at other wavelengths/i,
    /explorar pesquisa/i, /boletins informativos/i, /mídia social/i, /multimídia imagens multimídia/i,
    /lista de missões/i, /observatório da terra imagem do dia/i, /topics of the eo explorer/i,
    /audio podcasts and blogs/i, /social media/i, /multimedia images/i
  ];

  function stripHtml(htmlText = '') {
    const div = document.createElement('div');
    div.innerHTML = decodeEntitiesLoose(String(htmlText || ''));
    return sanitizeDisplayText((div.textContent || div.innerText || '').replace(/\s+/g, ' ').trim());
  }

  function isArticleNoise(text = '') {
    const cleaned = stripHtml(text);
    return !cleaned || cleaned.length < 18 || ARTICLE_BODY_NOISE_PATTERNS.some(rx => rx.test(cleaned));
  }

  function uniqueTextItems(items = []) {
    const out = [];
    const seen = new Set();
    items.forEach(item => {
      const cleaned = stripHtml(item);
      if (!cleaned) return;
      const key = normalizarTexto(cleaned).replace(/[^a-z0-9]+/g, '');
      if (!key || seen.has(key)) return;
      for (const existing of out) {
        const ex = normalizarTexto(existing).replace(/[^a-z0-9]+/g, '');
        if (key === ex || key.includes(ex) || ex.includes(key)) return;
      }
      seen.add(key);
      out.push(cleaned);
    });
    return out;
  }

  function cleanHighlightLine(line = '') {
    const cleaned = stripHtml(String(line)
      .replace(/^(Ponto central|Dado-chave|Origem institucional|Central point|Key datum|Institutional origin)\s*:\s*/i, ''));
    if (!cleaned || cleaned.length < 30) return '';
    if (/distinguir anúncio de evidência/i.test(cleaned) || /distinguish announcement from evidence/i.test(cleaned)) return '';
    if (/^\d{2}\.\d{4,9}\//.test(cleaned)) return '';
    return cleaned;
  }

  function extractArticleParagraphs(post) {
    const raw = currentLang === 'en' ? (post.body_en || post.body || '') : (post.body_pt || post.body || '');
    const parser = new DOMParser();
    const doc = parser.parseFromString(`<div>${raw}</div>`, 'text/html');
    const paragraphs = [...doc.querySelectorAll('p')]
      .filter(p => !p.classList.contains('art-source'))
      .map(p => stripHtml(p.innerHTML))
      .filter(text => !isArticleNoise(text));
    return uniqueTextItems(paragraphs);
  }

  function buildArticleSummary(post) {
    return '';
  }

  function inlineImagesFor(post) {
    const raw = Array.isArray(post?.inline_images) ? post.inline_images : [];
    const seen = new Set();
    return raw
      .map(item => item || {})
      .map(item => {
        const src = String(item.src || '').trim();
        const caption = currentLang === 'en'
          ? sanitizeDisplayText(String(item.caption_en || item.caption || '').trim())
          : sanitizeDisplayText(String(item.caption_pt || item.caption || '').trim());
        const alt = currentLang === 'en'
          ? sanitizeDisplayText(String(item.alt_en || item.alt || caption || textFor(post, 'title')).trim())
          : sanitizeDisplayText(String(item.alt_pt || item.alt || caption || textFor(post, 'title')).trim());
        return { src, caption, alt };
      })
      .filter(item => item.src)
      .filter(item => {
        const key = item.src.toLowerCase();
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
  }

  function articleInlineFigureMarkup(image, post) {
    if (!image || !image.src) return '';
    const caption = stripHtml(image.caption || '');
    const alt = stripHtml(image.alt || caption || textFor(post, 'title'));
    return `
      <figure class="article-inline-figure">
        <img src="${escapeAttr(image.src)}" alt="${escapeAttr(alt)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.closest('figure').style.display='none'">
        ${caption ? `<figcaption class="article-inline-caption">${caption}</figcaption>` : ''}
      </figure>`;
  }

  function extractKnownVideoEmbedFromHtml(html = '') {
    const source = String(html || '').trim();
    if (!source) return '';
    const parser = new DOMParser();
    const doc = parser.parseFromString(`<div>${source}</div>`, 'text/html');

    const iframeSrc = doc.querySelector('iframe[src]')?.getAttribute('src') || '';
    if (iframeSrc) return iframeSrc;

    const selectors = [
      'a[href*="youtu.be/"]',
      'a[href*="youtube.com/watch"]',
      'a[href*="youtube.com/embed/"]',
      'a[href*="youtube.com/shorts/"]',
      'a[href*="vimeo.com/"]',
      'video source[src]',
      'video[src]'
    ];

    for (const selector of selectors) {
      const found = doc.querySelector(selector);
      if (!found) continue;
      const attr = found.getAttribute('href') || found.getAttribute('src') || '';
      if (attr) return attr;
    }

    return '';
  }

  function normalizeYouTubeEmbedUrl(url = '') {
    const value = String(url || '').trim();
    if (!value) return '';

    const buildEmbed = id => {
      const cleanId = String(id || '').trim();
      if (!/^[A-Za-z0-9_-]{6,}$/.test(cleanId)) return '';
      return `https://www.youtube-nocookie.com/embed/${cleanId}?rel=0&modestbranding=1`;
    };

    try {
      const parsed = new URL(value, location.href);
      const host = parsed.hostname.replace(/^www\./i, '').toLowerCase();
      const path = parsed.pathname || '';
      let id = '';

      if (host === 'youtu.be') {
        id = path.split('/').filter(Boolean)[0] || '';
      } else if (host.endsWith('youtube.com') || host.endsWith('youtube-nocookie.com')) {
        if (/^\/embed\//i.test(path)) {
          id = path.split('/').filter(Boolean)[1] || '';
        } else if (/^\/watch$/i.test(path)) {
          id = parsed.searchParams.get('v') || '';
        } else if (/^\/(shorts|live)\//i.test(path)) {
          id = path.split('/').filter(Boolean)[1] || '';
        }
      }

      const normalized = buildEmbed(id);
      if (normalized) return normalized;
    } catch (e) {}

    const match = value.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/|live\/)|youtu\.be\/)([A-Za-z0-9_-]{6,})/i);
    return match ? buildEmbed(match[1]) : '';
  }

  function normalizeVimeoEmbedUrl(url = '') {
    const value = String(url || '').trim();
    if (!value) return '';
    try {
      const parsed = new URL(value, location.href);
      const host = parsed.hostname.replace(/^www\./i, '').toLowerCase();
      if (!host.endsWith('vimeo.com') && !host.endsWith('player.vimeo.com')) return '';
      const parts = parsed.pathname.split('/').filter(Boolean);
      const id = parts.find(part => /^\d{6,}$/.test(part)) || '';
      return id ? `https://player.vimeo.com/video/${id}` : '';
    } catch (e) {
      const match = value.match(/vimeo\.com\/(?:video\/)?(\d{6,})/i);
      return match ? `https://player.vimeo.com/video/${match[1]}` : '';
    }
  }

  function normalizeVideoEmbedUrl(url = '', platform = '') {
    const value = String(url || '').trim();
    const provider = String(platform || '').trim().toLowerCase();
    if (!value) return '';

    if (provider.includes('youtube') || /youtu(?:\.be|be\.com)/i.test(value)) {
      return normalizeYouTubeEmbedUrl(value);
    }
    if (provider.includes('vimeo') || /vimeo\.com/i.test(value)) {
      return normalizeVimeoEmbedUrl(value);
    }
    if (/^https?:\/\//i.test(value)) return value;
    return '';
  }

  function inferVideoDataFromPost(post) {
    const rawVideo = post && post.video && typeof post.video === 'object' ? post.video : {};
    const bodyHtml = currentLang === 'en'
      ? String(post?.body_en || post?.body || '')
      : String(post?.body_pt || post?.body || '');

    const candidates = [
      rawVideo.embedUrl,
      rawVideo.url,
      rawVideo.src,
      rawVideo.watchUrl,
      rawVideo.watch_url,
      rawVideo.youtubeUrl,
      rawVideo.youtube_url,
      rawVideo.videoUrl,
      rawVideo.video_url,
      rawVideo.iframe,
      rawVideo.embed,
      post?.videoUrl,
      post?.video_url,
      post?.youtubeUrl,
      post?.youtube_url,
      post?.embedUrl,
      post?.embed_url,
      extractKnownVideoEmbedFromHtml(bodyHtml)
    ].map(value => String(value || '').trim()).filter(Boolean);

    const platformHint = [
      rawVideo.platform,
      post?.videoPlatform,
      post?.video_platform
    ].map(value => String(value || '').trim()).find(Boolean) || '';

    const embedUrl = candidates
      .map(url => normalizeVideoEmbedUrl(url, platformHint))
      .find(Boolean) || '';

    const fileUrl = [
      rawVideo.fileUrl,
      rawVideo.file_url,
      rawVideo.src,
      post?.fileUrl,
      post?.file_url
    ].map(value => String(value || '').trim())
     .find(url => /^https?:\/\//i.test(url) && /\.(mp4|webm|ogg)(?:$|[?#])/i.test(url)) || '';

    return {
      kind: fileUrl ? 'file' : (embedUrl ? 'embed' : ''),
      platform: platformHint || (embedUrl.includes('youtube') ? 'youtube' : (embedUrl.includes('vimeo') ? 'vimeo' : '')),
      embedUrl,
      fileUrl
    };
  }

  function articleVideoFor(post) {
    const raw = post && post.video && typeof post.video === 'object' ? post.video : {};
    const inferred = inferVideoDataFromPost(post);
    if (!inferred.embedUrl && !inferred.fileUrl) return null;

    const title = currentLang === 'en'
      ? sanitizeDisplayText(String(raw.title_en || raw.title || post?.title_en || post?.title || '').trim())
      : sanitizeDisplayText(String(raw.title_pt || raw.title || post?.title_pt || post?.title || '').trim());
    const caption = currentLang === 'en'
      ? sanitizeDisplayText(String(raw.caption_en || raw.caption || '').trim())
      : sanitizeDisplayText(String(raw.caption_pt || raw.caption || '').trim());

    return {
      kind: inferred.kind,
      platform: inferred.platform,
      embedUrl: inferred.embedUrl,
      fileUrl: inferred.fileUrl,
      poster: String(raw.poster || primaryImage(post) || '').trim(),
      title,
      caption
    };
  }

  function articleVideoMarkup(post) {
    const video = articleVideoFor(post);
    if (!video) return '';
    const caption = stripHtml(video.caption || video.title || '');
    const title = stripHtml(video.title || textFor(post, 'title'));
    if (video.kind === 'embed' && video.embedUrl) {
      return `
        <figure class="article-video">
          <div class="article-video-frame">
            <iframe src="${escapeAttr(video.embedUrl)}"
              title="${escapeAttr(title)}"
              loading="lazy"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
              allowfullscreen
              referrerpolicy="strict-origin-when-cross-origin"></iframe>
          </div>
          ${caption ? `<figcaption class="article-video-caption">${caption}</figcaption>` : ''}
        </figure>`;
    }
    if (video.kind === 'file' && video.fileUrl) {
      return `
        <figure class="article-video">
          <div class="article-video-frame">
            <video controls preload="metadata" playsinline ${video.poster ? `poster="${escapeAttr(video.poster)}"` : ''} onerror="this.closest('figure').style.display='none'">
              <source src="${escapeAttr(video.fileUrl)}">
            </video>
          </div>
          ${caption ? `<figcaption class="article-video-caption">${caption}</figcaption>` : ''}
        </figure>`;
    }
    return '';
  }

  function articleAudioFor(post) {
    const raw = post && post.audio && typeof post.audio === 'object' ? post.audio : null;
    if (!raw) return null;
    const title = currentLang === 'en'
      ? sanitizeDisplayText(String(raw.title_en || raw.title || '').trim())
      : sanitizeDisplayText(String(raw.title_pt || raw.title || '').trim());
    const caption = currentLang === 'en'
      ? sanitizeDisplayText(String(raw.caption_en || raw.caption || '').trim())
      : sanitizeDisplayText(String(raw.caption_pt || raw.caption || '').trim());
    return {
      kind: String(raw.kind || '').trim(),
      platform: String(raw.platform || '').trim(),
      embedUrl: String(raw.embedUrl || '').trim(),
      fileUrl: String(raw.fileUrl || '').trim(),
      title,
      caption
    };
  }

  function articleAudioMarkup(post) {
    const audio = articleAudioFor(post);
    if (!audio) return '';
    const caption = stripHtml(audio.caption || audio.title || '');
    const title = stripHtml(audio.title || textFor(post, 'title'));
    if (audio.kind === 'embed' && audio.embedUrl) {
      return `
        <figure class="article-audio">
          <div class="article-audio-frame">
            <iframe src="${escapeAttr(audio.embedUrl)}"
              title="${escapeAttr(title)}"
              loading="lazy"
              allow="autoplay; clipboard-write; encrypted-media; fullscreen"
              referrerpolicy="strict-origin-when-cross-origin"></iframe>
          </div>
          ${caption ? `<figcaption class="article-audio-caption">${caption}</figcaption>` : ''}
        </figure>`;
    }
    if (audio.kind === 'file' && audio.fileUrl) {
      return `
        <figure class="article-audio">
          <div class="article-audio-frame">
            <audio controls preload="metadata">
              <source src="${escapeAttr(audio.fileUrl)}">
            </audio>
          </div>
          ${caption ? `<figcaption class="article-audio-caption">${caption}</figcaption>` : ''}
        </figure>`;
    }
    return '';
  }

  function buildArticleBody(post) {
    const ledeLike = uniqueTextItems([stripHtml(textFor(post, 'sub')), stripHtml(textFor(post, 'excerpt'))]);
    const bodyParagraphs = extractArticleParagraphs(post).filter(text => {
      const key = normalizarTexto(text).replace(/[^a-z0-9]+/g, '');
      return !ledeLike.some(item => {
        const other = normalizarTexto(item).replace(/[^a-z0-9]+/g, '');
        return key === other;
      });
    });
    const paragraphs = uniqueTextItems(bodyParagraphs);
    const intro = uniqueTextItems([stripHtml(textFor(post, 'sub')), stripHtml(textFor(post, 'excerpt'))]);
    const finalParagraphs = paragraphs.length ? uniqueTextItems([...intro, ...paragraphs]) : intro;
    const inlineImages = inlineImagesFor(post);
    // We no longer insert the video at this point because it is rendered once
    // in the article cover area. Avoid duplicating video players in the body.
    const audioMarkup = articleAudioMarkup(post);

    if (!finalParagraphs.length && !inlineImages.length && !audioMarkup) return '';

    const blocks = [];
    // Only insert audio here; video is handled elsewhere.
    if (audioMarkup) blocks.push(audioMarkup);
    let nextImageIndex = 0;
    finalParagraphs.forEach((text, idx) => {
      blocks.push(`<p>${text}</p>`);
      if (!inlineImages.length || !inlineImages[nextImageIndex]) return;

      const isFirstParagraph = idx === 0;
      const isEverySecondParagraph = (idx + 1) % 2 === 0;
      const isLastParagraph = idx === finalParagraphs.length - 1;
      if (isFirstParagraph || isEverySecondParagraph || isLastParagraph) {
        blocks.push(articleInlineFigureMarkup(inlineImages[nextImageIndex], post));
        nextImageIndex += 1;
      }
    });

    if (!finalParagraphs.length) {
      inlineImages.forEach(image => blocks.push(articleInlineFigureMarkup(image, post)));
    } else {
      while (inlineImages[nextImageIndex]) {
        blocks.push(articleInlineFigureMarkup(inlineImages[nextImageIndex], post));
        nextImageIndex += 1;
      }
    }

    return blocks.join('');
  }

  function engagementBoxMarkup() {
    return `
      <section class="engagement-box">
        <div class="engagement-head">
          <div class="engagement-title">${currentLang === 'en' ? 'Reactions and comments' : 'Reações e comentários'}</div>
        </div>
        <div id="articleDiscussionMount" class="engagement-mount"></div>
      </section>`;
  }

  function getGiscusConfig() {
    return Object.assign({
      enabled: false,
      repo: 'marambaiajunior/cosmos-week',
      repoId: '',
      category: 'Comentários',
      categoryId: '',
      mapping: 'specific',
      strict: '1',
      reactionsEnabled: '1',
      emitMetadata: '0',
      inputPosition: 'top',
      theme: 'dark_dimmed'
    }, window.COSMOS_GISCUS || {});
  }

  function mountArticleDiscussion(post) {
    const mount = document.getElementById('articleDiscussionMount');
    if (!mount) return;
    mount.innerHTML = '';
    const cfg = getGiscusConfig();
    const ready = !!(cfg.enabled && cfg.repo && cfg.repoId && cfg.category && cfg.categoryId);
    if (!ready) {
      mount.innerHTML = `<div class="engagement-disabled">${currentLang === 'en'
        ? 'Public reactions and comments are wired for activation. To turn them on, fill the repository identifiers in giscus-config.js.'
        : 'Reações públicas e comentários já estão preparados para ativação.'}</div>`;
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://giscus.app/client.js';
    script.async = true;
    script.crossOrigin = 'anonymous';
    script.setAttribute('data-repo', cfg.repo);
    script.setAttribute('data-repo-id', cfg.repoId);
    script.setAttribute('data-category', cfg.category);
    script.setAttribute('data-category-id', cfg.categoryId);
    script.setAttribute('data-mapping', cfg.mapping || 'specific');
    script.setAttribute('data-term', post.slug);
    script.setAttribute('data-strict', String(cfg.strict ?? '1'));
    script.setAttribute('data-reactions-enabled', String(cfg.reactionsEnabled ?? '1'));
    script.setAttribute('data-emit-metadata', String(cfg.emitMetadata ?? '0'));
    script.setAttribute('data-input-position', cfg.inputPosition || 'top');
    script.setAttribute('data-theme', cfg.theme || 'dark_dimmed');
    script.setAttribute('data-lang', currentLang === 'en' ? 'en' : 'pt');
    script.setAttribute('data-loading', 'lazy');
    mount.appendChild(script);
  }

  // ── Article ────────────────────────────────────────────────────────────────
  function renderArticle(slug) {
    const post = DB.find(item => item.slug === slug);
    if (!post) { goHome(); return; }
    currentArticleSlug = slug;
    const meta = formatMeta(post);
    const highlights = listFor(post,'highlights');
    const related = DB.filter(item => item.slug!==post.slug && item.cat===post.cat).slice(0,3);
    const keywords = keywordListFor(post);
    const sb = post.scoreBreakdown || {};
    const mount = document.getElementById('pageArticle');
    mount.innerHTML = `
      <div class="breadcrumbs">
        <button onclick="goHome()">${tr('home')}</button>
        <span>›</span>
        <button onclick="setCategory('${escapeAttr(post.cat)}');goHome();">${prettyCategory(post.cat)}</button>
        <span>›</span>
        <span>${post.source}</span>
      </div>

      <article class="article-shell">
        <div class="article-cover">
          <img ${imageAttrs(post,'eager')}>
          <div class="article-cover-content">
            ${renderBadgeRow(post, `<span class="meta-chip">${post.source}</span>`)}
            <h1 class="headline-xl" style="margin-bottom:14px;">${textFor(post,'title')}</h1>
            <div class="meta-row" style="margin-top:16px;">
              <span>${tr('newsroom')}</span>
              <span>${meta.date}</span>
              <span>${meta.time}</span>
              <span>${meta.read}</span>
            </div>
          </div>
        </div>

        <div class="article-layout">
          <div>
            ${articleVideoMarkup(post)}
            ${buildArticleSummary(post)}
            <div class="article-body">${buildArticleBody(post)}</div>

            <!-- AD SLOT: In-article (após o corpo do texto, antes dos botões de share)
                 Para ativar: remova display:none do CSS .ad-slot e descomente o <ins> abaixo. -->
            <div class="ad-slot ad-slot--in-article" aria-hidden="true">
              <!--
              <ins class="adsbygoogle"
                style="display:block; text-align:center;"
                data-ad-layout="in-article"
                data-ad-format="fluid"
                data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
                data-ad-slot="XXXXXXXXXX"></ins>
              <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
              -->
            </div>

            <div class="share-box" style="margin-top:32px; overflow:visible;">
              <div class="box-head">${tr('articleShare')}</div>
              <div class="box-body">
                <button class="ghost-btn" type="button" onclick="copyArticleLink()">${tr('copyLink')}</button>
                <button class="ghost-btn" type="button" onclick="shareCurrentArticle()" style="gap:6px;">
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" style="width:14px;height:14px;flex-shrink:0;">
                    <path fill="currentColor" d="M18 16a3 3 0 0 0-2.39 1.2l-6.94-3.47a3.12 3.12 0 0 0 0-1.46l6.94-3.47A3 3 0 1 0 15 7a3.12 3.12 0 0 0 .06.6L8.12 11.07a3 3 0 1 0 0 1.86l6.94 3.47A3 3 0 1 0 18 16Z"></path>
                  </svg>
                  <span>${tr('shareNow')}</span>
                </button>
                <a class="ghost-btn" href="${escapeAttr(post.srcUrl)}" target="_blank" rel="noopener">${tr('articleReadOriginal')}</a>
              </div>
            </div>
            ${related.length ? `
              <div class="section-head" style="margin-top:38px;margin-bottom:18px;">
                <div class="section-title">${tr('relatedTitle')}</div>
              </div>
              <div class="story-grid">${related.map(cardMarkup).join('')}</div>` : ''}
            ${engagementBoxMarkup()}
          </div>

          <aside class="sidebar">
            ${post.isPreprint ? `
              <div class="warning-box">
                <div class="box-head">${tr('warningTitle')}</div>
                <div class="warning-body">${tr('preprintWarning')}</div>
              </div>` : ''}

            <div class="highlights-box">
              <div class="box-head">${tr('articleHighlights')}</div>
              <div class="box-body">
                <ul class="highlights-list">${highlights.map(item=>`<li>${item}</li>`).join('')}</ul>
                ${keywords.length ? `<div class="keyword-row">${keywords.slice(0,5).map(k=>`<span class="kw-chip">${k}</span>`).join('')}</div>` : ''}
              </div>
            </div>

            <div class="source-box">
              <div class="box-head">${tr('articleSource')}</div>
              <div class="box-body">
                <div style="font-size:13.5px;font-weight:600;color:var(--txt);">${post.source}</div>
                <div class="source-domain">${sourceDomainFor(post)}</div>
                <div class="source-note">${sanitizeDisplayText(currentLang==='en'?(post.sourceNote_en||post.sourceNote):(post.sourceNote_pt||post.sourceNote))}</div>
                <div style="margin-top:14px;">
                  <a href="${escapeAttr(post.srcUrl)}" target="_blank" rel="noopener" style="color:var(--accent-2);font-size:13.5px;text-decoration:underline;text-decoration-color:rgba(127,179,255,.3);text-underline-offset:3px;">${tr('articleReadOriginal')}</a>
                </div>
              </div>
            </div>

            <div class="score-box">
              <div class="box-head">${tr('scoreLabel')}</div>
              <div class="box-body">
                <div>
                  <span class="score-overall">${post.score||0}</span>
                  <span class="score-label">/100</span>
                </div>
                ${[
                  ['evidence',      tr('evidenceLabel'),    sb.evidence||0],
                  ['relevance',     tr('relatedTitle').split(' ')[0], sb.relevance||0],
                  ['novelty',       tr('noveltyLabel'),    sb.novelty||0],
                  ['accessibility', tr('accessLabel'),  sb.accessibility||0]
                ].map(([,label,val]) => `
                  <div>
                    <div class="score-dim">
                      <span class="score-dim-name">${label}</span>
                      <span class="score-dim-val">${val}</span>
                    </div>
                    <div class="mini-bar-wrap"><div class="mini-bar" style="width:${val}%"></div></div>
                  </div>`).join('')}
              </div>
            </div>
          </aside>
        </div>
      </article>`;
    mountArticleDiscussion(post);
    markNav(''); activatePage('article'); updateMetaArticle(post);
  }

  // ── Search ─────────────────────────────────────────────────────────────────
  function renderSearch(query) {
    const q = normalizarTexto(query);
    const results = DB.filter(post => normalizarTexto([
      post.title, post.title_pt, post.title_en, post.excerpt, post.excerpt_pt, post.excerpt_en,
      post.body, post.body_pt, post.body_en, post.source, post.cat
    ].join(' ')).includes(q));
    document.getElementById('searchInfo').textContent = `${results.length} ${tr('resultsFor')} "${query}"`;
    document.getElementById('searchGrid').innerHTML = results.map(cardMarkup).join('');
    const empty = document.getElementById('searchEmpty');
    if (!results.length) {
      empty.classList.remove('hidden');
      empty.innerHTML = `<p>${tr('noSearch')}</p><p style="margin-top:8px;">${tr('trySearch')}</p>`;
    } else { empty.classList.add('hidden'); }
    markNav(''); activatePage('search'); updateMetaStatic('search');
  }

  // ── Navigation helpers ─────────────────────────────────────────────────────
  function activatePage(page) {
    currentPage = page;
    document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
    const map = { home:'pageHome', article:'pageArticle', archive:'pageArchive', about:'pageAbout', standards:'pageStandards', search:'pageSearch' };
    const el = document.getElementById(map[page]);
    if (el) el.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function markNav(which) {
    ['navHome','navArchive','navAbout','navStandards'].forEach(id => document.getElementById(id).classList.remove('on'));
    const map = { home:'navHome', archive:'navArchive', about:'navAbout', standards:'navStandards' };
    if (map[which]) document.getElementById(map[which]).classList.add('on');
  }

  function setCategory(category, btn) {
    currentCategory = category || 'all';
    if (btn) syncCategoryButtons(btn);
    if (currentPage === 'archive') renderArchive(); else renderHome();
  }

  function syncCategoryButtons(activeBtn) {
    document.querySelectorAll('.cat-pill').forEach(btn => btn.classList.remove('on'));
    if (activeBtn) { activeBtn.classList.add('on'); return; }
    const target = document.querySelector(`.cat-pill[data-cat="${CSS.escape(currentCategory)}"]`) || document.querySelector('.cat-pill[data-cat="all"]');
    if (target) target.classList.add('on');
  }

  function safeReplaceState(url) {
    try { history.replaceState({}, '', url); }
    catch (err) { console.warn('History replaceState falhou:', err); }
  }

  function safePushState(url) {
    try { history.pushState({}, '', url); }
    catch (err) { console.warn('History pushState falhou:', err); }
  }

  function openPage(page) {
    if (page === 'archive')   { safeReplaceState(pageUrl('archive'));   renderArchive(); }
    else if (page === 'about')     { safeReplaceState(pageUrl('about'));     renderAbout(); }
    else if (page === 'standards') { safeReplaceState(pageUrl('standards')); renderStandards(); }
    else goHome();
  }

  function goHome() { safeReplaceState(pageUrl('home')); renderHome(); }

  function openArticle(slug) {
    const post = DB.find(item => item.slug === slug);
    if (post) safePushState(getURLForArticle(post));
    renderArticle(slug);
  }

  function handleSearchInput(value) {
    clearTimeout(searchTimer);
    if (!value.trim()) { if (currentPage === 'search') goHome(); return; }
    searchTimer = setTimeout(() => renderSearch(value.trim()), 220);
  }

  function syncCurrentRouteUrl() {
    if (currentPage === 'search') return;
    if (currentPage === 'article' && currentArticleSlug) {
      const post = DB.find(item => item.slug === currentArticleSlug);
      if (post) { safeReplaceState(getURLForArticle(post)); return; }
    }
    if (currentPage === 'archive')   { safeReplaceState(pageUrl('archive')); return; }
    if (currentPage === 'about')     { safeReplaceState(pageUrl('about')); return; }
    if (currentPage === 'standards') { safeReplaceState(pageUrl('standards')); return; }
    safeReplaceState(pageUrl('home'));
  }

  function setLanguage(lang) {
    currentLang = lang === 'en' ? 'en' : 'pt';
    localStorage.setItem('cw_lang', currentLang);
    applyUIStrings();
    rerenderCurrentView();
    syncCurrentRouteUrl();
  }

  function applyUIStrings() {
    const homePageTitle = document.getElementById('homePageTitle');
    if (homePageTitle) homePageTitle.textContent = currentLang === 'en'
      ? 'Cosmos Week scientific news portal'
      : 'Portal Cosmos Week de notícias científicas';
    document.documentElement.lang = currentLang === 'en' ? 'en-US' : 'pt-BR';
    const ids = {
      logoSub:'logoSub', navHome:'home', navArchive:'archive', navAbout:'about',
      navStandards:'standards', methodBtn:'methodology', adsBtn:'advertise', updateBtnLabel:'update',
      tickerBadge:'ticker', latestSectionTitle:'latestTitle', latestSectionKicker:'latestKicker',
      archiveLinkTop:'archiveLink', trendingWidgetTitle:'trending', latestUpdatesTitle:'latestUpdatesTitle',
      sourceMixTitle:'sourceMixTitle', quickLinksTitle:'quickLinksTitle', archivePicksTitle:'archivePicksTitle',
      archiveTitle:'archiveTitle', archiveKicker:'archiveKicker', searchTitle:'searchTitle',
      footerDescription:'footerDescription', footerNavTitle:'footerNavTitle',
      footerAdvertise:'advertise', footerMediaKit:'mediaKit',
      footerSourcesTitle:'footerSourcesTitle', footerFeed:'footerFeed', footerPrivacy:'privacy', footerTerms:'terms',
      footerSitemap:'footerSitemap', footerCorrections:'footerCorrections',
      footerBottomLeft:'footerBottomLeft', footerBottomCenter:'footerBottomCenter',
      newsletterTitle:'newsletterTitle',
      newsletterDescription:'newsletterDescription', newsletterButton:'newsletterButton',
      newsletterNote:'newsletterNote', newsletterButton:'newsletterButton'
    };
    for (const [id, key] of Object.entries(ids)) {
      const el = document.getElementById(id); if (el) el.textContent = tr(key);
    }
    document.getElementById('topbarCopy').innerHTML = tr('topbarCopy');
    const si = document.getElementById('searchInput'); if (si) si.placeholder = tr('searchPlaceholder');
    const nl = document.getElementById('newsletterLabel'); if (nl) nl.textContent = tr('newsletterLabel');
    const ne = document.getElementById('newsletterEmail'); if (ne) ne.placeholder = tr('newsletterPlaceholder');
    syncAuxiliaryLinks();
    const cookieTitle = document.getElementById('cookieTitle'); if (cookieTitle) cookieTitle.textContent = tr('cookieTitle');
    const cookieLink = document.getElementById('cookiePolicyLink'); if (cookieLink) cookieLink.textContent = tr('cookiePolicy');
    const cookieText = document.getElementById('cookieText'); if (cookieText) {
      const linkHref = auxiliaryPageHref('privacy');
      cookieText.innerHTML = `${tr('cookieText').replace(tr('cookiePolicy'), `<a href="${linkHref}" id="cookiePolicyLink">${tr('cookiePolicy')}</a>`)}`;
    }
    const cookieBanner = document.getElementById('cookieBanner'); if (cookieBanner) cookieBanner.setAttribute('aria-label', tr('cookieAria'));
    const denyBtn = document.getElementById('cookieDenyBtn'); if (denyBtn) denyBtn.textContent = tr('cookieDeny');
    const analyticsBtn = document.getElementById('cookieAnalyticsBtn'); if (analyticsBtn) analyticsBtn.textContent = tr('cookieAnalytics');
    const acceptBtn = document.getElementById('cookieAcceptBtn'); if (acceptBtn) acceptBtn.textContent = tr('cookieAccept');
    document.querySelectorAll('.cat-pill').forEach(btn => {
      const cat = btn.dataset.cat;
      btn.textContent = cat === 'all' ? tr('allCategories') : prettyCategory(cat);
    });
    document.getElementById('langPt').classList.toggle('on', currentLang==='pt');
    document.getElementById('langEn').classList.toggle('on', currentLang==='en');
    const footerHome = document.getElementById('footerHome'); if (footerHome) footerHome.textContent = tr('home');
    const footerArchive = document.getElementById('footerArchive'); if (footerArchive) footerArchive.textContent = tr('archive');
    const footerAbout = document.getElementById('footerAbout'); if (footerAbout) footerAbout.textContent = tr('about');
    const footerStandards = document.getElementById('footerStandards'); if (footerStandards) footerStandards.textContent = tr('standardsPageTitle');
    syncPrimaryNavigationLinks();
    updateRigSyncBannerLanguage();
    updateLastUpdatedLabel();
  }


  const FLOAT_AD_CONFIG = {
    enabled: false,
    dismissKey: 'cw_floating_ad_dismissed',
    href: '#',
    target: '_blank',
    rel: 'noopener sponsored',
    pt: {
      eyebrow: 'Espaço patrocinado',
      title: 'Sua marca aqui',
      text: 'Este espaço está pronto para receber o link e a mensagem de um patrocinador.',
      cta: 'Anunciar',
      close: 'Fechar anúncio',
      aria: 'Espaço patrocinado'
    },
    en: {
      eyebrow: 'Sponsored slot',
      title: 'Your brand here',
      text: 'This slot is ready for a sponsor link and message whenever you want to activate it.',
      cta: 'Advertise',
      close: 'Close ad',
      aria: 'Sponsored slot'
    }
  };

  function updateRigSyncBannerLanguage() {
    const config = FLOAT_AD_CONFIG;
    const copy = config[currentLang] || config.pt;
    const eyebrow = document.getElementById('rigsyncBannerEyebrow');
    const title = document.getElementById('rigsyncBannerTitle');
    const text = document.getElementById('rigsyncBannerText');
    const cta = document.getElementById('rigsyncBannerCta');
    const close = document.getElementById('rigsyncBannerClose');
    const banner = document.getElementById('rigsyncBanner');
    const logo = banner ? banner.querySelector('.rigsync-float__logo') : null;

    if (eyebrow) eyebrow.textContent = copy.eyebrow;
    if (title) title.textContent = copy.title;
    if (text) text.textContent = copy.text;
    if (cta) {
      cta.textContent = copy.cta;
      cta.href = config.href || '#';
      cta.target = config.target || '_blank';
      cta.rel = config.rel || 'noopener sponsored';
      cta.setAttribute('aria-label', copy.cta);
    }
    if (logo) {
      logo.href = config.href || '#';
      logo.target = config.target || '_blank';
      logo.rel = config.rel || 'noopener sponsored';
      logo.setAttribute('aria-label', copy.aria);
    }
    if (close) close.setAttribute('aria-label', copy.close);
    if (banner) banner.setAttribute('aria-label', copy.aria);
  }

  function syncRigSyncBannerOffset() {
    const banner = document.getElementById('rigsyncBanner');
    if (!banner) return;
    const cookie = document.getElementById('cookieBanner');
    const visible = cookie && cookie.classList.contains('show');
    const base = window.innerWidth <= 780 ? 12 : 18;
    const extra = visible ? cookie.offsetHeight + 16 : 0;
    banner.style.bottom = `${base + extra}px`;
  }

  function initRigSyncBanner() {
    const banner = document.getElementById('rigsyncBanner');
    const close = document.getElementById('rigsyncBannerClose');
    const config = FLOAT_AD_CONFIG;
    if (!banner || !close) return;

    if (!config.enabled || !config.href || config.href === '#') {
      banner.remove();
      return;
    }

    try {
      if (localStorage.getItem(config.dismissKey) === '1') {
        banner.remove();
        return;
      }
    } catch (e) {}

    updateRigSyncBannerLanguage();
    syncRigSyncBannerOffset();

    close.addEventListener('click', () => {
      banner.classList.remove('show');
      window.setTimeout(() => banner.remove(), 220);
      try { localStorage.setItem(config.dismissKey, '1'); } catch (e) {}
    });

    window.addEventListener('resize', syncRigSyncBannerOffset, { passive: true });

    const cookie = document.getElementById('cookieBanner');
    if (cookie && typeof MutationObserver !== 'undefined') {
      const observer = new MutationObserver(syncRigSyncBannerOffset);
      observer.observe(cookie, { attributes: true, attributeFilter: ['class', 'style'] });
    }

    window.setTimeout(() => banner.classList.add('show'), 850);
  }

  function updateLastUpdatedLabel() {
    const latest = DB[0];
    const stamp = latest
      ? `${currentLang==='en'?(latest.date_en||latest.date):(latest.date_pt||latest.date)} · ${currentLang==='en'?(latest.time_en||latest.time):(latest.time_pt||latest.time)}`
      : tr('latestFeed');
    const el = document.getElementById('lastUpdatedLabel');
    if (el) el.textContent = `${tr('lastUpdatedPrefix')} ${stamp}`;
  }

  function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message; toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3200);
  }

  function refreshFeed() {
    const btn = document.getElementById('updateBtn');
    bumpHeroRotationSeed();
    btn.classList.add('loading'); btn.disabled = true;
    fetch(`/posts.js?cb=${Date.now()}`, { cache:'no-store' })
      .then(resp => { if (!resp.ok) throw new Error('fetch failed'); return resp.text(); })
      .then(js => {
        const sandboxWindow = {};
        Function('window', js + '; return window.postsData;')(sandboxWindow);
        if (Array.isArray(sandboxWindow.postsData) && sandboxWindow.postsData.length) {
          DB = mergePostCollections(sandboxWindow.postsData, DB);
          frontLayoutCache.clear();
          persistArchiveCache();
          updateLastUpdatedLabel();
          rerenderCurrentView();
          showToast(tr('updateDone'));
        } else {
          rerenderCurrentView();
          showToast(tr('updateDone'));
        }
      })
      .catch(() => { rerenderCurrentView(); showToast(tr('updateFail')); })
      .finally(() => { btn.classList.remove('loading'); btn.disabled = false; });
  }

  function copyArticleLink() {
    const post = DB.find(item => item.slug === currentArticleSlug);
    const url = post ? getShareURLForArticle(post) : location.href;
    navigator.clipboard.writeText(url).then(() => showToast(tr('copied'))).catch(() => showToast(url));
  }

  async function shareCurrentArticle() {
    const post = DB.find(item => item.slug === currentArticleSlug);
    const url = post ? getShareURLForArticle(post) : location.href;
    const title = post ? textFor(post, 'title') : document.title;
    const textBody = post ? stripHtml(textFor(post, 'excerpt') || textFor(post, 'sub') || '') : '';
    const shareData = { title, text: textBody, url };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
        return;
      } catch (err) {
        if (err && err.name === 'AbortError') return;
      }
    }

    navigator.clipboard.writeText(url)
      .then(() => showToast(tr('shareFallback')))
      .catch(() => showToast(url));
  }

  function handleNewsletterSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('newsletterEmail');
    const email = input.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { showToast(tr('newsletterInvalid')); input.focus(); return; }
    localStorage.setItem('cw_newsletter_email', email);
    input.value = ''; showToast(tr('newsletterSuccess'));
  }

  function loadSavedNewsletterEmail() {
    const saved = localStorage.getItem('cw_newsletter_email');
    if (saved) { const el = document.getElementById('newsletterEmail'); if (el) el.value = saved; }
  }

  const CONSENT_KEY = 'cw_cookie_consent';

  /* Mapeia os 3 estados para os sinais do Consent Mode v2.
     'full'      → analytics + anúncios personalizados
     'analytics' → só analytics, anúncios não-personalizados
     'denied'    → tudo desligado                           */
  function _consentSignals(mode) {
    const full      = mode === 'full';
    const analytics = mode === 'full' || mode === 'analytics';
    return {
      analytics_storage:  analytics ? 'granted' : 'denied',
      ad_storage:         full      ? 'granted' : 'denied',
      ad_user_data:       full      ? 'granted' : 'denied',
      ad_personalization: full      ? 'granted' : 'denied'
    };
  }

  function setCookieConsent(mode) {
    // mode: 'full' | 'analytics' | 'denied'
    try { localStorage.setItem(CONSENT_KEY, mode); } catch (e) {}
    if (typeof gtag === 'function') gtag('consent', 'update', _consentSignals(mode));
    const banner = document.getElementById('cookieBanner');
    if (banner) banner.classList.remove('show');
  }

  function initCookieBanner() {
    let saved = null;
    try { saved = localStorage.getItem(CONSENT_KEY); } catch (e) {}
    const banner = document.getElementById('cookieBanner');
    if (!banner) return;

    const validStates = ['full', 'analytics', 'denied',
                         'granted']; // 'granted' = estado legado, tratar como 'analytics'
    if (validStates.includes(saved)) {
      const normalized = saved === 'granted' ? 'analytics' : saved;
      if (typeof gtag === 'function') gtag('consent', 'update', _consentSignals(normalized));
      // Migra silenciosamente o valor legado
      if (saved === 'granted') { try { localStorage.setItem(CONSENT_KEY, 'analytics'); } catch (e) {} }
      banner.classList.remove('show');
      return;
    }

    banner.classList.add('show');
  }

  // ── SEO / Meta ─────────────────────────────────────────────────────────────
  function updateMetaHome() {
    const title = currentLang==='en' ? SITE.homeTitleEn : SITE.homeTitlePt;
    const description = currentLang==='en' ? SITE.homeDescriptionEn : SITE.homeDescriptionPt;
    const homeJsonLd = [
      {
        '@context': 'https://schema.org',
        '@type': 'NewsMediaOrganization',
        '@id': SITE.canonicalBaseUrl + '#organization',
        name: SITE.title,
        url: SITE.canonicalBaseUrl,
        logo: { '@type': 'ImageObject', url: 'https://www.cosmosweek.com/assets/og-default.jpg' },
        description: description,
        publishingPrinciples: canonicalPageUrl('standards', 'pt'),
        inLanguage: ['pt-BR', 'en-US']
      },
      {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': SITE.canonicalBaseUrl + '#website',
        name: SITE.title,
        url: SITE.canonicalBaseUrl,
        description: description,
        inLanguage: currentLang === 'en' ? 'en-US' : 'pt-BR',
        publisher: { '@id': SITE.canonicalBaseUrl + '#organization' },
        potentialAction: {
          '@type': 'SearchAction',
          target: { '@type': 'EntryPoint', urlTemplate: SITE.canonicalBaseUrl + '?q={search_term_string}' },
          'query-input': 'required name=search_term_string'
        }
      }
    ];
    updateMetaCommon(title, description, canonicalPageUrl('home'), IMG.pillars, homeJsonLd, {
      robots: 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1',
      newsKeywords: 'astronomia, astrofísica, cosmologia, ciência, espaço',
      alternatePt: canonicalPageUrl('home', 'pt'),
      alternateEn: canonicalPageUrl('home', 'en'),
      alternateDefault: canonicalPageUrl('home', 'pt'),
      locale: currentLang === 'en' ? 'en_US' : 'pt_BR',
      localeAlternate: currentLang === 'en' ? 'pt_BR' : 'en_US',
      imageAlt: 'Cosmos Week',
      author: currentLang === 'en' ? 'Cosmos Week Editorial Desk' : 'Redação do Cosmos Week',
      ogType: 'website'
    });
  }

  function updateMetaStatic(page) {
    const titles = {
      about: currentLang==='en'?'About Cosmos Week':'Sobre o Cosmos Week',
      archive: currentLang==='en'?'Editorial archive':'Arquivo editorial',
      standards: currentLang==='en'?'Editorial standards':'Padrões editoriais',
      search: currentLang==='en'?'Search':'Busca'
    };
    const descriptions = {
      about: currentLang==='en'?'About the editorial ambition and scope of Cosmos Week.':'Sobre a ambição editorial e o escopo do Cosmos Week.',
      archive: currentLang==='en'?'The complete archive of stories currently available.':'O arquivo completo das matérias disponíveis.',
      standards: currentLang==='en'?'Methodology, source labeling and editorial safeguards.':'Metodologia, rotulagem de fonte e salvaguardas editoriais.',
      search: currentLang==='en'?'Search results inside Cosmos Week.':'Resultados de busca dentro do Cosmos Week.'
    };
    updateMetaCommon(`${titles[page]} — ${SITE.title}`, descriptions[page], canonicalPageUrl(page), IMG.pillars, null, {
      robots: page === 'search' ? 'noindex,follow' : 'index,follow',
      newsKeywords: 'Notícias Científicas, astronomia, astrofísica, cosmologia',
      alternatePt: canonicalPageUrl(page, 'pt'),
      alternateEn: canonicalPageUrl(page, 'en'),
      alternateDefault: canonicalPageUrl(page, 'pt'),
      locale: currentLang === 'en' ? 'en_US' : 'pt_BR',
      localeAlternate: currentLang === 'en' ? 'pt_BR' : 'en_US',
      imageAlt: titles[page],
      author: currentLang === 'en' ? 'Cosmos Week Editorial Desk' : 'Redação do Cosmos Week',
      ogType: 'website'
    });
  }

  function updateMetaArticle(post) {
    const title = `${textFor(post,'title')} — ${SITE.title}`;
    const description = textFor(post,'excerpt') || textFor(post,'sub') || textFor(post,'title');
    const url = getCanonicalURLForArticle(post);
    const alternates = articleAlternateUrls(post);
    const keywords = keywordListFor(post);
    const langCode = currentLang === 'en' ? 'en-US' : 'pt-BR';
    const authorName = currentLang === 'en' ? 'Cosmos Week Editorial Desk' : 'Redação do Cosmos Week';
    const image = primaryImage(post);
    const jsonLd = [
      { '@context':'https://schema.org','@type':'NewsMediaOrganization', '@id':`${SITE.canonicalBaseUrl}#organization`, name:SITE.title, url:SITE.canonicalBaseUrl, logo:{'@type':'ImageObject',url:IMG.pillars} },
      { '@context':'https://schema.org','@type':'BreadcrumbList', itemListElement:[
        {'@type':'ListItem',position:1,name:currentLang==='en'?'Home':'Início',item: canonicalPageUrl('home', currentLang)},
        {'@type':'ListItem',position:2,name:prettyCategory(post.cat),item: canonicalPageUrl('home', currentLang)},
        {'@type':'ListItem',position:3,name:textFor(post,'title'),item:url}
      ]},
      { '@context':'https://schema.org','@type':'WebPage', '@id':url, url, name:title, description,
        inLanguage:langCode,
        isPartOf:{'@type':'WebSite',name:SITE.title,url: canonicalPageUrl('home', currentLang)},
        primaryImageOfPage:{'@type':'ImageObject',url:image},
        hasPart:[{'@type':'WebPage',url:currentLang==='en'?alternates.pt:alternates.en,inLanguage:currentLang==='en'?'pt-BR':'en-US'}]
      },
      { '@context':'https://schema.org','@type':'NewsArticle',
        headline:textFor(post,'title'), description, image:[image], thumbnailUrl:image,
        datePublished:post.publishedIso, dateModified:post.lastModifiedIso||post.publishedIso,
        inLanguage:langCode, isAccessibleForFree:true,
        articleSection:prettyCategory(post.cat), keywords,
        author:[{'@type':'Organization',name:authorName}],
        publisher:{'@type':'Organization',name:SITE.title,logo:{'@type':'ImageObject',url:IMG.pillars}},
        mainEntityOfPage:{'@type':'WebPage','@id':url},
        about:keywords.map(k => ({'@type':'Thing',name:k})),
        isBasedOn: post.srcUrl || undefined,
        citation: post.srcUrl ? [{'@type':'CreativeWork', name:post.source || post.srcUrl, url:post.srcUrl}] : undefined
      }
    ];
    updateMetaCommon(title, description, url, image, jsonLd, {
      robots: 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1',
      newsKeywords: keywords.join(', '),
      published: post.publishedIso,
      modified: post.lastModifiedIso || post.publishedIso,
      alternatePt: alternates.pt,
      alternateEn: alternates.en,
      alternateDefault: alternates.xDefault,
      locale: currentLang === 'en' ? 'en_US' : 'pt_BR',
      localeAlternate: currentLang === 'en' ? 'pt_BR' : 'en_US',
      imageAlt: textFor(post,'title'),
      author: authorName,
      section: prettyCategory(post.cat),
      ogType: 'article'
    });
  }

  function updateMetaCommon(title, description, url, image, articleJsonLd, options = {}) {
    document.title = title;
    document.querySelector('meta[name="description"]').setAttribute('content', description);
    document.querySelector('meta[property="og:title"]').setAttribute('content', title);
    document.querySelector('meta[property="og:description"]').setAttribute('content', description);
    document.querySelector('meta[property="og:type"]').setAttribute('content', options.ogType || 'website');
    document.querySelector('meta[property="og:url"]').setAttribute('content', url);
    document.querySelector('meta[property="og:image"]').setAttribute('content', image);
    document.getElementById('ogImageAltMeta').setAttribute('content', options.imageAlt || title);
    document.getElementById('ogLocaleMeta').setAttribute('content', options.locale || 'pt_BR');
    document.getElementById('ogLocaleAlternateMeta').setAttribute('content', options.localeAlternate || 'en_US');
    document.querySelector('meta[name="twitter:title"]').setAttribute('content', title);
    document.querySelector('meta[name="twitter:description"]').setAttribute('content', description);
    document.querySelector('meta[name="twitter:image"]').setAttribute('content', image);
    document.getElementById('twitterImageAltMeta').setAttribute('content', options.imageAlt || title);
    document.getElementById('authorMeta').setAttribute('content', options.author || (currentLang === 'en' ? 'Cosmos Week Editorial Desk' : 'Redação do Cosmos Week'));
    document.getElementById('canonicalLink').setAttribute('href', url);
    document.getElementById('alternatePtLink').setAttribute('href', options.alternatePt || withLanguageParam(url, 'pt'));
    document.getElementById('alternateEnLink').setAttribute('href', options.alternateEn || withLanguageParam(url, 'en'));
    document.getElementById('alternateDefaultLink').setAttribute('href', options.alternateDefault || withLanguageParam(url, 'pt'));
    document.getElementById('robotsMeta').setAttribute('content', options.robots||'index,follow');
    document.getElementById('newsKeywordsMeta').setAttribute('content', options.newsKeywords||'astronomia, ciência');
    document.getElementById('articlePublishedMeta').setAttribute('content', options.published||'');
    document.getElementById('articleModifiedMeta').setAttribute('content', options.modified||options.published||'');
    document.getElementById('articleSectionMeta').setAttribute('content', options.section || '');
    document.getElementById('siteJsonLd').textContent = JSON.stringify(articleJsonLd || {
      '@context':'https://schema.org','@type':'WebSite', name:SITE.title, url: canonicalPageUrl('home', currentLang), description,
      inLanguage: currentLang === 'en' ? 'en-US' : 'pt-BR'
    });
  }

  function rerenderCurrentView() {
    if (currentPage==='article' && currentArticleSlug) renderArticle(currentArticleSlug);
    else if (currentPage==='archive') renderArchive();
    else if (currentPage==='about') renderAbout();
    else if (currentPage==='standards') renderStandards();
    else if (currentPage==='search') {
      const q = document.getElementById('searchInput').value.trim();
      if (q) renderSearch(q); else renderHome();
    } else renderHome();
  }

  function parseRoute() {
    const params = new URLSearchParams(window.location.search);
    const article = params.get('article');
    const pageParam = normalizePageKey(params.get('page') || '');
    const path = window.location.pathname || '';
    const bodyPage = normalizePageKey(document.body?.dataset?.cwPage || '');
    const bodyLang = (document.body?.dataset?.cwLang || '').toLowerCase();
    const pathMatchPt = path.match(/^\/noticia\/([^\/]+)\/?$/i);
    const pathMatchEn = path.match(/^\/en\/news\/([^\/]+)\/?$/i);
    const articleFromPath = pathMatchEn ? decodeURIComponent(pathMatchEn[1]) : (pathMatchPt ? decodeURIComponent(pathMatchPt[1]) : '');
    if ((params.get('lang') || '').toLowerCase() === 'en' || /^\/en(?:\/|$)/i.test(path) || pathMatchEn || bodyLang === 'en') currentLang = 'en';
    if ((params.get('lang') || '').toLowerCase() === 'pt' || pathMatchPt || bodyLang === 'pt' || /^\/(arquivo|sobre|padroes)(?:\/|$)/i.test(path) || path === '/') currentLang = 'pt';
    if (article) { renderArticle(article); return; }
    if (articleFromPath) { renderArticle(articleFromPath); return; }
    const page = pageParam !== 'home' ? pageParam : (routePageFromPath(path) || bodyPage || 'home');
    if (page === 'archive') { renderArchive(); return; }
    if (page === 'about') { renderAbout(); return; }
    if (page === 'standards') { renderStandards(); return; }
    renderHome();
  }

  // Reading progress
  window.addEventListener('scroll', () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = max > 0 ? (window.scrollY / max) * 100 : 0;
    document.getElementById('readingProgress').style.width = `${ratio}%`;
  }, { passive: true });

  window.addEventListener('popstate', parseRoute);

  document.addEventListener('DOMContentLoaded', () => {
    applyUIStrings();
    loadSavedNewsletterEmail();
    initCookieBanner();
    initRigSyncBanner();
    persistArchiveCache();
    parseRoute();
    if (normalizePageKey(document.body?.dataset?.cwPage || '') === 'archive' || routePageFromPath(window.location.pathname || '') === 'archive') {
      ensureFullArchiveLoaded();
    }
  });
