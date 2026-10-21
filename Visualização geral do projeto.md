# Visão geral do ClimaPrev

O ClimaPrev consulta previsões de curto prazo e calcula estimativas heurísticas de risco, apresentando fonte, qualidade dos dados e avisos oficiais separadamente. Reference-v1 permanece em uso; os experimentos da candidata não representam uma previsão superior já aprovada.

Frontend Vue/TypeScript e API FastAPI possuem builds e Composes independentes no mesmo repositório. Redis suporta cache, locks, limites e métricas temporárias; não armazena um histórico público de consultas. O caso de uso coordena serviços distintos de local, previsão e avisos, com regras meteorológicas no domínio e integrações na infraestrutura.

A janela pública tem sete datas elegíveis, hoje UTC até +6. Existe recuperação de falhas/cancelamento e inspeção responsiva local; leitor de tela permanece pendente. O horizonte de 14 dias é planejamento, não funcionalidade ativa.

O produto pretende ter código aberto e permitir serviços empresariais e apoio da comunidade. Comparação de múltiplos modelos/fontes, qualidade de previsão e enquadramento das licenças ainda são evolução planejada. Hospedagem adiada.

[Estado e validações](docs/projeto/STATE.md) · [Pendências](RELATORIO-PENDENCIAS-2026-10-20.md) · [Arquitetura](docs/arquitetura/arquitetura.md) · [Histórico](VISAO-GERAL-HISTORICO-ATE-2026-10-20.md).
