# Validação da versão comercial

Data: 24 de agosto de 2026

## Resultado

A versão comercial da landing, o checklist e suas integrações passaram nas validações estruturais e funcionais disponíveis no ambiente de desenvolvimento.

## Verificações aprovadas

- Sintaxe de assets/js/book.js e assets/js/app.js.
- Sintaxe dos scripts Python sem gerar novos artefatos de bytecode.
- Parse completo de assets/css/book.css e assets/css/main.css.
- Um único h1 em cada página principal.
- Ausência de IDs HTML duplicados.
- Referências aria-labelledby válidas.
- Imagens com atributo alt.
- Botões com tipo explícito.
- Links em nova aba protegidos com noopener.
- JSON-LD válido para Book, Offer, FAQ, WebPage, CreativeWork e breadcrumbs.
- ISBN, preço, formato e varejista consistentes em toda a experiência.
- Ausência das referências antigas de Amazon e ISBN na interface ativa.
- Landing e checklist presentes no sitemap.
- Simulação dos eventos view_item, book_landing_view, book_cta_click, book_store_click e book_clube_autores_click.
- Propagação de utm_source e utm_medium para os eventos do livro.
- Smoke test HTTP 200 para homepage, landing, checklist, CSS, JavaScript, capa, sitemap e feed.
- Execução do fluxo local de reconstrução, refinamento editorial, índices e sitemap.
- Remoção do formulário de newsletter que apenas armazenava o e-mail no navegador; substituição por RSS real.

## Rotas para conferência após publicação

- https://www.cosmosweek.com/livro/vortice-maligno/
- https://www.cosmosweek.com/livro/vortice-maligno/checklist/

## Limite do teste

O binário do navegador automatizado não estava disponível no ambiente, portanto não foi gerada uma captura visual automatizada. Antes de ativar mídia paga, faça uma conferência final das duas rotas publicadas em Chrome e Safari, nas larguras de 390 px e 1440 px.

## Limite de atribuição

Como o checkout acontece no Clube de Autores, o site mede o clique de alta intenção para o varejista, mas não recebe automaticamente a confirmação da compra. Use os pedidos e royalties do painel do varejista para calcular custo por venda e retorno líquido.
