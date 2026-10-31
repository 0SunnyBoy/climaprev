# Contexto histórico da main — 24/09/2026

> Registro histórico preservado na promoção de 31/10/2026. Não descreve o estado atual. Consulte [STATE vigente](../projeto/STATE.md) e [RDP](RELATORIO-PENDENCIAS-2026-10-20.md).

Atualizado em 24 de setembro de 2026. Branch de trabalho: `develop`.

## Publicação atual

O estado atual do rework do frontend, das atualizações de backend,
infraestrutura, testes e documentação está publicado em `origin/develop` no
commit `b671d9b`.

A `main` permanece como branch estável e contém o merge anterior do projeto.
Não houve deploy em produção nem publicação de segredos reais.

## Estado técnico

- O frontend usa Vue 3, TypeScript e Vite.
- O Nginx entrega o frontend e encaminha as rotas públicas da API.
- O FastAPI funciona como backend API e não serve HTML ou assets.
- A política ativa de risco é `reference-v1`, heurística e orientativa.
- O horizonte de consulta é de até sete dias inclusivos.
- A consulta permanece anônima e não persiste localização no navegador.
- A pasta `tmp/` foi removida do repositório e passou a ser ignorada pelo Git.

## Validações recentes

As validações do frontend passaram dentro do Docker:

- Vitest: 4 testes aprovados.
- ESLint: aprovado.
- Build TypeScript/Vite: aprovado.
- Aceitação no navegador: aprovada.
- `nginx -t`: aprovado.

As validações de homologação real continuam dependentes de certificados,
segredos e infraestrutura próprios do ambiente. Não copie `.homolog/` para o
repositório.

## Como retomar

1. Conferir `git status --short --branch` antes de editar.
2. Ler [PROJECT](../projeto/PROJECT.md), [STATE](../projeto/STATE.md) e [ROADMAP](../projeto/ROADMAP.md).
3. Consultar a documentação técnica diretamente afetada pela mudança.
4. Descrever processo, ganho, impacto e validação antes de implementar.
5. Executar os testes direcionados e depois a suíte relevante dentro do Docker.
6. Atualizar a documentação correspondente ao comportamento alterado.

Preserve o fallback `reference-v1`, não publique segredos e não altere a
`main` diretamente sem revisão.
