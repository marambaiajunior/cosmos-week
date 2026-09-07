# Cosmos Week

> Versão corrigida de 7 de setembro de 2026. Para instalar, leia **ATUALIZAR-GITHUB.md**. O diagnóstico e os resultados estão em **RELATORIO-CORRECOES-2026-09-07.md**.

Portal bilíngue de notícias científicas, com cobertura de astronomia, astrofísica, cosmologia, física e outras fronteiras da ciência.

## Experiência do site

- visual editorial responsivo para desktop, tablet e celular;
- matérias abertas dentro do mesmo portal, sem recarregar a página;
- URLs reais preservadas para compartilhamento, SEO e abertura em nova aba;
- histórico do navegador compatível com **Voltar** e **Avançar**;
- páginas estáticas individuais como fallback e para mecanismos de busca;
- navegação por tema, busca, arquivo PT/EN e identificação de preprints;
- acessibilidade com foco visível, navegação por teclado e movimento reduzido;
- índices compactos; a busca carrega o arquivo completo sob demanda e mostra resultados em páginas de 30 itens.

## Publicação no GitHub Pages

O repositório já inclui dois fluxos em `.github/workflows`:

1. `deploy.yml` publica o site sempre que há um push humano na branch `main`.
2. `update.yml` atualiza as notícias diariamente, recria os índices e publica a versão atualizada.

No GitHub, abra **Settings → Pages** e selecione **GitHub Actions** como fonte. Confirme também o domínio `www.cosmosweek.com` e a opção de HTTPS.

> Um arquivo ZIP enviado como arquivo único ao GitHub não é descompactado nem publicado. Extraia este pacote sobre um clone do repositório e envie os arquivos com GitHub Desktop ou Git.

## Atualização local dos dados

O gerador principal continua em `scripts/fetch_news.py`. Depois de atualizar `all_posts.json`, recrie o índice público com:

```bash
node scripts/build_archive_index.mjs
node scripts/upgrade_shell_pages.mjs
node scripts/build_sitemap.mjs
```

## Estrutura principal

- `index.html`: shell editorial e metadados da página inicial;
- `livro/vortice-maligno/`: landing comercial do livro;
- `livro/vortice-maligno/checklist/`: material gratuito e imprimível;
- `CAMPANHA-VORTICE-MALIGNO.md`: plano de divulgação, UTMs, eventos e criativos;
- `assets/css/modern.css`: camada visual moderna;
- `assets/js/app.js`: conteúdo, busca e navegação integrada;
- `assets/data/posts-index.json`: seleção recente da home;
- `assets/data/archive-index.json`: índice leve do arquivo completo;
- `noticia/` e `en/news/`: páginas estáticas individuais;
- `scripts/`: automação editorial e geração de dados.

## Licença e conteúdo

O código, a identidade editorial e o conteúdo pertencem aos respectivos titulares. As fontes originais permanecem identificadas em cada matéria.

## Validação sem consultar serviços externos

```bash
python scripts/normalize_book_paths.py
python scripts/validate_site.py
python scripts/validate_vortice.py
python -m unittest discover -s scripts -p 'test_*.py'
node scripts/test_app_logic.mjs
node scripts/test_analytics_consent.mjs
```

Use Python 3.11 ou superior e Node.js 24. Não há dependências adicionais para esses comandos. A verificação opcional das dimensões das imagens usa Pillow quando instalado.
