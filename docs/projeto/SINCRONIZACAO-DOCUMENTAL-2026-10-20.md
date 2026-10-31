# Sincronização da documentação — 20/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Esta revisão atualiza a documentação técnica local antes de qualquer envio ao GitHub. Versões declaradas nos manifests: backend 0.1.0 e frontend 0.1.0; desenvolvimento sem nova release/tag. Branch develop, base 23bf4ce, alterações ainda locais. [STATE](STATE.md) é a fonte do estado vigente; [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) consolida pendências.

## Alterações desta revisão

- Estado atual colocado antes dos históricos em README, contexto, índice, STATE, handoff, roadmap e catálogo de implementações.
- RDP consolidado sem misturar contagens antigas com a última validação: 644 backend e 27 frontend; carga local 3.000 requisições sem falhas e limites explícitos.
- Contratos de datas UTC, prazo cooperativo, alertas, desacoplamento, métricas e limitações operacionais sincronizados.
- CI remota distinguida da local: execução antiga aprovada de CI e falha de Security gates no tema; correção local ainda não enviada. Consulta alternativa confirma develop sem proteção/checks; 403 administrativo não prova falta de acesso ao código.
- Prioridades 1, 2, 3, 4 e 6 registradas; evolução da candidata por último e orientada a qualidade/precisão. Revisão científica preparatória não autoriza fitting/calibração/promoção.
- Horizonte de 14 dias só planejado, hospedagem adiada e monitoramento externo não instalado.

## Preservação e limites

Protocolos congelados, manifestos, snapshots, relatórios JSON/CSV de experimentos e evidências históricas não foram recalculados ou reescritos. Documentos históricos receberam referência ao estado atual quando não congelados. PDF/DOCX acadêmicos, entregáveis e conteúdos em diretórios de trabalho não integram esta sincronização técnica. Não foram executados novos testes funcionais apenas por alteração documental; usam-se as evidências do último lote, sem apresentá-las como novo ensaio. Verificação adicional desta revisão: versões nos manifests, links locais, diff e disponibilidade local. Nenhum commit, push, deploy ou mudança de proteção foi realizado.

## Verificação final desta revisão

API `/health/ready` retornou `ready` e frontend local HTTP 200. `git diff --check` aprovado. O link ativo de Nginx foi corrigido para `frontend/nginx.conf`. Referências de arquivos antigos removidos e de outro checkout SIGFAS foram preservadas como texto histórico, sem links locais inválidos. Protocolos/evidências não modificados. Nenhum teste funcional novo foi alegado nesta revisão documental.

## Revisão de conteúdo complementar

Após a primeira sincronização, informações históricas ainda apresentadas como atuais foram corrigidas no corpo dos documentos. STATE, handoff, roadmap e catálogo agora mantêm apenas o estado vigente; seus registros antigos foram transferidos para arquivos históricos vizinhos, preservando os caminhos relativos. Contexto e visão geral foram reescritos para a branch develop e a ordem atual. Runbook de homologação e descrição da CI foram corrigidos sem equiparar o gate JS aprovado ao runner Python ainda não reexecutado. Catálogo e diagnóstico horário deixaram de aparecer como próximas tarefas. Nove documentos receberam encerramento específico de pendências já superadas; protocolos congelados têm um documento complementar de estado atual, sem reescrever o desenho original.

## Cobertura documental atualizada

Inventário de todos os Markdown técnicos da raiz, docs, frontend e gate de navegador; dependências, diretórios temporários e entregáveis acadêmicos fora do escopo. Documentos preservados como evidência não foram reinterpretados como resultados novos.

| Documento | Tratamento |
|---|---|
| [CONTEXTO-HISTORICO-ATE-2026-10-20.md](../contexto/CONTEXTO-HISTORICO-ATE-2026-10-20.md) | Arquivo histórico separado dos documentos vigentes |
| [CONTEXTO.md](../contexto/CONTEXTO.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/analise-referencias-sigfas.md](../arquitetura/analise-referencias-sigfas.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/arquitetura.md](../arquitetura/arquitetura.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/datas-e-fusos-2026-10-20.md](../arquitetura/datas-e-fusos-2026-10-20.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/desacoplamento-2026-10-20.md](../arquitetura/desacoplamento-2026-10-20.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/fluxos-informacao.md](../arquitetura/fluxos-informacao.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/fluxos.md](../arquitetura/fluxos.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/parametros-de-predicao.md](../arquitetura/parametros-de-predicao.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/arquitetura/validacao-e-calibracao.md](../arquitetura/validacao-e-calibracao.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/frontend/Frontend-Rework.md](../frontend/Frontend-Rework.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/operacoes/execucao-frentes-1-a-7-2026-10-20.md](../operacoes/execucao-frentes-1-a-7-2026-10-20.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/operacoes/homologacao.md](../operacoes/homologacao.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/operacoes/operations.md](../operacoes/operations.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/operacoes/restricoes.md](../operacoes/restricoes.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/operacoes/segredos-e-seguranca.md](../operacoes/segredos-e-seguranca.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/operacoes/validacao-documentacao.md](../operacoes/validacao-documentacao.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/operacoes/validacao-local-2026-10-19.md](../operacoes/validacao-local-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/evolucao-climaprev/context.md](../planejamento/evolucao-climaprev/context.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/evolucao-climaprev/design.md](../planejamento/evolucao-climaprev/design.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/evolucao-climaprev/evidence/baseline.md](../planejamento/evolucao-climaprev/evidence/baseline.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/browser-tests.md](../planejamento/evolucao-climaprev/evidence/browser-tests.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/browser-tls-preflight.md](../planejamento/evolucao-climaprev/evidence/browser-tls-preflight.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t1.md](../planejamento/evolucao-climaprev/evidence/t1.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t10.md](../planejamento/evolucao-climaprev/evidence/t10.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t11.md](../planejamento/evolucao-climaprev/evidence/t11.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t12.md](../planejamento/evolucao-climaprev/evidence/t12.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t13.md](../planejamento/evolucao-climaprev/evidence/t13.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t14.md](../planejamento/evolucao-climaprev/evidence/t14.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t15.md](../planejamento/evolucao-climaprev/evidence/t15.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t16.md](../planejamento/evolucao-climaprev/evidence/t16.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t17.md](../planejamento/evolucao-climaprev/evidence/t17.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t18.md](../planejamento/evolucao-climaprev/evidence/t18.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t19.md](../planejamento/evolucao-climaprev/evidence/t19.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t2.md](../planejamento/evolucao-climaprev/evidence/t2.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t20.md](../planejamento/evolucao-climaprev/evidence/t20.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t21.md](../planejamento/evolucao-climaprev/evidence/t21.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t22.md](../planejamento/evolucao-climaprev/evidence/t22.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t23.md](../planejamento/evolucao-climaprev/evidence/t23.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t24.md](../planejamento/evolucao-climaprev/evidence/t24.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t25.md](../planejamento/evolucao-climaprev/evidence/t25.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t3.md](../planejamento/evolucao-climaprev/evidence/t3.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t4.md](../planejamento/evolucao-climaprev/evidence/t4.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t5.md](../planejamento/evolucao-climaprev/evidence/t5.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t6.md](../planejamento/evolucao-climaprev/evidence/t6.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t7.md](../planejamento/evolucao-climaprev/evidence/t7.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t8.md](../planejamento/evolucao-climaprev/evidence/t8.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/evidence/t9.md](../planejamento/evolucao-climaprev/evidence/t9.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/evolucao-climaprev/spec.md](../planejamento/evolucao-climaprev/spec.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/evolucao-climaprev/tasks.md](../planejamento/evolucao-climaprev/tasks.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| `docs/planejamento/numeros-emergenciais-internacionais.md` (plano de desenvolvimento excluído da main) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md](../planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/analise-e-plano.md](../planejamento/reference-candidate-1/analise-e-plano.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/auditoria-referencia-2026-10-16.md](../planejamento/reference-candidate-1/auditoria-referencia-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/baseline-e-criterios-propostos-2026-10-19.md](../planejamento/reference-candidate-1/baseline-e-criterios-propostos-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/chuva-horaria-2026-10-19.md](../planejamento/reference-candidate-1/chuva-horaria-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/comparacao-estacao-2026-10-16.md](../planejamento/reference-candidate-1/comparacao-estacao-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/diagnostico-e-adendo-2026-10-19.md](../planejamento/reference-candidate-1/diagnostico-e-adendo-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md](../planejamento/reference-candidate-1/diagnostico-horario-e-reservas-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/estado-dos-protocolos-2026-10-20.md](../planejamento/reference-candidate-1/estado-dos-protocolos-2026-10-20.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/execucao-2026-10-16.md](../planejamento/reference-candidate-1/execucao-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/execucao-2026-10-19.md](../planejamento/reference-candidate-1/execucao-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md](../planejamento/reference-candidate-1/experimento-espacial-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/horizontes-completos-2026-10-16.md](../planejamento/reference-candidate-1/horizontes-completos-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/importacao-inmet-2026-10-16.md](../planejamento/reference-candidate-1/importacao-inmet-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/protocolo-etapas-1-a-5.md](../planejamento/reference-candidate-1/protocolo-etapas-1-a-5.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/reference-candidate-1/protocolo-piloto.md](../planejamento/reference-candidate-1/protocolo-piloto.md) | Original histórico/congelado preservado; estado atual no STATE/adendo |
| [docs/planejamento/reference-candidate-1/reconciliacao-e-suporte-2026-10-19.md](../planejamento/reference-candidate-1/reconciliacao-e-suporte-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/reference-candidate-1/sequencia-e-impactos.md](../planejamento/reference-candidate-1/sequencia-e-impactos.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/seguranca-configuracao-segredos/context.md](../planejamento/seguranca-configuracao-segredos/context.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/seguranca-configuracao-segredos/design.md](../planejamento/seguranca-configuracao-segredos/design.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/seguranca-configuracao-segredos/evidence.md](../planejamento/seguranca-configuracao-segredos/evidence.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/seguranca-configuracao-segredos/spec.md](../planejamento/seguranca-configuracao-segredos/spec.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/planejamento/seguranca-configuracao-segredos/tasks.md](../planejamento/seguranca-configuracao-segredos/tasks.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/projeto/handoff-HISTORICO-ATE-2026-10-20.md](handoff-HISTORICO-ATE-2026-10-20.md) | Arquivo histórico separado dos documentos vigentes |
| [docs/projeto/handoff.md](handoff.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/projeto/ImplementationsAndRefactoring-HISTORICO-ATE-2026-10-20.md](ImplementationsAndRefactoring-HISTORICO-ATE-2026-10-20.md) | Arquivo histórico separado dos documentos vigentes |
| [docs/projeto/ImplementationsAndRefactoring.md](ImplementationsAndRefactoring.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/projeto/PossivelPlanoDeEvolução.md](PossivelPlanoDeEvolu%C3%A7%C3%A3o.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/projeto/PROJECT.md](PROJECT.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/projeto/ROADMAP-HISTORICO-ATE-2026-10-20.md](ROADMAP-HISTORICO-ATE-2026-10-20.md) | Arquivo histórico separado dos documentos vigentes |
| [docs/projeto/ROADMAP.md](ROADMAP.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/projeto/SINCRONIZACAO-DOCUMENTAL-2026-10-20.md](SINCRONIZACAO-DOCUMENTAL-2026-10-20.md) | Inventário e verificação desta revisão |
| [docs/projeto/STATE-HISTORICO-ATE-2026-10-20.md](STATE-HISTORICO-ATE-2026-10-20.md) | Arquivo histórico separado dos documentos vigentes |
| [docs/projeto/STATE.md](STATE.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [docs/seguranca/seguranca.md](../seguranca/seguranca.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [frontend/README.md](../../frontend/README.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [README.md](../../README.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-ACESSO-INMET-2026-10-16.md](../contexto/RELATORIO-ACESSO-INMET-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-COMPATIBILIDADE-CONTEXTO-2026-10-15.md](../contexto/RELATORIO-COMPATIBILIDADE-CONTEXTO-2026-10-15.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-HISTORICO-REFERENCE-V2-2026-10-16.md](../contexto/RELATORIO-HISTORICO-REFERENCE-V2-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-LICENCIAMENTO-OPEN-SOURCE-2026-10-16.md](../contexto/RELATORIO-LICENCIAMENTO-OPEN-SOURCE-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-PENDENCIAS-2026-10-15.md](../contexto/RELATORIO-PENDENCIAS-2026-10-15.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-PENDENCIAS-2026-10-19.md](../contexto/RELATORIO-PENDENCIAS-2026-10-19.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-PENDENCIAS-2026-10-20.md](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-PREPARACAO-REPOSITORIO-PUBLICO-2026-10-16.md](../contexto/RELATORIO-PREPARACAO-REPOSITORIO-PUBLICO-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-REFERENCE-CANDIDATE-1-ETAPAS-1-A-5-2026-10-16.md](../contexto/RELATORIO-REFERENCE-CANDIDATE-1-ETAPAS-1-A-5-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-REVISAO-DEVELOP-2026-10-16.md](../contexto/RELATORIO-REVISAO-DEVELOP-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [RELATORIO-REVISAO-IMPLEMENTACOES-COM-CSV-2026-10-16.md](../contexto/RELATORIO-REVISAO-IMPLEMENTACOES-COM-CSV-2026-10-16.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [tests/docker/decoupling/README.md](../../tests/docker/decoupling/README.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
| [VISAO-GERAL-HISTORICO-ATE-2026-10-20.md](../contexto/VISAO-GERAL-HISTORICO-ATE-2026-10-20.md) | Arquivo histórico separado dos documentos vigentes |
| [Visualização geral do projeto.md](../contexto/Visualiza%C3%A7%C3%A3o%20geral%20do%20projeto.md) | Conteúdo vigente ou encaminhamento atualizado; registros datados identificados |
