# Contexto para o próximo Codex

Atualizado em 2026-09-21. Branch: `Atualizacao-Geral-V3`.

Este é um checkpoint de trabalho **parcial**, não uma versão aprovada para
produção. A implementação foi retomada para concluir controles locais e
registrar gates reproduzíveis. Não houve publicação, deploy ou troca de
segredos reais.

Comece pelo [contexto de retomada da segurança](docs/planejamento/seguranca-configuracao-segredos/context.md).
Ele registra alterações, testes, falhas, dependências e ordem de continuação.
Depois leia [spec](docs/planejamento/seguranca-configuracao-segredos/spec.md),
[design](docs/planejamento/seguranca-configuracao-segredos/design.md),
[tasks](docs/planejamento/seguranca-configuracao-segredos/tasks.md) e
[evidências](docs/planejamento/seguranca-configuracao-segredos/evidence.md).

Não confunda resultados históricos do projeto com validação deste checkpoint.
Os gates locais abaixo foram reexecutados em Redis/containers descartáveis;
homologação dependente de mounts Windows, scanners externos e revisão
independente continuam fora do aceite local. Preserve alterações locais e
não publique segredos ou artefatos de scanner.
