# Validação e rastreabilidade documental

**Data:** 2026-09-13. **Escopo:** documentação, leitura estática e coerência
com os arquivos presentes. [Índice](../PROJECT.md).

## Critérios desta entrega

- Documentos `.md` em português com navegação a partir de PROJECT e README.
- Arquitetura, fluxos, dados transmitidos, segurança e restrições cobertos.
- Diagrama de componentes, sequência de consulta e fronteiras de confiança.
- Comportamentos implementados separados de propostas e limitações.
- Referências locais apontando para arquivos existentes.
- Nenhuma alteração em código, testes, configuração de execução ou SIGFAS.

## Rastreabilidade

| Tema / requisito           | Evidência de implementação                                                                                 | Testes existentes relacionados                                                                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Local, período e unidade   | [Schema](../src/climaprev/api/schemas/risk.py)                                                             | [Schema HTTP](../tests/unit/api/test_risk_schema.py)                                                                                                                    |
| Contrato público e erros   | [Rota](../src/climaprev/api/routes/risk.py), [handlers](../src/climaprev/main.py)                          | [Endpoint](../tests/integration/api/test_risk_endpoint.py), [envelope](../tests/unit/api/test_error_envelope.py)                                                        |
| Normalização de previsão   | [Open-Meteo](../src/climaprev/infrastructure/providers/open_meteo.py)                                      | [Contrato](../tests/contract/providers/test_open_meteo_payload.py), [adaptador](../tests/integration/providers/test_open_meteo_adapter.py)                              |
| Cache, lock e fallback     | [Serviço](../src/climaprev/application/services/forecast_query.py)                                         | [Consulta](../tests/integration/application/test_forecast_query.py), [cache](../tests/integration/redis/test_cache.py), [lock](../tests/integration/redis/test_lock.py) |
| Risco heurístico           | [Avaliador](../src/climaprev/domain/risk_evaluator.py), [política](../src/climaprev/domain/risk_policy.py) | [Avaliador](../tests/unit/domain/test_risk_evaluator.py), [política](../tests/unit/domain/test_risk_policy.py)                                                          |
| Alertas oficiais           | [Provider sem configuração](../src/climaprev/application/official_alerts.py)                               | [Alertas](../tests/unit/application/test_official_alerts.py)                                                                                                            |
| IP, proxies e rate limit   | [Dependências](../src/climaprev/api/deps.py)                                                               | [Dependências](../tests/unit/api/test_deps.py), [limiter](../tests/integration/redis/test_rate_limiter.py)                                                              |
| Logs e correlação          | [Observabilidade](../src/climaprev/api/observability.py)                                                   | [Observabilidade](../tests/unit/api/test_observability.py)                                                                                                              |
| Execução e perfil de carga | [Compose](../docker-compose.yml)                                                                           | [Harness](../tests/docker/test_docker_harness.py), [carga](../tests/load/test_risk_load.py)                                                                             |

Os links de testes indicam cobertura relacionada disponível para consulta,
não comprovam que cada lacuna documentada já possui teste ou correção.

## Verificação desta revisão

Foi feita leitura dos módulos de API, aplicação, domínio, infraestrutura e
configuração, além da documentação original e dos modelos SIGFAS. Os links
locais, delimitadores de blocos de código e formato JSON de exemplo foram
verificados por script, e o diff foi inspecionado quanto a espaços inválidos
e alterações fora da documentação.

Resultado do script: **11 arquivos verificados** (dez novos documentos e o
README atualizado), **118 links locais válidos**, **seis diagramas Mermaid**
identificados e nenhum erro de link, bloco não fechado ou JSON de exemplo.
`git diff --check` terminou sem erro.

Na conferência final, `docker-compose.yml` apresentava uma alteração de
formatação feita fora desta tarefa. Ela foi apenas inspecionada e preservada;
não muda os valores usados como referência nesta documentação.

Não foram executados testes de aplicação, carga, acesso ao Open-Meteo ou
publicação: o comportamento executável não foi alterado. Os diagramas foram
revisados como texto; não houve renderização automatizada Mermaid nesta revisão.

## Evidência histórica

O [handoff](../handoff.md) relata uma execução anterior de testes e medições.
As pastas de evidência referidas nele não estão nesta cópia do projeto. Não
reutilizar esses resultados como certificado de capacidade, segurança ou
validação do estado atual.

Para mudanças de código, usar os comandos Docker documentados no
[README](../README.md) e registrar comando, resultado, ambiente e data. Para
avaliar integração externa, distinguir explicitamente provedor real de mock.
