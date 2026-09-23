# ROADMAP — Clima Prev

**Data:** 23 de setembro de 2026.
**Estado:** implementação local até P2.6 concluída; branch conectada ao Git;
commit, push e revisão independente final pendentes.

O progresso detalhado está em [STATE](STATE.md), e o catálogo técnico está em
[Implementations and refactoring](ImplementationsAndRefactoring.md).

## Etapas do produto

| Etapa | Objetivo | Estado atual |
| --- | --- | --- |
| R0 — Documentação | Consolidar arquitetura, contratos e limites. | Concluída; documentação sincronizada nesta revisão. |
| R1 — Consistência dos dados | Resolver fuso, cobertura horária, valores inválidos e completude. | Concluída no ciclo T1–T5. |
| R2 — Falhas e configuração | Tratar stale, falhas do provedor, lock e configuração. | Concluída no ciclo T6–T10 e incrementos P1.6/P1.11. |
| R3 — Segurança e operação | Definir proxy, logs, cotas, imagem, redes e métricas. | Concluída no ciclo T11–T20 e incrementos P1.1–P1.9. |
| R4 — Frontend | Entregar consulta, resultado, recuperação e acessibilidade. | Concluída no ciclo T21–T25 e incrementos P0/P2.3/P2.5/P2.6. |
| R5 — Alertas oficiais | Integrar fonte autorizada sem misturar alertas ao risco heurístico. | Integração básica do INMET concluída em P2.1; contrato operacional ampliado ainda pendente. |
| R6 — Personalização | Avaliar contas, favoritos, histórico e notificações. | Pendente; exige contratos próprios de identidade e dados. |

As 25 tarefas do ciclo base estão concluídas. Os incrementos P0–P2.6
estenderam o ciclo com separação do frontend, integração do INMET, busca de
localidades, controle de consultas e acessibilidade. A revisão independente
final ainda precisa ser executada.

## Decisões e limites

| ID | Decisão | Estado |
| --- | --- | --- |
| DEC-01 | A consulta permanece anônima neste ciclo. | Mantida; operações pessoais ficam fora. |
| DEC-02 | O período máximo permanece em sete dias inclusivos. | Mantida e validada. |
| DEC-03 | A completude usa `complete`, `partial` e `unavailable`. | Implementada e exposta na API e no frontend. |
| DEC-04 | O ambiente local usa Nginx para frontend e API FastAPI separada. | Implementada. |
| DEC-05 | O risco permanece heurístico e orientativo. | Mantida; calibração científica pendente. |
| DEC-06 | O INMET é a fonte oficial integrada nesta etapa. | Implementada em P2.1; cobertura e operação precisam de consolidação futura. |
| DEC-07 | Alertas oficiais permanecem separados de `forecast_risk`. | Implementada. |
| DEC-08 | Dados pessoais, contas e notificações ficam fora deste ciclo. | Mantida; revisar antes de criar identidade ou histórico. |

## Entregas concluídas

- Frontend estático em `frontend/`, servido pelo Nginx local.
- Backend FastAPI sem responsabilidade de servir HTML ou assets.
- Consulta de risco disponível por GET e POST.
- Proxy confiável, rate limit e headers de segurança configurados.
- Containers e rede local endurecidos.
- Cache Redis, lock distribuído, retries e timeouts controlados.
- Métricas de cache, provedor, retries e lock disponíveis internamente.
- Alertas ativos do INMET integrados com cache e estados de disponibilidade.
- Busca de localidades com sugestões no frontend.
- Timeout, cancelamento e proteção contra respostas obsoletas.
- Acessibilidade funcional e layout responsivo validados.
- Workflow de CI para build, testes, análise estática, Nginx e smoke test.
- Smoke test da CI compatível com assets hashados gerados pelo Vite.

## Próximas etapas

1. Executar a revisão independente final com evidência por requisito.
2. Sincronizar evidências após essa revisão.
3. Revisar as alterações, criar o commit e publicar `Atualizacao-Geral-V3`.
4. Provisionar `.homolog/` e validar a stack real de homologação.
5. Executar a revisão independente final com evidência por requisito.
6. Definir protocolo e dados para calibrar a política de risco.
7. Consolidar o contrato operacional dos alertas oficiais.
8. Definir, se necessário, identidade, histórico e notificações.
9. Planejar implantação pública, CD, monitoramento e rollback.

O processo de validação offline, com fallback e critérios para aumentar o
escopo da previsão, está descrito em [possível continuação e viabilidade de
escopo](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md).

## Tarefas históricas

O arquivo [tasks.md](../planejamento/evolucao-climaprev/tasks.md) mantém as
25 tarefas do ciclo base, seus gates e a matriz de testes. O arquivo
[Possível Plano de Evolução](PossivelPlanoDeEvolução.md) mantém o backlog
ampliado e as ideias de evolução do produto.
