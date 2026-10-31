# Contexto histórico

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Registro anterior, sem instruções vigentes. Consulte [contexto atual](CONTEXTO.md).

# Contexto para o próximo Codex

## Retomada vigente — 20/10/2026

Usar branch develop, base 23bf4ce, pacotes 0.1.0 em desenvolvimento, alterações locais sem commit/push. Começar por [STATE](../projeto/STATE.md) e [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md). Priorizar INMET real, CI remota, revisão científica preparatória, critérios de aprovação e acessibilidade manual. Candidate-1 por último com foco em qualidade/precisão; v1 preservada, sem fitting/calibração/promoção. 14 dias só planejado, hospedagem adiada, PDF acadêmico fora do escopo. Informações sobre V3/publicação abaixo são históricas.

Atualizado em 2026-09-23. Branch: `Atualizacao-Geral-V3`.

## Publicação atual

O rework do frontend, as atualizações de backend, infraestrutura, testes e
documentação estão publicados na branch `Atualizacao-Geral-V3` no commit
`0f17809` (`feat: finalize Vue frontend rework and project updates`). A branch
acompanha `origin/Atualizacao-Geral-V3`; nenhum deploy ou merge em `main` foi
realizado.

Este é um checkpoint de trabalho **sem aprovação de produção**. T14–T19
foram implementadas e validadas com dados sintéticos; CI e Security gates
passaram no GitHub para o commit `525854ab132e4db37bde9b483468e72ac36cdf10`.
T19 concluiu com decisão condicional; a revisão independente e a validação
da borda real ainda faltam. Não houve deploy nem troca de segredos reais.

Comece pelo [contexto de retomada da segurança](../planejamento/seguranca-configuracao-segredos/context.md).
Ele registra alterações, testes, falhas, dependências e ordem de continuação.
Depois leia [spec](../planejamento/seguranca-configuracao-segredos/spec.md),
[design](../planejamento/seguranca-configuracao-segredos/design.md),
[tasks](../planejamento/seguranca-configuracao-segredos/tasks.md) e
[evidências](../planejamento/seguranca-configuracao-segredos/evidence.md).

Não confunda resultados históricos do projeto com validação deste checkpoint.
Os gates locais foram reexecutados em Redis/containers descartáveis, e os
dois workflows remotos passaram. A homologação sintética não valida DNS,
firewall, certificado público nem credenciais reais. Preserve alterações
locais e não publique segredos ou artefatos de scanner.
