# Handoff de retomada — ClimaPrev

Retomada vigente — 28/10: integração das etapas 1 a 5 concluída tecnicamente onde há dados. Ler `docs/operacoes/frente-2-etapas-1-a-5-2026-10-28.md` (raiz). Correção oficial: temperatura observada é média horária, não instantânea; umidade e vento instantâneos não equivalentes permanecem bloqueados. CLI offline integra arquivos, CSV, horizontes e cobertura; verificação primária do piloto identifica falta de observações recentes nas três estações. Piloto desativado, sem fitting/promoção. 858 testes backend/mypy 89 módulos/Ruff aprovados; lote anterior baa3465 já passou CI/Security, incremento seguinte exige checks próprios. Preservar plano local de extração de API fora deste escopo e reservas históricas.

Retomada mais recente em 28/10: ler `docs/operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md` (raiz). CSVs públicos 2026 até setembro obtidos, Belém reconciliada por versão, preflight 15/15; importação/pareamento/comparação experimental de temperatura/umidade/rajada e cobertura planejada prontos. Fonte atual de outubro segue bloqueada no fluxo verificado (interface reCAPTCHA com cota excedida); piloto desativado. 845 testes backend, mypy 88 módulos e Ruff aprovados localmente. Sem fitting, promoção, push ou CI do diff. Preservar arquivos locais e dados reservados; refazer manifestos deliberadamente antes de habilitar execução após mudança de pipeline. Reference-v1 permanece ativa.

Última retomada em 28/10: preparação das quatro etapas entregue, com 826 testes backend/mypy 86 módulos/Ruff aprovados. Ver `docs/operacoes/preparacao-frente-2-etapas-1-a-4-2026-10-28.md` (raiz). Bloqueios: observações atuais retornam 204, coordenadas de Belém precisam de reconciliação, suporte efetivo/bloco estatístico ainda dependem de dados. Piloto de 29/10–11/11 às 18 UTC e partições futuras apenas preparados/desativados; não simular execução ou backfill. Materiais existentes fora da allowlist seguem em quarentena lógica. Mudanças locais sem push e reference-v1 ativa. Este estado supera os checkpoints abaixo.

Retomada vigente de 28/10: Frente 2 avançada até ordem 4, com parâmetros ainda em revisão. Pareamento de chuva valida contratos; comparador explicita controle por estrato; avaliador de critérios consome evidência sem promover. 815 testes backend e mypy 85 módulos/Ruff aprovados localmente. Incremento sem push, reference-v1 ativa; não iniciar ordens 5 a 9 nesta autorização. Ler relatório `docs/operacoes/frente-2-ordens-1-a-4-2026-10-28.md` (raiz) e RDP antes dos checkpoints históricos abaixo.

Atualização consolidada de 27/10: complemento de cobertura operacional qualificado com **757 testes backend**, mypy em **83 módulos** e Ruff; frontend com **48 testes**, lint/build e auditoria sem vulnerabilidades. Lote inicial publicado em `4525202`, Security gates aprovado; resultado remoto do complemento deve ser conferido no seu próprio SHA. Sem campanha ativa, promoção, merge em main ou deploy. Parâmetros continuam em revisão por escolha expressa do usuário. Registros numéricos anteriores são checkpoints históricos.

## Retomada vigente — 27/10/2026

Lote consolidado publicado na develop em `4525202`: 748 testes backend, mypy 82 módulos, 48 frontend, lint/build/hardening aprovados localmente. Vitest corrigido, auditoria sem vulnerabilidades; Gitleaks em 56 commits sem achados. CI e Security em acompanhamento. Complemento: auditoria somente leitura contra calendário explícito e revisão dos parâmetros solicitada pelo usuário. Ver relatório `docs/operacoes/consolidacao-2026-10-27.md` e revisão `docs/planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md` (raiz do projeto). Campanha segue desativada, reference-v1 ativa. Parágrafos abaixo de ausência de push ou de qualificações antigas são checkpoints históricos.

Última continuação: [comparador de chuva e elegibilidade](../operacoes/comparacao-experimental-2026-10-26.md), com 75 testes direcionados e checks estáticos aprovados. Entradas v2, baseline diária, cobertura/exclusões e D+7 ausente explícitos. Sem novo ganho real, campanha ou publicação; checkpoints integrais abaixo são anteriores.

## Continuação de 26/10/2026

Ler o [relatório de implementação](../../RELATORIO-IMPLEMENTACAO-2026-10-26.md). Base remota `5a6fc9c`; lote experimental e alerta 429 ainda locais. 714 testes backend, 33 frontend e checks locais aprovados. Baseline/rodadas, manifesto/ledger e pareamento exploratório de chuva prontos no escopo descrito; campanha e promoção desativadas. Parâmetros finais, outras variáveis, acessibilidade auditiva e publicação do lote continuam pendentes. Registros anteriores são históricos.

## Ler primeiro

[STATE](STATE.md) para validações e estado; [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md) para fila; [catálogo](ImplementationsAndRefactoring.md) para caminhos; [refatoração](../operacoes/refatoracao-2026-10-20.md) para o diff transversal.

## Checkout e execução

Branch develop, HEAD/referência local origin/develop em `451d845`; incrementos de responsividade e refatoração ainda locais. Preservar alterações acumuladas e revisar arquivos antes de staging. Não confundir imagem antiga ou CI antigo com o código local atual. Não houve merge/release/deploy.

API/frontend possuem Dockerfiles e Composes próprios; modo integrado local usa `docker compose up -d --build`. Aguardar readiness real, não apenas containers iniciados. Comandos e ambientes estão no README e documentação operacional. Para regressão com Redis usar ambiente isolado de teste, sem flush no banco da aplicação.

## Retomada funcional

O acesso real INMET já foi verificado; acompanhar disponibilidade não equivale a repetir a investigação como bloqueio atual. Leitor de tela aguarda disponibilidade do usuário. Candidate-1 foi retomada no planejamento, com foco em precisão e múltiplos modelos; ainda depende de critérios/proveniência e avaliação independentes. Usuário responsável pelo aceite; responsabilidade não significa aprovação registrada.

Não abrir reservas para escolher ajuste, não promover automaticamente a candidata e não reescrever evidências congeladas. Horizonte de 14 dias e hospedagem adiados. Sem separação de repositórios ou atualização do PDF acadêmico.

## Próximo envio

Revisar diff e arquivos novos, manter .homolog/segredos/dados brutos locais fora do versionamento e executar os gates pertinentes. Conferir CI e Security gates do commit efetivamente enviado. Sem alterações administrativas remotas neste lote.

[Histórico](handoff-HISTORICO-ATE-2026-10-20.md).
