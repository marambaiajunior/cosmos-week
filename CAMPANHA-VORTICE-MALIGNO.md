# Campanha Vórtice Maligno

Plano operacional para transformar o livro em uma campanha mensurável, sem prometer vendas garantidas e sem confundir clique com compra.

Versão: 24 de agosto de 2026

## O que esta versão já entrega

- Landing comercial: https://www.cosmosweek.com/livro/vortice-maligno/
- Checklist gratuito: https://www.cosmosweek.com/livro/vortice-maligno/checklist/
- Página de compra: https://clubedeautores.com.br/livro/vortice-maligno
- Imagem para links e anúncios horizontais: assets/img/livro/vortice-maligno-og.jpg, 1200 × 630
- Capa em WebP e JPG
- GA4 com eventos de produto, CTAs, varejista, FAQ e checklist
- Parâmetros UTM preservados nos eventos do livro
- Barra de compra para celular e CTAs distribuídos pela página

## A limitação que precisa orientar a campanha

O pagamento ocorre no Clube de Autores. O Cosmos Week consegue medir a visita à landing e o clique que leva ao varejista, mas não recebe automaticamente a confirmação da compra.

Por isso:

- book_store_click representa intenção de compra, não venda;
- não chame esse evento de purchase;
- confirme pedidos e royalties no painel do Clube de Autores;
- compare os pedidos reais com dias, campanhas e conteúdos que geraram cliques;
- não calcule retorno sobre anúncios usando o preço de capa: use o royalty líquido recebido por exemplar.

Enquanto o checkout externo não devolver conversões, a primeira campanha paga deve validar mensagens e cliques qualificados. A otimização automática para vendas só faz sentido quando uma venda puder ser registrada de forma confiável.

## Funil recomendado

| Entrada | Destino | Próxima ação | Medida |
|---|---|---|---|
| Post, vídeo, entrevista ou anúncio | Landing do livro | Clique no Clube de Autores | book_store_click |
| Conteúdo educativo ou anúncio frio | Checklist gratuito | Conhecer o livro | book_guide_view e book_cta_click |
| Artigo sobre desinformação | Landing ou varejista | Ler e comprar | book_cta_click |
| Leitor engajado | Convite para entrevista, palestra ou projeto | Contato por e-mail | Mensagens recebidas |

Use sempre a landing do Cosmos Week como destino principal dos anúncios. Ela explica o livro, mede a origem e prepara o leitor antes do checkout.

## Convenção de UTMs

Use nomes minúsculos, sem acentos e sem espaços.

| Campo | Regra | Exemplo |
|---|---|---|
| utm_source | Plataforma ou parceiro | instagram |
| utm_medium | Tipo de distribuição | paid_social |
| utm_campaign | Campanha permanente | nao_basta_refutar |
| utm_content | Criativo específico | video_por_que_inteligentes_v1 |
| utm_term | Segmento, somente quando útil | amplo_br |

Exemplos prontos:

- Instagram orgânico: https://www.cosmosweek.com/livro/vortice-maligno/?utm_source=instagram&utm_medium=organic_social&utm_campaign=nao_basta_refutar&utm_content=carrossel_mente_rede_identidade
- Instagram pago: https://www.cosmosweek.com/livro/vortice-maligno/?utm_source=instagram&utm_medium=paid_social&utm_campaign=nao_basta_refutar&utm_content=video_por_que_inteligentes_v1
- Facebook pago: https://www.cosmosweek.com/livro/vortice-maligno/?utm_source=facebook&utm_medium=paid_social&utm_campaign=nao_basta_refutar&utm_content=imagem_mais_fatos_v1
- Checklist: https://www.cosmosweek.com/livro/vortice-maligno/checklist/?utm_source=instagram&utm_medium=organic_social&utm_campaign=nao_basta_refutar&utm_content=checklist_7_perguntas
- Entrevista ou podcast: https://www.cosmosweek.com/livro/vortice-maligno/?utm_source=nome_do_canal&utm_medium=podcast&utm_campaign=nao_basta_refutar&utm_content=entrevista_01

O Google recomenda parâmetros UTM para identificar as campanhas que enviam tráfego. Referência oficial: https://support.google.com/analytics/answer/10917952

## Eventos para acompanhar no GA4

| Evento | Significado correto | Pode virar evento principal? |
|---|---|---|
| view_item | Visualização da landing como produto | Não é venda |
| book_landing_view | Entrada na landing | Diagnóstico |
| book_cta_click | Clique em qualquer CTA do ecossistema | Diagnóstico |
| book_store_click | Saída para o Clube de Autores | Sim, como intenção de compra |
| book_guide_view | Visualização do checklist | Diagnóstico |
| book_guide_click | Acesso ao checklist | Diagnóstico |
| book_guide_share | Tentativa de compartilhar o checklist | Diagnóstico |
| book_guide_print | Impressão ou salvamento em PDF | Diagnóstico |
| book_faq_open | Objeção ou dúvida aberta | Pesquisa de mensagem |

O evento recomendado pelo GA4 para visualizar um produto é view_item. Referências oficiais:

- https://support.google.com/analytics/answer/9267735
- https://support.google.com/analytics/answer/12200568

No GA4, marque book_store_click como evento principal somente com o nome mental correto: ele mede um clique de alta intenção, não uma compra concluída.

## Antes de investir

1. Abra o Clube de Autores e confirme preço, disponibilidade, ISBN e descrição.
2. Faça um pedido de teste ou percorra o fluxo até a etapa anterior ao pagamento.
3. Abra a landing em celular e desktop.
4. Aceite somente analytics no aviso de cookies e verifique os eventos no DebugView do GA4.
5. Clique em cada posição de CTA e confirme cta_location.
6. Registre quantos pedidos e royalties já existem antes da campanha.
7. Descubra o royalty líquido por exemplar. Esse número define o custo máximo sustentável por venda.
8. Crie um Meta Pixel real no Gerenciador de Eventos antes de instalar qualquer código de anúncios.

O Meta Pixel exige um ID pertencente à conta do anunciante. Não há ID no projeto e nenhum foi inventado. Instruções oficiais:

- Instalar o Meta Pixel: https://www.facebook.com/business/help/952192354843755
- Entender o Meta Pixel: https://www.facebook.com/business/help/742478679120153

Como o site é estático, a Conversions API exige um serviço ou endpoint no servidor. Ela não deve ser simulada apenas no navegador. Referência oficial: https://www.facebook.com/business/help/AboutConversionsAPI

## Estrutura inicial de anúncios

Quando o orçamento é pequeno, evite muitas campanhas e conjuntos concorrendo pelos mesmos poucos eventos.

- Uma campanha.
- Um conjunto de anúncios amplo para Brasil e português.
- Três anúncios com ângulos diferentes.
- Um único destino: a landing.
- Otimização inicial para visualização da landing enquanto não houver compra mensurável.
- Sete a quatorze dias sem mudanças diárias impulsivas, salvo erro evidente.

O próprio Meta recomenda consolidar conjuntos quando a fragmentação impede o aprendizado. Referências:

- https://www.facebook.com/business/help/950694752295474
- https://www.facebook.com/business/help/112167992830700

Não existe orçamento universal. Escolha um valor que possa perder integralmente como custo de aprendizado. Se precisar de uma referência operacional, use um teste limitado de 14 dias e não escale até conhecer royalty, pedidos reais e taxa de clique para o varejista.

## Os quatro ângulos criativos

### 1. Não basta refutar

Texto principal:

Mais fatos nem sempre vencem uma crença. Quando uma ideia oferece pertencimento, certeza e identidade, corrigi-la deixa de ser uma simples disputa de informações. Vórtice Maligno investiga por que isso acontece — e como reconstruir uma rota de retorno sem abandonar método, evidência ou humanidade.

Título: Não basta refutar.

Descrição: Livro impresso • 314 páginas.

CTA: Saiba mais.

### 2. Por que pessoas inteligentes?

Texto principal:

Por que pessoas inteligentes, instruídas e convencidas de pensar por conta própria podem ficar presas em crenças que rejeitam qualquer evidência contrária? A resposta não cabe em “ignorância”. Ela passa por mente, redes, pertencimento e custo de mudar de ideia.

Título: Como a dúvida vira identidade?

Descrição: Conheça Vórtice Maligno.

CTA: Saiba mais.

### 3. O mapa do Vórtice

Texto principal:

Da resiliência crítica ao fechamento militante: cinco posições para entender como critérios de evidência podem enfraquecer, mudar de fonte e acabar protegidos por identidade. O MVM não é diagnóstico. É um mapa para calibrar perguntas e intervenções.

Título: Reconheça os cinco níveis.

Descrição: Método, evidência e resiliência epistêmica.

CTA: Saiba mais.

### 4. Checklist gratuito

Texto principal:

Antes de acreditar ou compartilhar, faça sete perguntas: qual é a alegação, o que poderia refutá-la, qual é a fonte original, há comparação, o mecanismo é plausível, existem alternativas e houve correção independente? Abra o checklist gratuito do Cosmos Week.

Título: Sete perguntas em cinco minutos.

Descrição: Gratuito, sem cadastro e pronto para imprimir.

CTA: Saiba mais.

## Roteiro de vídeo de 30 segundos

0–4 s: “Mais fatos nem sempre vencem uma crença.”

4–10 s: “Porque uma crença pode deixar de ser apenas uma ideia. Ela pode virar pertencimento, reputação e identidade.”

10–18 s: “Vórtice Maligno mapeia como mente, redes e identidade se combinam — da resiliência crítica ao fechamento militante.”

18–25 s: “Não para humilhar quem erra. Para entender por que o erro resiste e como uma rota de retorno pode existir.”

25–30 s: “Vórtice Maligno. Conheça o livro no Cosmos Week.”

Na tela final: capa, cosmosweek.com/livro/vortice-maligno/ e “Livro impresso • 314 páginas”.

## Carrossel de seis telas

1. Mais fatos nem sempre vencem uma crença.
2. Porque a crença pode oferecer certeza.
3. A rede recompensa reação e repetição.
4. Mudar de ideia pode custar pertencimento.
5. Não basta refutar. É preciso entender o mecanismo.
6. Vórtice Maligno — conheça o livro.

Não altere a capa, não use selo de best-seller e não publique depoimentos sem autorização verificável.

## Calendário de 30 dias

| Período | Objetivo | Ações | Decisão |
|---|---|---|---|
| Dias 1–3 | Estabelecer a base | Validar preço, checkout, GA4, UTMs e pedidos atuais | Corrigir qualquer falha antes de anunciar |
| Dias 4–7 | Aquecer audiência | Publicar carrossel “Não basta refutar”, vídeo do autor e checklist | Identificar saves, compartilhamentos e cliques |
| Dias 8–14 | Testar mensagens | Rodar três anúncios no mesmo conjunto, com UTMs distintas | Não fragmentar por muitos interesses |
| Dias 15–18 | Ler sinais | Comparar custo por visualização qualificada, taxa de saída e pedidos reais | Pausar erros evidentes, não reagir a um único dia |
| Dias 19–24 | Iterar | Produzir nova versão do melhor ângulo e publicar trecho comentado pelo autor | Manter um controle e uma variação |
| Dias 25–30 | Consolidar | Buscar entrevista, live, newsletter parceira e contato educacional | Escalar somente se os pedidos confirmarem o sinal |

Ritmo orgânico sugerido por semana:

- um vídeo curto do autor;
- um carrossel conceitual;
- uma pergunta aberta com resposta em post posterior;
- uma chamada para o checklist;
- uma chamada direta para o livro;
- uma conversa, live ou participação em canal de terceiro.

## O que medir toda semana

| Métrica | Fórmula | Interpretação |
|---|---|---|
| Taxa de saída para o varejista | book_store_click ÷ sessões da landing | Força comercial da página e da mensagem |
| Taxa de entrada no checklist | book_guide_click ÷ sessões da landing | Interesse de quem ainda não está pronto para comprar |
| Checklist para livro | cliques ao livro ÷ book_guide_view | Capacidade do material gratuito de aprofundar |
| Custo por clique ao varejista | gasto ÷ book_store_click | Proxy, não custo por venda |
| Custo por venda confirmada | gasto ÷ pedidos atribuídos | Só usar com pedidos reais |
| Retorno líquido | royalties atribuídos − gasto | O número que decide escala |

Analise também:

- quais perguntas do FAQ são abertas com mais frequência;
- qual cta_location gera mais saídas;
- qual utm_content traz sessões engajadas;
- quais posts geram salvamentos e compartilhamentos, não apenas curtidas;
- quais dias de pico de book_store_click coincidem com pedidos.

## Regras de decisão

- Não declare um criativo vencedor depois de poucos cliques.
- Compare períodos equivalentes e UTMs corretas.
- Pause anúncios com erro de mensagem, link ou segmentação imediatamente.
- Para desempenho normal, espere dados comparáveis antes de mexer.
- Não aumente orçamento apenas porque o custo por clique caiu; confirme pedidos e royalty.
- Não use alcance, curtidas ou visualizações como prova de venda.
- Preserve o anúncio de controle ao testar uma nova variação.
- Se a landing recebe visitas mas quase ninguém vai ao varejista, revise oferta e objeções.
- Se há muitos cliques e poucos pedidos, investigue frete, prazo, confiança e preço no checkout externo.

## Crescimento além de anúncios

Para um livro com checkout externo e royalty limitado, distribuição editorial pode ser mais valiosa do que depender apenas de mídia paga.

- Entrevistas em podcasts de ciência, educação, psicologia e cultura digital.
- Lives com comunicadores científicos.
- Palestras para escolas, universidades, bibliotecas e organizações.
- Clubes de leitura com roteiro de discussão.
- Exemplares de cortesia para resenhistas, sem exigir avaliação positiva.
- Artigos derivados de conceitos do livro, sempre com CTA contextual.
- Parcerias com newsletters que aceitem link UTM próprio.
- Página ou proposta específica para compras institucionais quando houver processo comercial definido.

Peça avaliações honestas a leitores reais no canal de compra. Nunca invente depoimentos, números de vendas, urgência, escassez ou autoridade.

## Publicação e manutenção

Antes de cada nova onda:

1. Confirme o preço no Clube de Autores.
2. Teste todos os CTAs.
3. Gere uma UTM diferente para cada criativo.
4. Anote a data, o gasto, o criativo e o número de pedidos.
5. Arquive capturas dos relatórios.
6. Atualize o plano com o que foi aprendido.

O objetivo do primeiro ciclo não é “vender muito” por promessa. É encontrar uma mensagem que produza cliques qualificados e pedidos confirmados de forma repetível. A escala vem depois da evidência.
