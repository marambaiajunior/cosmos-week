# Relatório técnico de correção para nova revisão do Google AdSense

Data: 25 de abril de 2026  
Domínio: cosmosweek.com / www.cosmosweek.com  
Status observado nos screenshots: **Conteúdo de baixo valor**.

## Diagnóstico

A reprovação não está relacionada ao `ads.txt`, que já contém o publisher correto:

`google.com, pub-7289727408346815, DIRECT, f08c47fec0942fa0`

O problema principal é editorial e estrutural: o site tinha muitas páginas de notícias derivadas de fontes externas, com estrutura repetitiva, páginas em inglês duplicando a cobertura e um sitemap muito amplo. Para o AdSense, isso pode parecer um agregador/republicador em massa, mesmo quando há boa intenção editorial. A internet, como sempre, pune sutilezas com uma marreta algorítmica.

## Correções executadas neste pacote

1. **Redução do inventário indexável**
   - Mantidas como indexáveis apenas 40 matérias principais em português.
   - Marcadas com `noindex,follow`:
     - 202 matérias antigas/excedentes em `/noticia/`;
     - 242 páginas duplicadas em `/en/news/`.
   - Objetivo: reduzir sinal de conteúdo duplicado, reescrito ou excessivamente derivado de terceiros.

2. **Sitemap reconstruído**
   - Removidos URLs com parâmetros como `?page=` e `?lang=`.
   - Removidas páginas `/en/news/`.
   - Removidas matérias não selecionadas.
   - Novo sitemap contém 66 URLs:
     - páginas institucionais;
     - guias originais;
     - 40 matérias selecionadas em português.

3. **Arquivos de dados consolidados**
   - `all_posts.json` agora contém 40 itens, alinhado com o inventário público principal.
   - `posts.json` agora contém os mesmos 40 itens usados como superfície editorial de aprovação.
   - `assets/data/posts-index.json` foi preservado como índice principal resumido.

4. **Conteúdo original adicionado**
   - Criada a seção `/guias/`.
   - Adicionados 9 guias autorais:
     - Como distinguir ciência de pseudociência;
     - Como ler um paper científico;
     - Por que preprints não são prova final;
     - O que é espectroscopia;
     - Como a ciência detecta exoplanetas;
     - Matéria escura: o que sabemos;
     - O que significa “sigma” na ciência;
     - O que é uma evidência científica;
     - Por que a ciência muda de ideia.
   - Objetivo: criar base autoral evergreen, com valor próprio para o leitor.

5. **Remoção de elementos comerciais antes da aprovação**
   - Removidos blocos flutuantes patrocinados e placeholders publicitários das páginas institucionais principais.
   - Objetivo: evitar a impressão de página construída para anúncios ou patrocinadores antes da aprovação.

6. **Política de privacidade reforçada**
   - Adicionadas informações explícitas sobre:
     - cookies de publicidade do Google;
     - anúncios personalizados;
     - Google Ads Settings;
     - aboutads.info;
     - fornecedores terceirizados.
   - Aplicado também na versão inglesa da política de privacidade.

7. **Navegação reforçada**
   - Adicionado link para “Guias” na navegação principal.
   - Inserido bloco de guias originais nas páginas principais em português.

## Validação local

- `ads.txt`: presente e correto.
- `sitemap.xml`: recriado sem páginas duplicadas de notícia em inglês.
- `robots.txt`: aponta para o sitemap correto.
- Matérias indexáveis em português: 40.
- Notícias antigas ou duplicadas marcadas como `noindex`: 444 páginas.
- Guias autorais criados: 9 páginas + índice.
- Páginas sem meta robots: 0.

## Próximo passo recomendado

1. Substituir os arquivos do repositório pelos arquivos deste pacote.
2. Fazer commit e push.
3. Aguardar o deploy do GitHub Pages.
4. Abrir:
   - `https://www.cosmosweek.com/ads.txt`
   - `https://www.cosmosweek.com/sitemap.xml`
   - `https://www.cosmosweek.com/guias/`
   - `https://www.cosmosweek.com/politica-de-privacidade.html`
5. Confirmar que as páginas carregam corretamente.
6. No Google AdSense, marcar que os problemas foram corrigidos e clicar em **Pedir revisão**.

## Observação importante

Esta correção melhora muito o perfil editorial do site, mas não há garantia matemática de aprovação. O AdSense não publica uma fórmula exata de aprovação. O objetivo aqui foi remover os sinais mais prováveis de baixo valor: excesso de republicação, duplicação bilíngue, sitemap inchado, páginas antigas indexáveis e ausência de uma base autoral forte.
