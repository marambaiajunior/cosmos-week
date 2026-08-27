# Auditoria e implementação — Vórtice Maligno

Data da execução: 27 de agosto de 2026  
Escopo principal: `https://www.cosmosweek.com/livro/vortice-maligno/` e recursos diretamente associados  
Publicação: **não realizada**

## Resultado executivo

A implementação atende no código-fonte aos 14 itens verificáveis do checklist. Foram corrigidos o overflow horizontal no escopo das experiências do livro, a entrega responsiva da capa, os metadados Twitter/OG, a rota do checklist, os `lastmod`, a governança de Analytics por consentimento, a reabertura das preferências de cookies e as proteções de regressão do deploy.

A fonte de verdade comercial foi preservada:

- título: **Vórtice Maligno**;
- autor: **Humberto Marambaia Junior**;
- ISBN visível: **978-65-266-8163-3**;
- ISBN no JSON-LD: `9786526681633`;
- 1ª edição, 2026, 314 páginas;
- preço: **R$ 59,12** / `59.12 BRL`;
- vendedor: **Clube de Autores**;
- compra: `https://clubedeautores.com.br/livro/vortice-maligno`;
- canonical: `https://www.cosmosweek.com/livro/vortice-maligno/`.

Validação final local: **197 aprovações e 0 falhas**.

## Arquitetura encontrada

- Site estático bilíngue, sem `package.json`, framework ou etapa de compilação do front-end.
- 4.129 documentos HTML no pacote.
- O próprio diretório raiz é o artefato publicado pelo GitHub Pages.
- `.github/workflows/deploy.yml` envia o conteúdo estático para Pages.
- `.github/workflows/update.yml` regenera conteúdo, índices e sitemap diariamente.
- A página do livro é mantida em `livro/vortice-maligno/index.html`.
- CSS e comportamento compartilhados ficam em `assets/css/book.css`, `assets/js/book.js` e `assets/js/cw-analytics.js`.
- O sitemap é produzido por `scripts/build_sitemap.mjs`.
- `robots.txt` e `404.html` já existiam e estavam corretos; foram preservados.

O comando `git status --short --branch` foi executado, mas retornou código 128 porque o ZIP recebido não contém o diretório `.git`. Para preservar e auditar o material original, a implementação foi feita em uma segunda extração e comparada integralmente com uma cópia intocada.

## Linha de base

- Primeira execução da verificação local: `PASS 61`, `FAIL 29`.
- Produção, antes das mudanças, apresentou `clientWidth = 1348` e `scrollWidth = 1436`, confirmando overflow horizontal real.
- Principais falhas locais: rota do checklist com caixa incorreta, ausência de `srcset`/`sizes` e variantes responsivas, `twitter:image:alt` ausente, `lastmod` ausente, referência comercial histórica obsoleta e carregamento do Google tag antes de consentimento.

## Checklist implementado

| Item | Resultado no código-fonte |
|---|---|
| CTA na primeira dobra | CTAs de cabeçalho e hero preservados; áreas mínimas de 44 px; barra mobile com safe area; localidades Analytics normalizadas para `header`, `hero`, `sticky_mobile` e `final_cta`. |
| Título e descrição | Landing e checklist têm um único `title`, description, canonical e `h1`, com `lang`, `hreflang` e robots coerentes. |
| Favicon | `/assets/favicon.svg` preservado e referenciado; `site.webmanifest` declarado. Não foram inventados PNGs de baixa qualidade. |
| Alt text | Capa e retrato mantêm descrições; imagens decorativas mantêm `alt=""`; todas as imagens auditadas têm dimensões intrínsecas. |
| Responsividade | Decorações contidas com `overflow-x: clip` somente em `body.book-page` e `body.book-guide-page`; navegação interna continua rolável; cabeçalho e CTA foram ajustados em telas estreitas. |
| Formulários | Não aplicável: landing, checklist e páginas públicas de contato não possuem formulário funcional. Nenhum formulário artificial foi criado. |
| Privacidade | Política atualizada para refletir a implementação; controles visíveis permitem reabrir e alterar a preferência de cookies. |
| Analytics / Search Console | GA4 `G-MX20J1ZG06` carrega somente após consentimento Analytics/full; `page_view` e eventos são bloqueados sem consentimento e deduplicados; UTMs são saneadas. Não há token/meta/arquivo de Search Console no repositório, portanto o método externo ou DNS permanece para confirmação manual. |
| Imagens comprimidas | Capa entregue por `<picture>` em AVIF/WebP, cinco larguras, `srcset` e `sizes`; hero continua sem lazy loading; recursos abaixo da dobra usam lazy loading. |
| 404 | Conteúdo existente preservado e servidor local de verificação retorna HTTP 404 real com `noindex,follow`. |
| Open Graph / Twitter | OG JPG 1200×630 preservado; MIME, dimensões, textos alternativos e `twitter:image:alt` validados. |
| `robots.txt` | Preservado: permite crawling público e aponta para o sitemap absoluto. |
| `sitemap.xml` | XML regenerado, sem duplicatas, com URLs canônicas do livro/checklist e `lastmod` legítimo `2026-08-27`. |
| Índice de busca obsoleto | ISBN antigo e URL de compra Amazon da obra removidos do material do projeto; registro histórico foi neutralizado sem substituição global em notícias não relacionadas. |

## Imagens: antes e depois

Arquivo-base WebP anteriormente entregue em todos os contextos: 519.188 bytes, 1280×2048.

| Arquivo | Dimensões | Bytes | Redução vs. WebP-base |
|---|---:|---:|---:|
| `vortice-maligno-capa-320.avif` | 320×512 | 26.961 | 94,8% |
| `vortice-maligno-capa-320.webp` | 320×512 | 40.078 | 92,3% |
| `vortice-maligno-capa-480.avif` | 480×768 | 57.527 | 88,9% |
| `vortice-maligno-capa-480.webp` | 480×768 | 83.640 | 83,9% |
| `vortice-maligno-capa-640.avif` | 640×1024 | 96.242 | 81,5% |
| `vortice-maligno-capa-640.webp` | 640×1024 | 139.210 | 73,2% |
| `vortice-maligno-capa-960.avif` | 960×1536 | 186.388 | 64,1% |
| `vortice-maligno-capa-960.webp` | 960×1536 | 258.612 | 50,2% |
| `vortice-maligno-capa-1280.avif` | 1280×2048 | 278.369 | 46,4% |
| `vortice-maligno-capa-1280.webp` | 1280×2048 | 367.860 | 29,1% |

Preservados por compatibilidade:

- OG JPG: 1200×630, 110.723 bytes;
- capa JPG do JSON-LD: 1280×2048, 785.036 bytes.

O gerador foi repetido e produziu arquivos byte a byte idênticos. A menor variante também foi inspecionada visualmente e manteve capa e tipografia legíveis.

## Validações executadas

```text
python scripts/validate_vortice.py
PASS 197
FAIL 0

node scripts/test_analytics_consent.mjs
Analytics consent tests: PASS

python scripts/apply_analytics_repair.py
Analytics repair complete: 0 HTML files updated / 4129 scanned.

node --check em todos os .js/.mjs
compile() em todos os .py
parse em todos os .json, .xml, .yml e .yaml
PASS: JS/MJS=12, Python=9, JSON=6, XML=2, YAML=2

node scripts/build_sitemap.mjs + python scripts/build_book_images.py
PASS: sitemap e dez variantes de imagem reproduzidos com SHA-256 idêntico

smoke HTTP local
PASS: 13 rotas/recursos essenciais com HTTP 200 e rota inexistente com HTTP 404 real
```

Outras verificações finais:

- 4.129 HTML examinados;
- 4.126 usam o carregador Analytics central;
- os três HTML sem Analytics são a 404 e dois redirecionamentos `noindex`;
- zero carregadores diretos de GA em HTML;
- zero bootstrap legado inline de `gtag` em HTML;
- zero ocorrência do ISBN antigo relacionada à obra;
- zero URL obsoleta de compra Amazon relacionada à obra;
- JSON-LD parseável e consistente com texto, preço, vendedor e disponibilidade;
- `robots.txt`, sitemap, favicon, manifest, CSS, JS e imagens essenciais respondem localmente.

Como não há `package.json`, build ou lint do framework, não existe um comando de “production build” além da geração dos arquivos estáticos. O artefato estático final foi regenerado e validado pelas rotinas acima. As mesmas verificações foram adicionadas aos workflows de atualização e deploy para bloquear regressões.

## Validação visual e Lighthouse

A versão corrigida não pôde ser aberta no navegador de QA deste ambiente: a prévia aceita projetos com servidor de desenvolvimento baseado em `package.json`, enquanto este repositório é um site estático puro. A política da ferramenta não permite substituir essa validação por um navegador autônomo. Por isso, não há resultado inventado para as larguras 320, 360, 375, 390, 414, 768, 1024 e 1440 px, nem notas Lighthouse da versão corrigida.

O que foi validado sem renderização:

- contenção de overflow restrita às páginas do livro, sem `overflow-x: hidden` global;
- áreas mínimas de toque, compensação da barra fixa e safe area;
- `prefers-reduced-motion`;
- contrastes estáticos principais ≥ 4,5:1;
- estrutura nativa e nomes acessíveis de FAQ, botões e links;
- regras e assets responsivos para todas as larguras solicitadas.

O teste visual final, o critério `scrollWidth <= clientWidth + 1`, o zoom de 200%, a navegação por teclado, o console e o Lighthouse permanecem como verificação manual pós-deploy. Não se declara aprovação desses itens sem medição.

## Arquivos alterados

### Infraestrutura e documentação

- `.github/workflows/deploy.yml`
- `.github/workflows/update.yml`
- `AJUSTES-LANDING-VORTICE-2026-08-13-REV4-README.txt`
- `README_ANALYTICS_REPAIR.md`
- `AUDITORIA-VORTICE-MALIGNO-CHECKLIST-2026-08-27.md` (este relatório)
- `sitemap.xml`

### Página e estilos/comportamento

- `livro/vortice-maligno/index.html`
- `Livro/vortice-maligno/checklist/index.html` (removido; rota com caixa incorreta)
- `livro/vortice-maligno/checklist/index.html` (adicionado na rota canônica)
- `assets/css/book.css`
- `assets/js/book.js`
- `assets/js/cw-analytics.js`
- `index.html`
- `guias/como-distinguir-ciencia-de-pseudociencia/index.html`

### Remoção do bootstrap Analytics legado

- `arquivo/index.html`
- `sobre/index.html`
- `padroes/index.html`
- `politica-de-privacidade.html`
- `en/index.html`
- `en/about/index.html`
- `en/archive/index.html`
- `en/standards/index.html`
- `en/privacy/index.html`

### Novos assets responsivos

- `assets/img/livro/vortice-maligno-capa-320.avif`
- `assets/img/livro/vortice-maligno-capa-320.webp`
- `assets/img/livro/vortice-maligno-capa-480.avif`
- `assets/img/livro/vortice-maligno-capa-480.webp`
- `assets/img/livro/vortice-maligno-capa-640.avif`
- `assets/img/livro/vortice-maligno-capa-640.webp`
- `assets/img/livro/vortice-maligno-capa-960.avif`
- `assets/img/livro/vortice-maligno-capa-960.webp`
- `assets/img/livro/vortice-maligno-capa-1280.avif`
- `assets/img/livro/vortice-maligno-capa-1280.webp`

### Scripts de validação/manutenção

- `scripts/apply_analytics_repair.py`
- `scripts/build_book_images.py`
- `scripts/serve_static.py`
- `scripts/test_analytics_consent.mjs`
- `scripts/validate_vortice.py`

## Ações manuais pós-deploy

1. Abrir a landing e o checklist nas larguras 320, 360, 375, 390, 414, 768, 1024 e 1440 px e verificar `document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1`.
2. Confirmar CTA na primeira dobra, barra fixa, zoom a 200%, foco visível, ordem de teclado e FAQ em Chrome e Safari.
3. Inspecionar o console e a aba Network; confirmar ausência de erros e 4xx/5xx essenciais.
4. Executar Lighthouse mobile e registrar Performance, Accessibility, Best Practices, SEO, CLS e LCP.
5. Testar uma URL inexistente no host final e confirmar HTTP 404 real, não soft 404.
6. Confirmar HTTP 200 para favicon, manifest, `robots.txt`, `sitemap.xml`, OG JPG e capa JPG do JSON-LD.
7. Confirmar no Google Search Console o método real de propriedade, inspecionar a canonical e solicitar nova indexação. Não há garantia de prazo de atualização do Google.
8. Revalidar preço e disponibilidade no Clube de Autores antes do deploy caso a publicação ocorra em outra data.

