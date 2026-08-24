COSMOS WEEK — INTEGRAÇÃO COMERCIAL VÓRTICE MALIGNO
Versão: 2026-08-24

ROTAS
- Landing: https://www.cosmosweek.com/livro/vortice-maligno/
- Checklist gratuito: https://www.cosmosweek.com/livro/vortice-maligno/checklist/
- Compra: https://clubedeautores.com.br/livro/vortice-maligno

EDIÇÃO DE REFERÊNCIA
- Varejista: Clube de Autores
- Versão: impressa
- Preço exibido em 24/08/2026: R$ 59,12
- ISBN: 978-65-266-8163-3
- Páginas: 314
- Edição: 1ª edição (2026)
- Formato: A5 (148 × 210 mm)
- Acabamento: brochura com orelha
- Miolo: preto e branco, papel pólen

O preço e o frete são controlados pelo Clube de Autores. Confirme o preço antes
de cada campanha e atualize landing, homepage, dados estruturados e book.js se o
valor mudar.

O QUE FOI IMPLEMENTADO
- Landing reestruturada para conversão, mantendo o rigor editorial.
- Oferta, preço, formato, ISBN e canal de compra apresentados sem contradições.
- CTAs em hero, cabeçalho, FAQ, encerramento e barra móvel.
- Transparência sobre checkout, pagamento, frete, prazo e envio externos.
- Seções de público, objeções, conteúdo, método, autor, edição e FAQ.
- Dados estruturados Schema.org para WebPage, Book, Offer, FAQ e breadcrumbs.
- Open Graph e Twitter Card prontos para compartilhamento.
- Checklist gratuito, imprimível e compartilhável, sem cadastro fictício.
- Navegação e estados de foco acessíveis.
- Layout responsivo com respeito a prefers-reduced-motion.

MENSURAÇÃO GA4
- view_item: visualização da landing como produto.
- book_landing_view: visualização comercial da landing.
- book_cta_click: qualquer CTA do ecossistema do livro.
- book_store_click: saída para o Clube de Autores.
- book_clube_autores_click: evento legado preservado.
- book_guide_view: visualização do checklist.
- book_guide_click: acesso ao checklist.
- book_guide_share: tentativa de compartilhamento.
- book_guide_print: impressão ou salvamento em PDF.
- book_faq_open: abertura de uma dúvida frequente.

Os parâmetros UTM presentes na URL são anexados aos eventos do livro. Como o
checkout ocorre em outro domínio e não retorna o evento de compra ao Cosmos Week,
book_store_click mede intenção de compra, não venda concluída. Compare esses
eventos com os pedidos reais do painel do varejista.

PIXEL DE ANÚNCIOS
Nenhum Meta Pixel foi ativado porque o projeto não contém um ID de Pixel
pertencente ao autor. Não publique um ID inventado. O plano de campanha descreve
como conectar um Pixel real depois que ele for criado no Gerenciador de Eventos.

ARQUIVOS PRINCIPAIS
- livro/vortice-maligno/index.html
- livro/vortice-maligno/checklist/index.html
- assets/css/book.css
- assets/js/book.js
- assets/img/livro/vortice-maligno-capa.webp
- assets/img/livro/vortice-maligno-capa.jpg
- assets/img/livro/vortice-maligno-og.jpg
- CAMPANHA-VORTICE-MALIGNO.md

TESTE LOCAL
Na raiz do projeto:
1. python -m http.server 8000
2. Abra http://localhost:8000/livro/vortice-maligno/
3. Abra http://localhost:8000/livro/vortice-maligno/checklist/

PUBLICAÇÃO
Envie o conteúdo desta pasta para a branch main do repositório. O workflow de
deploy existente continuará responsável pela publicação no GitHub Pages.
