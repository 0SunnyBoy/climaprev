# Baseline: PASS

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../../projeto/STATE.md) · [RDP vigente](../../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

Commit inicial: 0409f26. `docker compose build`: PASS.
`docker compose run --rm app pytest -q -W error`: **148 passed em 19,85 s**.
A imagem foi construída antes das alterações T1.

As próximas verificações usam o código atual, mesmo antes do rebuild de fim de fase:

```bash
docker compose run --rm -v "$PWD/src:/app/src:ro" -v "$PWD/tests:/app/tests:ro" app pytest -q -W error
```

Executar na raiz `climaprev`. Redis da stack `climaprev` foi criado nesta sessão e
permanece disponível até a revisão final. Nenhum volume preexistente foi removido.
