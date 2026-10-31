# Validação e rastreabilidade documental

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

**Data:** 2026-09-23. **Escopo:** rastreabilidade atualizada após a análise
documental inicial de 2026-09-13. [Índice](../projeto/PROJECT.md).

Este arquivo preserva a validação da primeira entrega documental. A execução
posterior alterou código, testes e configuração; os resultados atuais estão
em [tasks](../planejamento/evolucao-climaprev/tasks.md) e nas evidências de cada
tarefa. A ausência de testes descrita abaixo se refere apenas à revisão inicial.

## Critérios da entrega inicial

- Documentos `.md` em português com navegação a partir de PROJECT e README.
- Arquitetura, fluxos, dados transmitidos, segurança e restrições cobertos.
- Diagrama de componentes, sequência de consulta e fronteiras de confiança.
- Comportamentos implementados separados de propostas e limitações.
- Referências locais apontando para arquivos existentes.
- Nenhuma alteração em código, testes, configuração de execução ou SIGFAS.

## Rastreabilidade

| Tema / requisito           | Evidência de implementação                                                                                 | Testes existentes relacionados                                                                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Local, período e unidade   | [Schema](../../src/climaprev/api/schemas/risk.py)                                                             | [Schema HTTP](../../tests/unit/api/test_risk_schema.py)                                                                                                                    |
| Contrato público e erros   | [Rota](../../src/climaprev/api/routes/risk.py), [handlers](../../src/climaprev/main.py)                          | [Endpoint](../../tests/integration/api/test_risk_endpoint.py), [envelope](../../tests/unit/api/test_error_envelope.py)                                                        |
| Normalização de previsão   | [Open-Meteo](../../src/climaprev/infrastructure/providers/open_meteo.py)                                      | [Contrato](../../tests/contract/providers/test_open_meteo_payload.py), [adaptador](../../tests/integration/providers/test_open_meteo_adapter.py)                              |
| Cache, lock e fallback     | [Serviço](../../src/climaprev/application/services/forecast_query.py)                                         | [Consulta](../../tests/integration/application/test_forecast_query.py), [cache](../../tests/integration/redis/test_cache.py), [lock](../../tests/integration/redis/test_lock.py) |
| Risco heurístico           | [Avaliador](../../src/climaprev/domain/risk_evaluator.py), [política](../../src/climaprev/domain/risk_policy.py) | [Avaliador](../../tests/unit/domain/test_risk_evaluator.py), [política](../../tests/unit/domain/test_risk_policy.py)                                                          |
| Alertas oficiais           | [Provider INMET](../../src/climaprev/infrastructure/providers/inmet_alerts.py), com adapter opcional sem configuração | [INMET](../../tests/integration/providers/test_inmet_alerts.py), [fallback](../../tests/unit/application/test_official_alerts.py) |
| IP, proxies e rate limit   | [Dependências](../../src/climaprev/api/deps.py)                                                               | [Dependências](../../tests/unit/api/test_deps.py), [limiter](../../tests/integration/redis/test_rate_limiter.py)                                                              |
| Logs e correlação          | [Observabilidade](../../src/climaprev/api/observability.py)                                                   | [Observabilidade](../../tests/unit/api/test_observability.py)                                                                                                              |
| Execução e perfil de carga | [Compose](../../docker-compose.yml)                                                                           | [Harness](../../tests/docker/test_docker_harness.py), [carga](../../tests/load/test_risk_load.py)                                                                             |

Os links de testes indicam cobertura relacionada disponível para consulta,
não comprovam que cada lacuna documentada já possui teste ou correção.

## Verificação documental

Foi feita leitura dos módulos de API, aplicação, domínio, infraestrutura e
configuração, além da documentação original e dos modelos SIGFAS. A revisão
atual também conferiu a separação `frontend/`/API, as rotas GET e POST de risco,
a busca de localidades e a integração básica com o INMET. Os links locais,
delimitadores de blocos de código e formato JSON de exemplo foram verificados
por script, e o diff foi inspecionado quanto a espaços inválidos.

Resultado da revisão inicial: **11 arquivos verificados** (dez novos
documentos e o README atualizado), **118 links locais válidos**, **seis
diagramas Mermaid** identificados e nenhum erro de link, bloco não fechado ou
JSON de exemplo.

Na revisão atual, **52 arquivos Markdown** foram verificados e todos os links
locais resolvem. `git diff --check` terminou sem erro.

Na revisão atual, foram executados dentro do Docker:

- `docker compose build app`;
- `docker compose run --rm app pytest -q -W error`: **341 passed**;
- `docker compose run --rm app ruff check src tests --ignore EXE002`;
- `docker compose run --rm app mypy src`: **41 source files**;
- `docker compose exec -T frontend nginx -t`: configuração válida;
- smoke HTTP do frontend, CSS e `/health/live`: respostas esperadas.

Na validação integrada da cópia correta em 23 de setembro, também foram
confirmados build das imagens, Redis saudável, página HTTP 200, health check
HTTP 200, assets hashados e contratos de segurança e POST do frontend. A
execução local do homolog real não foi feita porque `.homolog/` não está
presente nesta cópia.

Os diagramas foram revisados como texto; não houve renderização automatizada
Mermaid nesta revisão.

## Evidência histórica

O [handoff](../projeto/handoff.md) relata uma execução anterior de testes e
medições. As evidências nele referidas são históricas e não devem ser
reutilizadas como certificado de capacidade, segurança ou validação do estado
atual.

Para mudanças de código, usar os comandos Docker documentados no
[README](../../README.md) e registrar comando, resultado, ambiente e data. Para
avaliar integração externa, distinguir explicitamente provedor real de mock.
