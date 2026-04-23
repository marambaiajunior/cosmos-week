Ajuste aplicado nas páginas de notícia do Cosmos Week em 2026-04-23.

O que foi alterado:
- Nas páginas estáticas de notícia (PT e EN), o título/bloco editorial passa a ficar acima da imagem principal.
- Depois da imagem principal, o texto completo da matéria aparece primeiro.
- Blocos como metadados, pontos-chave, ferramentas e painéis editoriais passam para depois do texto.
- O corpo da matéria ganhou leitura em estilo livro: coluna central, texto justificado, parágrafos com indentação e capitular na primeira letra.
- O título e o corpo passaram a ficar centralizados visualmente.
- O script gerador (scripts/fetch_news.py) foi atualizado para manter esse comportamento em futuras rebuilds.
- O CSS principal também recebeu override para melhorar a leitura da versão dinâmica das matérias.

Arquivos principais alterados:
- assets/js/article-layout.js
- assets/css/main.css
- scripts/fetch_news.py
- todas as páginas em noticia/*/index.html
- todas as páginas em en/news/*/index.html

Substituição:
- Se quiser a solução mais simples, substitua o repositório inteiro pelo pacote completo.
- Se quiser apenas aplicar o patch, use o pacote com arquivos alterados.
