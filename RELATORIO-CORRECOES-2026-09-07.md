# Cosmos Week — revisão técnica de 7 de setembro de 2026

## Diagnóstico confirmado

A falha final do GitHub Actions era a ausência de `livro/vortice-maligno/checklist/index.html`. A página estava em `Livro/vortice-maligno/checklist/index.html`. O validador existente reproduziu três falhas relacionadas a essa diferença de maiúsculas no ambiente Linux.

O mesmo log apresentou um problema separado: HTTP 429 por créditos pré-pagos esgotados no Gemini e alternativas de modelos que respondiam 404. O fluxo repetia chamadas até atingir seu limite de tempo.

## Correções

- Checklist movido para a rota canônica minúscula e alias redundante removido. Migração controlada nos workflows para uploads feitos sobre o checkout antigo.
- Validação integral antes da coleta de notícias, além da validação posterior. Uma rota ausente é detectada antes de gastar tempo com serviços externos.
- Interrupção imediata da revisão por IA para créditos esgotados, quota diária indisponível ou acesso negado. Retentativas limitadas para problemas transitórios, com respeito ao tempo restante e ao `Retry-After` informado pelo servidor.
- Modelos antigos removidos das alternativas fixas. Um erro 404 no principal permite usar a alternativa explicitamente configurada.
- Chave Gemini enviada em cabeçalho; mensagens de erro não imprimem a chave ou o conteúdo bruto do provedor.
- Edição anterior preservada quando não há notícias elegíveis e existe um snapshot válido.
- Cache de notícias deixa de impedir a consulta à edição atual. Cache limitado a 80 resumos; o tamanho do cache não é confundido com arquivo completo.
- Busca passa a carregar o índice histórico sob demanda, manter o termo na URL e exibir 30 resultados por vez, com carregamento adicional.
- Falhas de atualização são informadas corretamente. Falhas do arquivo exibem aviso e possibilidade de tentar novamente.
- Troca de idioma carrega o corpo correspondente, inclusive legendas das imagens. Respostas atrasadas não devem substituir uma página para a qual o leitor já navegou.
- `book.js` deixa de registrar um segundo controlador de menu nas páginas gerais. Tecla Escape e estados acessíveis mantidos no menu do livro.
- Campos de busca e alvos de toque ajustados para uso no celular. Textos de orientação ao visitante foram simplificados.
- Escape de texto em cards, corpo de leitura integrado, legendas e destaques para evitar interpretar texto do feed como HTML.
- Estilos repetidos nas páginas de matérias movidos para dois arquivos CSS compartilhados, preservando as duas variantes existentes.

## Reduções medidas nos arquivos

| Item | Antes | Depois | Redução |
| --- | ---: | ---: | ---: |
| Índice da página inicial | 344.510 bytes | 99.979 bytes | 70,98% |
| Índice do arquivo | 4.325.301 bytes | 3.489.270 bytes | 19,33% |
| HTML repetido nas matérias | — | — | 32.779.704 bytes removidos das páginas |

Os dois CSS compartilhados somam 16.975 bytes. As medidas são dos arquivos sem compressão HTTP; não equivalem a uma promessa de redução percentual no tempo de carregamento. A velocidade real também depende de rede, imagens externas, cache e dispositivo.

## Preservação do conteúdo

A comparação com o ZIP original confirmou:

- 4.096 páginas de matérias com conteúdo e regras CSS idênticos, descontando apenas a troca do bloco de estilos pelo link para o arquivo compartilhado.
- `posts.json`, `posts.js`, `all_posts.json` e `feed.xml` preservados byte a byte.
- 40 matérias na edição atual e 1.874 registros no índice histórico, como na base recebida. Páginas antigas que já estavam fora dessa base continuam disponíveis por seus endereços.
- Livro, checklist, guias, páginas institucionais, imagens existentes e domínio preservados.

## Validação

- 4.128 páginas HTML verificadas: zero referências internas ou recursos locais ausentes, zero IDs duplicados e JSON-LD válido.
- Validação existente do Vórtice Maligno: zero falhas após a correção.
- 11 testes Python: créditos esgotados, quotas, autorização, modelo removido, limite de tempo, indisponibilidade, preservação de dados e geração bilíngue sem rede.
- 9 testes de lógica JavaScript: cache, erros, busca paginada, idioma, navegação assíncrona, escape de texto e menu.
- Testes de consentimento de analytics aprovados.
- Sintaxe de 4.097 scripts inline e 6 arquivos JavaScript públicos, scripts Python, YAML e comandos Bash dos workflows validada.
- Migração das duas rotas antigas reproduzida com arquivos do ZIP original; segunda execução sem alterações.

As automações incluem esses testes para detectar regressões nas próximas execuções. Eles não substituem teste visual em navegador ou a execução autenticada do GitHub Actions. Não foram consumidos créditos de IA durante a validação.

## Referências técnicas consultadas

- [Diagnóstico de erros do Gemini](https://ai.google.dev/gemini-api/docs/troubleshooting): tratamento de erros transitórios e limites de retentativas.
- [Catálogo oficial de modelos Gemini](https://ai.google.dev/gemini-api/docs/models): modelo padrão e alternativa configurável.
- [GitHub Pages com workflows personalizados](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
- [Concorrência no GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency): a configuração existente `queue: max` é válida e foi preservada.
- [RSS oficial do JPL](https://www.jpl.nasa.gov/rss/): o endereço configurado permanece o divulgado pela instituição.
