# Baseline: PASS

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../../projeto/STATE.md) · [RDP](../../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Commit inicial: 0409f26. `docker compose build`: PASS.
`docker compose run --rm app pytest -q -W error`: **148 passed em 19,85 s**.
A imagem foi construída antes das alterações T1.

As próximas verificações usam o código atual, mesmo antes do rebuild de fim de fase:

```bash
docker compose run --rm -v "$PWD/src:/app/src:ro" -v "$PWD/tests:/app/tests:ro" app pytest -q -W error
```

Executar na raiz `climaprev`. Redis da stack `climaprev` foi criado nesta sessão e
permanece disponível até a revisão final. Nenhum volume preexistente foi removido.
