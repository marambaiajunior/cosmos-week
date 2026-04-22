# REPORT_FASE5.md

## 1. Resumo editorial da fase

A Fase 5 concentrou-se exclusivamente no padrão editorial das páginas de artigo e nos sinais de credibilidade jornalística do Cosmos Week.

Nesta etapa, o projeto passou a tratar a página de notícia como uma página editorial completa, e não apenas como um container de texto com imagem. O foco foi reforçar confiança, leitura, rastreabilidade da fonte e consistência entre as versões em português e inglês.

## 2. Template ideal definido para os artigos

O template desta fase foi reestruturado para conter:

- breadcrumbs visíveis no topo da matéria;
- cabeçalho editorial com tema, idioma, tipo de cobertura e nível de evidência;
- assinatura institucional explícita da redação do Cosmos Week;
- blocos de metadados com publicação, atualização, leitura e enquadramento;
- painel lateral editorial com:
  - leitura da fonte,
  - contexto editorial,
  - ferramentas de copiar link e compartilhar,
  - ligação para a página de padrões editoriais,
  - leitura relacionada;
- melhoria de conforto de leitura com hierarquia visual mais clara, largura útil controlada e separação entre corpo principal e apoio editorial;
- consistência estrutural entre PT e EN.

## 3. Melhorias aplicadas nos artigos

Foram geradas versões completas melhoradas dos seguintes artigos, em PT e EN:

- clinical-trial-results-support-use-of-weekly-extended-release-buprenorphine-for-treatment-of-opi
- sun-observing-satellite-uses-artificial-eclipse-to-capture-the-solar-wind
- cloudy-with-a-chance-of-metals-indications-of-co-2-in-the-atmosphere-of-gj-1214-b-from-high-reso

Melhorias reais aplicadas:
- inclusão de breadcrumbs visíveis;
- novo cabeçalho editorial;
- exibição mais forte de tipo de cobertura e nível de evidência;
- ferramentas de copiar link e compartilhar a matéria;
- ligação direta à página de padrões editoriais;
- bloco de leitura relacionada carregado a partir do índice do site;
- painel lateral de credibilidade e contexto;
- reforço de legibilidade no corpo do texto.

## 4. Páginas institucionais ajustadas

As páginas de padrões editoriais foram atualizadas:

- `/padroes/index.html`
- `/en/standards/index.html`

Agora elas explicam:
- como ler uma matéria do Cosmos Week;
- como funciona a escala de evidência do portal;
- quais compromissos editoriais valem para releases, papers, jornalismo científico e preprints;
- por que esse padrão melhora credibilidade e UX.

## 5. Justificativa jornalística e UX

As mudanças desta fase existem por uma razão simples: credibilidade editorial não pode depender de suposição.

Uma matéria científica precisa informar, ao primeiro olhar:
- de onde veio a informação;
- quão robusta ela é;
- o que pertence à fonte original;
- o que pertence ao enquadramento editorial do portal;
- para onde o leitor pode ir em seguida.

Isso melhora:
- confiança;
- escaneabilidade;
- retenção;
- compartilhamento limpo da URL;
- coerência institucional entre páginas;
- percepção de portal científico sério, em vez de espelho automático de feed.

## 6. Arquivos completos alterados nesta fase

### Template / base
- `scripts/fetch_news.py`
- `assets/css/main.css`

### Páginas institucionais
- `padroes/index.html`
- `en/standards/index.html`

### Artigos completos regenerados
- `noticia/clinical-trial-results-support-use-of-weekly-extended-release-buprenorphine-for-treatment-of-opi/index.html`
- `en/news/clinical-trial-results-support-use-of-weekly-extended-release-buprenorphine-for-treatment-of-opi/index.html`
- `noticia/sun-observing-satellite-uses-artificial-eclipse-to-capture-the-solar-wind/index.html`
- `en/news/sun-observing-satellite-uses-artificial-eclipse-to-capture-the-solar-wind/index.html`
- `noticia/cloudy-with-a-chance-of-metals-indications-of-co-2-in-the-atmosphere-of-gj-1214-b-from-high-reso/index.html`
- `en/news/cloudy-with-a-chance-of-metals-indications-of-co-2-in-the-atmosphere-of-gj-1214-b-from-high-reso/index.html`

## 7. O que fica para a Fase 6

Sugestão de escopo futuro, sem executar agora:
- aprofundar páginas de autor / equipe editorial;
- política formal de correções;
- página institucional específica sobre fontes e metodologia de curadoria;
- cards de related reading ainda mais inteligentes por tema, evidência e fonte;
- refinamento semântico e visual do corpo dos artigos longos;
- possíveis selos editoriais avançados por tipo de cobertura.

## 8. Observação de compatibilidade

As mudanças foram desenhadas para preservar compatibilidade com as fases anteriores:
- não removem a estrutura bilíngue existente;
- não quebram a rota dinâmica já usada no site;
- mantêm o padrão de diretórios do repositório;
- reforçam os arquivos estáticos sem exigir reestruturação total do projeto.
