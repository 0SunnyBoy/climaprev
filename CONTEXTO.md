# Contexto de retomada — ClimaPrev

Atualizado em 20/10/2026. Branch `develop`, base `23bf4cee997bc825e76028f99eefd6160f699ee5`; backend/frontend 0.1.0 em desenvolvimento, alterações locais acumuladas sem commit/push, sem nova release.

Ler [STATE](docs/projeto/STATE.md), [RDP](RELATORIO-PENDENCIAS-2026-10-20.md), [handoff](docs/projeto/handoff.md) e [catálogo](docs/projeto/ImplementationsAndRefactoring.md). Preservar o diff e revisar artefatos antes de qualquer staging/publicação. Não versionar .homolog, segredos ou dados brutos locais.

Aplicação local com frontend/API/Redis, desacoplamento concluído no monorepo, janela pública de sete datas UTC, alertas conservadores, prazo cooperativo, interface e métricas revisados. Último lote: 644 testes backend e 27 frontend aprovados, gate HTTPS local aprovado; carga sintética de 3.000 requisições sem falhas. Detalhes/limites no STATE.

Ordem: INMET real; CI remota; revisão científica preparatória; critérios de aprovação; acessibilidade manual. Por último, evolução da candidate-1 com foco em qualidade e precisão da previsão. Reference-v1 ativa; sem fitting/calibração/promoção. Horizonte de 14 dias só planejado. Hospedagem adiada, sem separar repositórios e sem atualizar o PDF acadêmico.

GitHub: CI antiga passou; Security gates antigo falhou na asserção de tema. Correção local ainda sem rerun remoto. develop sem proteção/checks obrigatórios, confirmado por leitura alternativa; 403 administrativo não bloqueia leitura do código. Nenhuma regra remota foi alterada.

[Contexto anterior](CONTEXTO-HISTORICO-ATE-2026-10-20.md) é apenas histórico.
