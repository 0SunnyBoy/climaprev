# Contexto de retomada — ClimaPrev

Retomada mais recente em 28/10: ler `docs/operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md` (raiz). CSVs públicos 2026 até setembro obtidos, Belém reconciliada por versão, preflight 15/15; importação/pareamento/comparação experimental de temperatura/umidade/rajada e cobertura planejada prontos. Fonte atual de outubro segue bloqueada no fluxo verificado (interface reCAPTCHA com cota excedida); piloto desativado. 845 testes backend, mypy 88 módulos e Ruff aprovados localmente. Sem fitting, promoção, push ou CI do diff. Preservar arquivos locais e dados reservados; refazer manifestos deliberadamente antes de habilitar execução após mudança de pipeline. Reference-v1 permanece ativa.

Última retomada em 28/10: preparação das quatro etapas entregue, com 826 testes backend/mypy 86 módulos/Ruff aprovados. Ver `docs/operacoes/preparacao-frente-2-etapas-1-a-4-2026-10-28.md` (raiz). Bloqueios: observações atuais retornam 204, coordenadas de Belém precisam de reconciliação, suporte efetivo/bloco estatístico ainda dependem de dados. Piloto de 29/10–11/11 às 18 UTC e partições futuras apenas preparados/desativados; não simular execução ou backfill. Materiais existentes fora da allowlist seguem em quarentena lógica. Mudanças locais sem push e reference-v1 ativa. Este estado supera os checkpoints abaixo.

Retomada vigente de 28/10: Frente 2 avançada até ordem 4, com parâmetros ainda em revisão. Pareamento de chuva valida contratos; comparador explicita controle por estrato; avaliador de critérios consome evidência sem promover. 815 testes backend e mypy 85 módulos/Ruff aprovados localmente. Incremento sem push, reference-v1 ativa; não iniciar ordens 5 a 9 nesta autorização. Ler relatório `docs/operacoes/frente-2-ordens-1-a-4-2026-10-28.md` (raiz) e RDP antes dos checkpoints históricos abaixo.

Atualização consolidada de 27/10: complemento de cobertura operacional qualificado com **757 testes backend**, mypy em **83 módulos** e Ruff; frontend com **48 testes**, lint/build e auditoria sem vulnerabilidades. Lote inicial publicado em `4525202`, Security gates aprovado; resultado remoto do complemento deve ser conferido no seu próprio SHA. Sem campanha ativa, promoção, merge em main ou deploy. Parâmetros continuam em revisão por escolha expressa do usuário. Registros numéricos anteriores são checkpoints históricos.

## Retomada vigente — 27/10/2026

Lote consolidado publicado na develop em `4525202`: 748 testes backend, mypy 82 módulos, 48 frontend, lint/build/hardening aprovados localmente. Vitest corrigido, auditoria sem vulnerabilidades; Gitleaks em 56 commits sem achados. CI e Security em acompanhamento. Complemento: auditoria somente leitura contra calendário explícito e revisão dos parâmetros solicitada pelo usuário. Ver relatório `docs/operacoes/consolidacao-2026-10-27.md` e revisão `docs/planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md` (raiz do projeto). Campanha segue desativada, reference-v1 ativa. Parágrafos abaixo de ausência de push ou de qualificações antigas são checkpoints históricos.

Continuação de 26/10: [comparador exploratório de chuva e elegibilidade](docs/operacoes/comparacao-experimental-2026-10-26.md) implementados, 75 testes direcionados e tipagem/lint aprovados. Sem nova avaliação de ganho real ou campanha; última suíte integral backend de 714 é checkpoint anterior. Consultar STATE/RDP para o estado vigente.

Atualizado em 26/10/2026. Monorepo, develop, backend/frontend 0.1.0. Base publicada `5a6fc9c` qualificada remotamente; incrementos posteriores locais, sem novo push. Baseline por adaptador/política, rodadas explícitas, manifesto/ledger local e pareamento exploratório de chuva implementados. 714 testes backend, 33 frontend, mypy Linux, Ruff, build e hardening aprovados localmente. Campanha desativada, parâmetros finais pendentes, reference-v1 preservada. Sem merge/deploy. [Relatório vigente](RELATORIO-IMPLEMENTACAO-2026-10-26.md). Checkpoints antigos abaixo não substituem o STATE atual.

## Fontes de referência

- [STATE](docs/projeto/STATE.md): estado observado e validações.
- [RDP](RELATORIO-PENDENCIAS-2026-10-20.md): fila e decisões vigentes.
- [Handoff](docs/projeto/handoff.md): retomada operacional.
- [Catálogo técnico](docs/projeto/ImplementationsAndRefactoring.md): responsabilidades e caminhos atuais.
- [Refatoração](docs/operacoes/refatoracao-2026-10-20.md): mudanças, limpeza e limites.

Prioridade do usuário: responsividade, qualidade e velocidade da aplicação, com evolução da candidata por comparação entre modelos/fontes. Reference-v1 permanece ativa; candidata sem superioridade comprovada ou promoção. Protocolo e critérios aguardam aceite. Horizonte de 14 dias e hospedagem continuam adiados; sem separar repositórios ou atualizar PDF acadêmico.

Preservar alterações locais, dados científicos, protocolos/evidências e segredos locais fora do versionamento. Não confundir aprovação do código antigo com CI do diff atual. O estado técnico detalhado é mantido no STATE para evitar resumos duplicados divergentes.

[Contexto histórico](CONTEXTO-HISTORICO-ATE-2026-10-20.md).
