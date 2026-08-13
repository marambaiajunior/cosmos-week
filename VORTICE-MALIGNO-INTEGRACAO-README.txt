COSMOS WEEK — INTEGRAÇÃO VÓRTICE MALIGNO
Data: 2026-08-12

ROTA PRINCIPAL
https://www.cosmosweek.com/livro/vortice-maligno/

AMAZON BRASIL CONFIGURADA
https://www.amazon.com.br/dp/6502266509

Observação importante sobre o link de compra:
- A capa informa o ISBN-13 978-65-02-26650-2.
- O botão foi configurado para amazon.com.br usando o ISBN-10 correspondente, 6502266509, na rota /dp/.
- O encurtador a.co enviado como referência não foi incorporado ao código. Assim, todo CTA de compra permanece explicitamente no domínio amazon.com.br.

ARQUIVOS NOVOS
- livro/vortice-maligno/index.html
- livro/index.html
- assets/css/book.css
- assets/js/book.js
- assets/img/livro/vortice-maligno-capa.webp
- assets/img/livro/vortice-maligno-capa.jpg
- assets/img/livro/vortice-maligno-og.jpg

ARQUIVOS MODIFICADOS / INTEGRAÇÃO
- index.html: item Livro no menu, card editorial na homepage e link no footer.
- arquivo/, sobre/, padroes/ e guias/: item Livro somente nas páginas em português.
- guias/como-distinguir-ciencia-de-pseudociencia/: CTA contextual para o livro.
- noticia/alan-valejo/ e noticia/seti-panel-revises-recommendations-for-dealing-with-disclosure-day/: CTA contextual por tratarem de desinformação/comunicação científica.
- scripts/fetch_news.py: novas matérias em português que tratem de pseudociência, teorias conspiratórias, desinformação, negacionismo, antivacina ou terraplanismo recebem CTA contextual automaticamente. As páginas em inglês não recebem esse bloco.
- scripts/upgrade_shell_pages.mjs: preserva a rota e o item Livro nas páginas PT mantidas pelo fluxo automático.
- .github/workflows/update.yml: valida landing/capa e inclui os arquivos do livro no staging do fluxo diário.
- sitemap.xml: regenerado com a landing indexável.

LANDING PAGE
- Em português do Brasil apenas.
- Identidade visual inspirada no Cosmos Week e na paleta da capa.
- SEO, Open Graph, Twitter Card e dados estruturados Schema.org Book.
- Capa otimizada em WebP/JPG.
- Conteúdo editorial baseado no manuscrito fornecido, incluindo o MVM, os cinco níveis, os três eixos, o estudo exploratório com 2.193 respondentes e os limites metodológicos expressos no próprio livro.
- Botões de compra exclusivamente para Amazon.com.br.
- Eventos GA4: book_cta_click e book_amazon_br_click.

NÃO FOI CRIADA VERSÃO EM INGLÊS.
Nenhum item Livro foi adicionado às páginas sob /en/.

TESTE LOCAL
Na raiz do projeto:
python -m http.server 8000
Abra: http://localhost:8000/livro/vortice-maligno/

PUBLICAÇÃO
Substitua/adicione os arquivos preservando exatamente as pastas e faça commit na branch main. O workflow Publicar site continuará responsável pelo deploy no GitHub Pages.
