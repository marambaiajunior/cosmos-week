# Cosmos Week Analytics repair

Este pacote corrige a medição do Google Analytics no Cosmos Week.

## O que foi corrigido

1. Todas as páginas HTML existentes passam a carregar:
   `<script src="/assets/js/cw-analytics.js" data-ga-id="G-MX20J1ZG06"></script>`

2. As tags antigas inline do GA foram removidas das páginas principais para evitar duplicação de `page_view`.

3. As páginas de matérias existentes em `/noticia/` e `/en/news/` agora carregam Analytics.

4. O gerador `scripts/fetch_news.py` foi alterado para que matérias novas também já sejam criadas com Analytics.

5. O arquivo `assets/js/cw-analytics.js` centraliza:
   - Consent Mode v2;
   - carregamento do GA4;
   - `page_view` inicial;
   - `page_view` em navegação SPA via `pushState`, `replaceState` e `popstate`;
   - banner de consentimento automático nas páginas que não tinham banner.

## Como aplicar

Extraia o conteúdo deste `.zip` na raiz do repositório `cosmos-week-main`, sobrescrevendo os arquivos existentes.

Depois faça commit e deploy.

## Validação local recomendada

```bash
grep -R "/assets/js/cw-analytics.js" -n --include="*.html" .
grep -R "googletagmanager.com/gtag/js?id=G-MX20J1ZG06" -n --include="*.html" .
```

O primeiro comando deve encontrar todas as páginas HTML.
O segundo comando idealmente não deve encontrar nada nos HTMLs, porque o carregamento ficou centralizado em `assets/js/cw-analytics.js`.

## Observação

O script `scripts/apply_analytics_repair.py` também está incluído. Ele serve como ferramenta de segurança: se algum HTML antigo escapar, rode:

```bash
python scripts/apply_analytics_repair.py
```
