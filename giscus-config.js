window.COSMOS_GISCUS = {
  enabled: true,
  repo: 'marambaiajunior/cosmos-week',
  repoId: 'R_kgDORytYJA',
  category: 'General',
  categoryId: 'DIC_kwDORytYJM4C5vwk',
  mapping: 'specific',
  strict: '1',
  reactionsEnabled: '1',
  emitMetadata: '0',
  inputPosition: 'bottom',
  theme: 'preferred_color_scheme'
};

/*
Arquivo ajustado para a arquitetura do Cosmos Week.

Motivo principal:
- O site abre artigos por query string, por exemplo: ?article=slug
- Por isso, usar mapping: 'pathname' faria todas as matérias compartilharem o mesmo caminho
  e poderia concentrar discussões diferentes no mesmo tópico.
- Com mapping: 'specific', o site usa o slug de cada artigo como identificador único.

Para instalar:
1) Substitua o arquivo giscus-config.js do repositório por este.
2) Faça commit e publique no GitHub Pages.
3) Abra uma matéria individual e role até "Reações e comentários".
*/