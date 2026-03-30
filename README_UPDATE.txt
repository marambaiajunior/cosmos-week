PACOTE DEFINITIVO — COSMOS WEEK
Gerado em: 2026-03-30
Versão: 2.0 (pós-revisão técnica completa)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARQUIVOS INCLUÍDOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

index.html
  ✓ Consent Mode v2 com 3 estados (Aceitar tudo / Só analytics / Recusar)
  ✓ Cookie banner atualizado com 3 botões
  ✓ JS de consent migra silenciosamente valores legados ('granted' → 'analytics')
  ✓ Slots de anúncio pré-posicionados (leaderboard topo, sidebar, in-article)
    → Todos com display:none por padrão; descomente quando AdSense aprovar
  ✓ Bloco AdSense comentado no <head> com checklist de ativação
  ✓ og:image movida para asset próprio (assets/og-default.jpg)
  ✓ Schema.org NewsArticle com publisher correto (já estava OK)

anuncie.html
  ✓ GA4 + Consent Mode v2 adicionados

media-kit.html
  ✓ GA4 + Consent Mode v2 adicionados
  ✓ Campo "Versão / última atualização" dinâmico via localStorage
    → Para atualizar: abra o console nesta página e rode:
      localStorage.setItem('cw_mediakit_updated', new Date().toISOString());

politica-de-privacidade.html
  ✓ GA4 + Consent Mode v2 adicionados
  ✓ Seção 4 (Publicidade) reescrita — descreve os 3 níveis de consentimento

termos-de-uso.html
  ✓ GA4 + Consent Mode v2 adicionados

ads.txt
  ✓ Instruções de ativação expandidas
  ✓ Linha do AdSense comentada até o publisher ID real ser obtido

robots.txt
  (inalterado — estava correto)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O QUE VOCÊ AINDA PRECISA FAZER MANUALMENTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CRIAR IMAGEM OG (urgente para compartilhamentos funcionarem)
   → Crie a pasta assets/ no repositório
   → Adicione uma imagem 1200×630 px chamada og-default.jpg
   → Sugestão: fundo escuro (#0c0f17) com logo Cosmos Week centralizado

2. E-MAIL COMERCIAL
   → Substitua as referências ao @cosmos_week nos arquivos
     anuncie.html e politica-de-privacidade.html pelo e-mail oficial
     quando criado (ex: ads@seudominio.com)

3. MÉTRICAS DO GA4 NO MEDIA KIT
   → Preencha os "SUBSTITUIR" em media-kit.html com números reais
   → Atualize a data via console (instrução no README e na própria página)

4. QUANDO ADSENSE APROVAR (checklist completo):
   a) Pegue seu publisher ID (ca-pub-XXXXXXXXXXXXXXXX)
   b) Em index.html: descomente o <script> do AdSense no <head>
      e substitua o ID nas 3 ocorrências
   c) Em index.html: remova a linha ".ad-slot { display: none; }" no CSS
   d) Em index.html: descomente os blocos <ins class="adsbygoogle"> em
      #adSlotLeaderboard, #adSlotSidebar e no in-article
   e) Em ads.txt: descomente a linha google.com e substitua o ID
   f) Verifique em adstxt.guru após o deploy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O QUE NÃO FOI MODIFICADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- sitemap.xml (mantenha o atual do repositório)
- posts.js (o feed de artigos não foi alterado)
- Toda a lógica editorial, de busca e de renderização do index.html

ORDEM DE UPLOAD RECOMENDADA:
1) ads.txt
2) index.html
3) anuncie.html
4) media-kit.html
5) politica-de-privacidade.html
6) termos-de-uso.html
7) assets/og-default.jpg (criar a pasta e adicionar a imagem)
