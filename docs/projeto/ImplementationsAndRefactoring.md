# Catálogo de implementações e responsabilidades

Estado de execução/validações em [STATE](STATE.md), pendências em [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md). Este catálogo descreve caminhos, sem duplicar checkpoints.

| Responsabilidade | Código atual |
|---|---|
| Composição e recursos | `src/climaprev/main.py`, `config.py` |
| Rotas, erros e saúde | `api/routes/`, `api/exception_handlers.py` |
| Entrada/saída HTTP | `api/schemas/risk.py`, `risk_response.py` |
| Caso de uso | `application/services/forecast_query.py` |
| Resolução de local | `application/services/location_resolver.py` |
| Cache/recuperação/lock/heartbeat da previsão | `application/services/forecast_cache.py` |
| Consulta/cache/entrega de avisos | `application/services/alert_query.py` |
| DTOs, conversões e prioridade do resultado | `application/query_result.py` |
| Formato validado do cache | `application/cache_codec.py` |
| Contratos e exceções internas | `application/ports.py`, `application/errors.py` |
| Regras meteorológicas e avaliação | `domain/` |
| HTTP, provedores, Redis e métricas | `infrastructure/`, `api/observability.py` |
| Cliente HTTP frontend | `frontend/src/services/api.ts` |
| Validação JSON em runtime | `frontend/src/services/responseValidation.ts` |
| Prazo/cancelamento compartilhado | `frontend/src/utils/requestDeadline.ts` |
| Interface e estados | `frontend/src/components/`, `frontend/src/composables/` |
| Doubles/builders de testes reutilizados | `tests/support/forecast.py` |
| Experimentos offline e reprodução | `src/climaprev/tools/`, `docs/planejamento/reference-candidate-1/scripts/` |
| Baseline e rodada experimental | `tools/experimental_baseline.py`, `tools/experimental_collection.py` sob `src/climaprev/` |
| Manifesto, orçamento local e execução por slot | `src/climaprev/tools/experimental_campaign.py` |
| Comparação consolidada exploratória de chuva | `src/climaprev/tools/experimental_comparison.py` |
| Arquivo, medições e pareamento exploratório INMET | `src/climaprev/tools/experimental_archive.py`, `experimental_normalization.py`, `experimental_pairing.py` |

A estrutura preserva independência de frontend/backend no monorepo. Extrações não alteram automaticamente identidade de cache, critérios científicos ou publicação. Avisos oficiais e risco heurístico continuam distintos. Scripts de reprodução e arquivos fingerprintados não são conteúdo descartável.

[Execução da refatoração](../operacoes/refatoracao-2026-10-20.md) · [Catálogo histórico](ImplementationsAndRefactoring-HISTORICO-ATE-2026-10-20.md).

## Frente 2 — preparação científica em 28/10/2026

`tools/experimental_equivalence.py` valida contratos declarados de medições e é consultado pelo pareamento de chuva. `tools/experimental_criteria.py` recebe critérios explícitos/evidências e retorna diagnóstico, sem cálculo de intervalos ou promoção. `experimental_comparison.py` explicita controles por estrato. Ver [relatório da rodada](../operacoes/frente-2-ordens-1-a-4-2026-10-28.md). Incremento local, 815 testes backend e mypy 85 módulos/Ruff aprovados; ordens científicas 1 a 4 seguem parcialmente dependentes de decisões.

## Preparação reproduzível da Frente 2 — 28/10/2026

`tools/experimental_preparation.py` reconcilia catálogo/versão histórica, prepara calendários desativados e verifica partições/embargos/congelamento antes das emissões de confirmação. `experimental_campaign.py` congela e encaminha inicialização explícita aos modelos compatíveis. `experimental_criteria.py` admite condição de precisão para intervalos de extremos e suporte previsto. Nenhum componente ativa campanha ou demonstra independência sozinho. Ver [relatório de preparação](../operacoes/preparacao-frente-2-etapas-1-a-4-2026-10-28.md).

## Continuidade multivariável da Frente 2 — 28/10/2026

`tools/experimental_observations.py` acrescenta temperatura/umidade horárias declaradas e prontidão por janela, sem alterar o importador histórico congelado. `tools/experimental_multivariable.py` pareia janelas exatas por alvo e compara casos comuns contra denominador planejado, com exclusões e sem promoção. Ambos têm identidade congelada no pipeline experimental. 845 testes backend/mypy 88 módulos/Ruff aprovados; ver [relatório](../operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md).
