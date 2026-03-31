PACOTE REVISADO — COSMOS WEEK
Gerado em: 2026-03-31
Versão: 3.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MELHORIAS ENTREGUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CAPA DINÂMICA
   ✓ O hero principal deixou de depender só do flag "featured"
   ✓ Agora a capa usa prioridade por recência + score + trending + rotação
   ✓ O destaque muda ao longo do dia, evitando a mesma manchete fixa por dias

2. ARQUIVO CUMULATIVO
   ✓ O arquivo continua exibindo todas as matérias disponíveis
   ✓ O front agora preserva um cache local cumulativo para não perder matérias em refresh parcial
   ✓ Script auxiliar incluído: merge_posts_helper.py
     → Serve para mesclar lotes novos com o arquivo atual sem apagar artigos antigos

3. CURTIDAS / GOSTEI / COMENTÁRIOS
   ✓ Estrutura pronta com Giscus (GitHub Discussions)
   ✓ Reações funcionam como botão de curtir/gostei
   ✓ Comentários ficam públicos e persistentes para todos verem
   ✓ Arquivo incluído: giscus-config.js
     → Falta apenas preencher repoId e categoryId e trocar enabled para true

4. ARTIGOS MAIORES E MAIS LIMPOS
   ✓ Corpos dos artigos foram saneados para remover lixo de scraping e repetição genérica
   ✓ Página de artigo ganhou bloco “Síntese estruturada”
   ✓ Textos ficaram mais legíveis, maiores e mais informativos
   ✓ Mantido tom factual, sóbrio e sem humor editorial

5. O QUE FOI PRESERVADO
   ✓ Navegação
   ✓ Busca
   ✓ Alternância PT/EN
   ✓ Home, arquivo, páginas institucionais e layout base
   ✓ Consentimento / analytics / estrutura já funcional

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ATIVAÇÃO DE COMENTÁRIOS E REAÇÕES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivo: giscus-config.js

Passos:
1) Habilite GitHub Discussions no repositório do site
2) Instale/autorize Giscus no repositório
3) Em https://giscus.app/ copie:
   - repoId
   - categoryId
4) Cole no arquivo giscus-config.js
5) Troque:
   enabled: false
   por:
   enabled: true

Observação:
- Enquanto isso não for preenchido, a área de interação aparece pronta para ativação, mas não publica comentários ainda

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMO MANTER O ARQUIVO ACUMULANDO NAS PRÓXIMAS ATUALIZAÇÕES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Opção manual:
- Continue sempre adicionando novos artigos ao posts.json / posts.js sem apagar os antigos

Opção recomendada:
- Use o script:
  python merge_posts_helper.py posts.json novo_lote.json

Resultado:
- merged_posts.json
- merged_posts.js

Depois:
- renomeie os arquivos mesclados para posts.json e posts.js antes do upload

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARQUIVOS NOVOS NESTE PACOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- giscus-config.js
- merge_posts_helper.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORDEM DE UPLOAD RECOMENDADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1) index.html
2) posts.json
3) posts.js
4) giscus-config.js
5) merge_posts_helper.py (opcional, só para manutenção local)
6) demais arquivos institucionais, se desejar manter o pacote todo sincronizado
