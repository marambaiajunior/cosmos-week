# Atualizar o Cosmos Week no GitHub

Esta é uma versão completa do site, baseada no ZIP enviado em 7 de setembro de 2026. Inclui as páginas existentes, imagens, dados, scripts e os dois workflows do GitHub Actions.

## Enviar os arquivos

1. Extraia o ZIP. Abra a pasta `cosmos-week-main` dentro dele.
2. No GitHub Desktop, abra ou clone `marambaiajunior/cosmos-week` e selecione a branch `main`. Use **Repository → Show in Explorer** (ou **Show in Finder**).
3. Copie **o conteúdo** de `cosmos-week-main` para a raiz do repositório local, substituindo os arquivos correspondentes. `index.html`, `assets`, `scripts` e `.github` devem ficar diretamente nessa raiz. Preserve a pasta `.git` do clone.
4. Inclua a pasta `.github` do pacote: ela contém a correção das automações. Não coloque `cosmos-week-main` como uma subpasta dentro do site.
5. No GitHub Desktop, revise as alterações, faça **Commit to main** e **Push origin**. É esperado que mais de 4.000 páginas apareçam modificadas: o CSS repetido foi movido para arquivos compartilhados; o texto das matérias foi preservado.
6. No GitHub, confirme **Settings → Pages → Source: GitHub Actions**. Acompanhe **Actions → Publicar site** até a conclusão.

O GitHub não descompacta um ZIP enviado como arquivo único. Envie os arquivos extraídos com GitHub Desktop ou Git.

## Pasta do livro

A pasta correta é `livro`, com L minúsculo. A página do checklist agora está em `livro/vortice-maligno/checklist/index.html`.

Se a cópia sobre o repositório antigo deixar também a pasta `Livro`, os workflows executam a migração dos dois arquivos legados antes da validação. Se houver conteúdo diferente entre as duas versões, o processo para com uma mensagem explícita para evitar sobrescrever uma alteração. A próxima atualização de notícias registra a remoção das rotas duplicadas no Git.

Os endereços antigos com `Livro` são encaminhados pela página 404 para as rotas corretas quando o navegador permite JavaScript.

## Gemini e a atualização de notícias

O log anexado mostrou **créditos pré-pagos esgotados**. O site pode ser publicado e navegado independentemente dessa conta. O código agora interrompe a revisão por IA diante desse erro e continua com o conteúdo de fallback do gerador, sem afirmar que ele foi revisado.

Para voltar a usar a revisão do Gemini, regularize os créditos no projeto correspondente no [Google AI Studio](https://ai.studio/projects). Não é necessário trocar uma chave válida apenas porque faltam créditos.

Configuração no GitHub, em **Settings → Secrets and variables → Actions**:

- **Secret `GEMINI_API_KEY`**: mantenha sua chave fora dos arquivos do site.
- **Variable `GEMINI_MODEL`**: opcional. Tem prioridade sobre o secret legado com o mesmo nome. Sem configuração, usa `gemini-3.5-flash-lite`.
- **Variable `GEMINI_MODEL_FALLBACKS`**: opcional, lista separada por vírgulas. O padrão é `gemini-3.5-flash-lite`. Modelos alternativos são usados para indisponibilidade de modelo, não para contornar uma quota esgotada.

Os modelos antigos `gemini-2.0-flash`, `gemini-2.0-flash-lite` e `gemini-1.5-flash` foram retirados da lista fixa de alternativas. Um modelo principal legado que retorne 404 não impede a tentativa da alternativa configurada.

Para testar a atualização diária após publicar, abra **Actions → Atualizar notícias → Run workflow**. A programação diária existente foi mantida.

## O que foi validado e o que depende do ambiente externo

Foram executados testes locais de arquivos, rotas, dados, geração de matérias, lógica de navegação e falhas simuladas de API. A publicação no seu repositório e a cobrança/créditos da conta Google não foram executadas nesta revisão. Não houve teste visual em navegador nem medição de Core Web Vitals.

As recusas 403, respostas 404 ou XML inválido de provedores de RSS não derrubam o gerador. São problemas externos que podem continuar acontecendo. O endereço do JPL foi mantido porque é o endereço divulgado pela própria NASA/JPL; não foram inventados endpoints alternativos ou contornados bloqueios.
