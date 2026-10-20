# Visão geral do ClimaPrev — 20/10/2026

Versão 0.1.0 em desenvolvimento, branch develop e alterações locais ainda sem commit/push. Não há release ou implantação pública deste lote.

O ClimaPrev consulta previsões e calcula estimativas heurísticas de risco pela reference-v1. O frontend Vue/TypeScript e a API FastAPI possuem builds/Composes próprios, permanecendo no mesmo repositório. Redis suporta cache, locks, limites e métricas temporárias por worker. Avisos oficiais são apresentados separadamente, com prioridade no resumo e tratamento conservador de indisponibilidade.

A janela pública contém hoje UTC até +6, com até sete dias por consulta. O prazo cooperativo do serviço é 7 s por padrão; a interface preserva contexto, foco, tema/idioma e informa falhas. O horizonte de 14 dias ainda não está ativo.

Validação local: 644 testes backend, 27 frontend, build/tipagem/lint e gate HTTPS aprovados. Campanha sintética: 3.000 requisições sem falhas; não mede capacidade de produção. Acesso real INMET e execução remota da revisão local permanecem pendentes.

As próximas frentes são INMET, CI remota, revisão científica preparatória, critérios de aprovação e acessibilidade manual. A evolução da candidata fica por último, voltada a ganho mensurável de qualidade e precisão, ainda não demonstrado. Hospedagem adiada pelo usuário.

[Estado detalhado](docs/projeto/STATE.md) · [Pendências](RELATORIO-PENDENCIAS-2026-10-20.md) · [Arquitetura](docs/arquitetura/arquitetura.md) · [Histórico](VISAO-GERAL-HISTORICO-ATE-2026-10-20.md).
