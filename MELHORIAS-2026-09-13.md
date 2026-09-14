# Melhorias do Cosmos Week — 13/09/2026

O portal continua estático, bilíngue e compatível com GitHub Pages. As alterações preservam URLs de matérias, conteúdo editorial, fontes, loja do livro, checklist e consentimento de analytics.

## Estrutura revisada

- `scripts/fetch_news.py`: coleta, seleção, revisão opcional com Gemini e geração das páginas PT/EN, RSS e metadados. Os testes cobrem indisponibilidade, limites da API e preservação da edição anterior.
- `scripts/editorial_refine.py` e regras JSON: curadoria, classificação e pontuação. Mantidos para preservar a política editorial.
- `assets/js/app.js`: home, arquivo, busca, idiomas, navegação interna e leitura de matérias estáticas sob demanda.
- `assets/js/article-layout.js`: apresentação das matérias abertas diretamente por URL.
- `livro/vortice-maligno/`: apresentação do livro, estrutura da obra, modelo conceitual, autor, perguntas frequentes e compra externa. O checklist continua gratuito e imprimível.
- Workflows: atualização diária das notícias, publicação no Pages e nova validação de pull requests sem acesso a segredos ou serviços editoriais externos.

## Mudanças

1. Índice do arquivo com dicionário de valores e nomes de campos compartilhados, sem perda de títulos, resumos, palavras-chave ou idiomas. O formato anterior permanece disponível. O leitor rejeita referências inválidas e permite tentar novamente.
2. CSS da promoção separado do CSS completo da landing e do checklist. As páginas do portal passam a solicitar apenas `book-promo.css`. O sincronizador conserva essa escolha nas atualizações automáticas.
3. Landing com apresentação e ações antes da capa também na ordem do HTML, título mais legível, capa responsiva menor, botões e navegação mais claros, contraste do menu corrigido e menos sombras/desfoques decorativos. Preservados texto, imagens, preço e destino da compra existentes.
4. Barra de leitura usa transformação visual sincronizada ao próximo frame, em vez de alterar largura a cada evento de rolagem. Imagens usam decodificação assíncrona.
5. Removido o fundo decorativo fixo do portal. Corrigidos verificadores de nomes de pastas e leitura UTF-8 no Windows.

## Medidas locais

Medidas do conteúdo existente no commit base `82c4350f6ff3931654ebed151849ef0abcc5dbdc`; não representam uma pontuação Lighthouse nem uma medição de produção.

| Recurso | Antes | Depois |
|---|---:|---:|
| CSS do livro solicitado pela home | 32.428 bytes | 2.753 bytes |
| Índice do arquivo, sem compressão HTTP | 3.693.387 bytes | 2.618.378 bytes |
| Índice comprimido com gzip local | 821.118 bytes | 784.627 bytes |

O CSS específico da promoção fica aproximadamente 91,5% menor. O índice fica 29,1% menor sem compressão e 4,4% menor com gzip. Brotli local produziu 533.994 bytes no formato antigo e 552.874 no novo; o ganho de transferência depende da compressão aplicada pelo servidor. O formato compacto exige decodificação no cliente; a melhoria de tempo real em aparelhos deve ser medida após publicação. A home continua carregando apenas o índice recente de 40 matérias; o arquivo completo tem 1.984 registros e só é solicitado sob demanda.

## Validação

- Verificador de rotas, arquivos locais, IDs, JSON-LD, índices bilíngues, RSS e sitemap: 4.348 páginas HTML, zero erros.
- Verificador de landing/checklist: zero falhas.
- 11 testes de lógica da aplicação, incluindo equivalência completa entre índices e rejeição de índices inválidos.
- 11 testes Python de resiliência e geração editorial.
- Testes de consentimento de analytics aprovados; JavaScript verificado quanto à sintaxe.

Execute os comandos do README antes de publicar. O deploy regenera os índices. A validação de PR não publica o site. A revisão não incluiu uma auditoria científica individual de cada notícia, transações na loja, chamadas Gemini reais ou medição de Core Web Vitals em produção.
