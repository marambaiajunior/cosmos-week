# Pacote completo corrigido do Cosmos Week

## O que mudou neste pacote

1. `fetch_news.py`
   - usa `GEMINI_API_KEY` do GitHub Secrets para revisão final de português
   - corrige gramática, ortografia, pontuação, coesão, coerência e repetições óbvias
   - preserva a estrutura HTML do corpo e rejeita revisão insegura do Gemini
   - extrai mídia adicional da fonte original (`feed_media` e `fetch_page_media`)
   - salva essas mídias no campo `media` de cada post
   - aborta a publicação quando o número de posts gerados fica abaixo do mínimo configurado

2. `index.html`
   - mantém a aparência geral do site, tipografia e identidade visual
   - renderiza imagens, vídeos HTML5 e embeds seguros dentro do corpo das matérias
   - distribui as mídias ao longo do texto: um bloco de mídia a cada dois parágrafos
   - deixa apenas o excedente no final, quando houver mais mídias do que pontos de inserção

3. `update.yml`
   - passa `GEMINI_API_KEY` do GitHub Secrets para o job
   - valida a saída antes do commit
   - bloqueia commit se `posts.json` vier vazio ou pequeno demais
   - bloqueia commit se `posts.js`, `feed.xml` ou `sitemap.xml` vierem inválidos

4. `posts.json`, `posts.js`, `feed.xml`, `sitemap.xml`
   - incluídos no pacote para você subir tudo de uma vez
   - esta sessão não tinha mais acesso ao acervo restaurado anterior
   - por isso, estes arquivos foram preenchidos com uma base inicial não vazia, composta por posts editoriais internos do próprio portal, apenas para o site não subir vazio
   - depois da primeira execução bem-sucedida da automação, esses arquivos serão naturalmente substituídos pelas matérias reais coletadas das fontes

## Ordem recomendada

1. Substituir todos os arquivos do pacote no repositório
2. Fazer commit e push
3. Rodar manualmente a workflow `Atualizar notícias`
4. Conferir se as matérias reais substituíram a base inicial

## Arquivos incluídos

- fetch_news.py
- update.yml
- index.html
- posts.json
- posts.js
- feed.xml
- sitemap.xml
