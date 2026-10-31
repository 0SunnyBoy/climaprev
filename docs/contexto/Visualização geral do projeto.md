# Visão geral do ClimaPrev

O ClimaPrev consulta previsões de curto prazo e calcula estimativas heurísticas de risco, apresentando fonte, qualidade dos dados e avisos oficiais separadamente. Reference-v1 permanece em uso; os experimentos da candidata não representam uma previsão superior já aprovada.

Frontend Vue/TypeScript e API FastAPI possuem builds e Composes independentes no mesmo repositório. Redis suporta cache, locks, limites e métricas temporárias; não armazena um histórico público de consultas. O caso de uso coordena serviços distintos de local, previsão e avisos, com regras meteorológicas no domínio e integrações na infraestrutura.

A janela pública tem 14 datas elegíveis, hoje UTC até +13, com consultas de um a sete dias consecutivos. Existe recuperação de falhas/cancelamento e inspeção responsiva local; leitor de tela permanece pendente. O horizonte 14/7 está implementado e qualificado na develop em ffa50f1.

O produto pretende ter código aberto e permitir serviços empresariais e apoio da comunidade. Coleta e comparação experimental de modelos/fontes estão implementadas; ganho de precisão da candidata e enquadramento das licenças continuam pendentes. Hospedagem adiada.

[Estado e validações](../projeto/STATE.md) · [Pendências](RELATORIO-PENDENCIAS-2026-10-20.md) · [Arquitetura](../arquitetura/arquitetura.md) · [Histórico](VISAO-GERAL-HISTORICO-ATE-2026-10-20.md).
