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
