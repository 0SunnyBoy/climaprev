# Contexto para o próximo Codex

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

Comece pelo [contexto de retomada da segurança](docs/planejamento/seguranca-configuracao-segredos/context.md).
Ele registra alterações, testes, falhas, dependências e ordem de continuação.
Depois leia [spec](docs/planejamento/seguranca-configuracao-segredos/spec.md),
[design](docs/planejamento/seguranca-configuracao-segredos/design.md),
[tasks](docs/planejamento/seguranca-configuracao-segredos/tasks.md) e
[evidências](docs/planejamento/seguranca-configuracao-segredos/evidence.md).

Não confunda resultados históricos do projeto com validação deste checkpoint.
Os gates locais foram reexecutados em Redis/containers descartáveis, e os
dois workflows remotos passaram. A homologação sintética não valida DNS,
firewall, certificado público nem credenciais reais. Preserve alterações
locais e não publique segredos ou artefatos de scanner.
