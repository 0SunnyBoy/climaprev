# STATE — ClimaPrev

## Entregas analíticas 4 → 1 → 2 → 3 — 30/10/2026

Implementados relatório automático de encerramento/cobertura do piloto, revisão declarada de contratos/altura/representatividade das variáveis secundárias, planejamento estatístico com alocação de confiança e sensibilidade de blocos e alternativas fixas de combinação/correção. São quatro módulos novos de análise; os arquivos congelados da coleta não foram alterados e o calendário ativo continua válido. 29 testes direcionados, Ruff integral e mypy dos quatro módulos aprovados; conferir CI próprio do incremento.

Relatório atual: zero capturas de piloto, 210 jobs futuros, sem encerramento ou ganho real. Contexto instrumental e cobertura simultânea não são certificados automaticamente; bloco final e suporte continuam pendentes de dados. Alternativas não ajustadas, selecionadas ou ativadas. Nenhum novo resultado reservado aberto. Reference-v1 e automação diária até a cota preservadas. Estado/limites e comandos em `docs/operacoes/frente-2-prioridades-4-1-2-3-2026-10-30.md`; evidência em `docs/planejamento/reference-candidate-1/evidence/entrega-prioridades-2026-10-30.json`. Este checkpoint supera a ausência dessas ferramentas, sem encerrar a validação científica.


## Piloto técnico adaptativo — observações restauradas em 30/10/2026

O acesso oficial TEMPO pelo navegador permitiu baixar os CSVs recentes das três estações; a API direta continua 204. Conversão explícita e rastreável entregue sem alterar o importador anual. Janela recente concluída: chuva/rajada 168/168 horas válidas em A201/A001/A801. Preflight renovado 15/15; D+1 disponível nos cinco braços; prontidão técnica de chuva aprovada, sem ganho de precisão calculado.

Usuário autorizou automação diária às 15h Brasília e depois reposição até completar a cota **sem data-limite**. Automação `piloto-t-cnico-climaprev` ativa; primeira janela 31/10 18 UTC. Regra: 14 capturas D+1 elegíveis por estação/modelo, 210 no total; pares completos deixam de ser consultados. Perdas viram novas datas futuras, sem backfill nem retirada do histórico de falhas. Notebook/Codex indisponíveis podem perder slots; a cauda observacional acompanha o último D+7 real. Calendário científico condicional exige revisão se as reposições ultrapassarem desenvolvimento; nenhuma confirmação/promoção autorizada. Zero slots de piloto executados nesta preparação; diagnóstico não conta na cota.

Código de importação e planejamento/auditoria de cota testado; conferir qualificação remota do novo SHA antes de transferir a aprovação anterior de 0471a98. Estado completo e comandos: `docs/operacoes/piloto-tecnico-observacoes-restauradas-2026-10-30.md`; protocolo v5: `docs/planejamento/reference-candidate-1/protocolo-piloto-adaptativo-2026-10-30.json`; evidências: `docs/planejamento/reference-candidate-1/evidence/observacoes-tempo-piloto-adaptativo-2026-10-30.json`. Este estado supera o bloqueio de observações e os calendários fixos anteriores, mantendo reference-v1 padrão e demais pendências científicas/auditivas/comerciais.


## Preparação vigente das etapas 1 a 6 — 30/10/2026

Merge cab7d8c publicado na develop, com CI 41081566586 e Security 41081566583 aprovados. Protocolo/critério/partições conciliados com o runner recebido; catálogo e contratos oficiais revisados; acesso recente INMET repetido (204 nas três estações, índice anual até setembro). Calendário desativado replanejado para 31/10–13/11, 18 UTC/15h Brasília, 210 jobs e 630 alvos até 20/11. Seleção condicional deslocada a 05/12 para preservar embargo de emissões D+7; confirmação não iniciada.

Prontidão executada: **não pronto**, por observações recentes ausentes, janela antiga e preflight de 28/10. Gate reforçado para bloquear preflight com mais de 24h, relógio ausente ou futuro. 34 testes direcionados, Ruff integral e mypy dos dois módulos aprovados; verificar CI próprio do incremento. Nenhuma campanha ativada, registros E1/E2/E3 emitidos, fitting, resultado reservado novo ou promoção. Reference-v1 permanece padrão. Critérios dependentes de suporte e bloco final seguem explicitamente condicionais. Ler `docs/operacoes/preparacao-piloto-etapas-1-a-6-2026-10-30.md` e `docs/planejamento/reference-candidate-1/protocolo-consolidado-2026-10-30.md`. Este estado supera o registro anterior de merge apenas local e os calendários antigos; preserva os demais checkpoints como histórico.


## Integração vigente da develop2 — 30/10/2026

Incorporada a origem `origin/develop2` (`9fd99b7`) à versão local, preservando o incremento da frente 2 (`bd7fbe3`). A origem acrescenta protocolo, partições, observações, campanha/cobertura, comparação/relatórios e infraestrutura de registro, seleção, confirmação técnica e adaptação explícita da candidata. Essas entregas usam ensaios sintéticos: não encerram campanha ou aprovação científica reais. Reference-v1 segue padrão; candidata não selecionada. Calendários antigos precisam de nova versão deliberada antes de execução; sem backfill. Relatório de conciliação e qualificação: `docs/operacoes/merge-develop2-frentes-2026-10-30.md`. Este checkpoint supera afirmações históricas abaixo de ausência dessa infraestrutura. Qualificação combinada: 1.099 testes backend, mypy em 93 módulos, Ruff integral; 56 testes frontend, lint e build com Node.js 22.23.2 aprovados. Merge exclusivamente local, sem push ou alteração da main.


## Integração da incerteza aos relatórios — 29/10/2026

Implementada `evaluate_development_reports`: consome relatórios v2, verifica lista de hashes observacionais de desenvolvimento, calendário explícito, partição declarada, braço/modelo, elegibilidade, identidade dos pares e slot de coleta. O comparador passa a expor pares comuns somente por opção explícita, preservando sua saída padrão. A análise entrega sensibilidade por tamanho de bloco, agregada e por estação, incluindo estações/dias sem nenhum par no denominador planejado.

Limites: hashes e partição são declarações do chamador, não autenticação independente; nenhum dado reservado foi aberto. Resultados continuam exploratórios, sem ajuste de multiplicidade, certificação de independência, fitting ou promoção. F2-05/F2-06 avançaram, mas não estão encerradas. O fingerprint de campanha agora inclui incerteza, critérios e bootstrap; calendários antigos exigem nova versão deliberada, sem reescrita silenciosa de hashes. Qualificação desta rodada: 874 testes backend em Linux aprovados, Ruff dos arquivos alterados e mypy local dos dois módulos de análise aprovados; mypy integral Linux aprovado em 90 módulos. Incremento local, sem push. Relatório: `docs/operacoes/frente-2-integracao-incerteza-2026-10-29.md`. Este checkpoint supera as pendências técnicas correspondentes dos registros abaixo.


## Preparação do fechamento da frente 2 — 28/10/2026

Implementado `experimental_uncertainty.py`: diferenças pareadas de MAE/detecção/falsos alarmes, blocos de datas agrupando estações, cobertura planejada e ligação ao diagnóstico de critérios. 46 testes específicos, Ruff e mypy aprovados; sem nova qualificação integral ou push. Intervalos exploratórios; independência não certificada, sem promoção. F2-06 avançou, mas não está concluída. Ainda preparar importação auditável dos pares/partições, estratos, multiplicidade e estrutura de refinamento/congelamento; validação real fica condicionada aos dados da frente 1. Frente 2 não encerrada. Relatório: `docs/operacoes/frente-2-fechamento-tecnico-2026-10-28.md`. Este checkpoint prevalece sobre estados históricos incompatíveis abaixo.


## Integração das etapas 1 a 5 — 28/10/2026

Lote anterior publicado em `baa3465`, com CI e Security aprovados. Nova revisão corrige contratos a partir do glossário oficial: temperatura horária é média da hora anterior, não instantânea; umidade mantém agregação não resolvida; vento observado é média de dez minutos. Comparações incompatíveis ficam bloqueadas; a afirmação antiga de pareamento instantâneo de temperatura/umidade é superada por esta correção.

Implementado `experimental_evaluation.py` (função e CLI offline): verifica integridade dos arquivos/CSV, modelo/rodada, ponto/slot, integra chuva e diagnósticos multivariáveis por D+1/D+3/D+7, preserva ausência da baseline horária e não fabrica pares. Avaliação real das quinze capturas/3 estações: previsões D+1 disponíveis, observações recentes com cobertura zero; métricas indefinidas, sem ganho calculado. Nova qualificação de piloto primário retorna bloqueios de observações de A201/A001/A801 e não ativa rotina. Calendário v2 desativado preservado.

**858 testes backend completos**, mypy Linux em **89 módulos**, Ruff aprovados. Incremento preparado para envio autorizado à develop nesta rodada; consultar CI/Security do SHA publicado para seu resultado próprio. Sem alteração da API pública/frontend/reference-v1, fitting, incerteza nova, confirmação, promoção ou main. Fonte anual oficial revalidada ainda termina em setembro; acesso recente legítimo e equivalência instrumental completa seguem pendentes. Relatório: `docs/operacoes/frente-2-etapas-1-a-5-2026-10-28.md`; contratos: `docs/planejamento/reference-candidate-1/contratos-instrumentais-verificados-2026-10-28.md` (raiz). Checkpoints abaixo são históricos onde conflitarem.

## Continuidade mais recente da Frente 2 — 28/10/2026

Observações públicas das três estações obtidas até setembro/2026; Belém reconciliada por versão 2026 compatível com catálogo, sem alterar 2024. Interface recente do INMET exige reCAPTCHA e mostrou cota excedida; fonte pública verificada ainda não cobre outubro. Preflight pontual de cinco braços/três pontos concluiu 15/15; piloto recorrente segue desativado. Parser e comparador multivariável experimentais implementados para temperatura amostrada, umidade e rajada, com fonte/janelas/slot compatíveis e cobertura contra plano completo. Vento sustentado e extrema térmica sem previsão equivalente permanecem inelegíveis. **845 testes backend**, mypy **88 módulos**, Ruff/whitespace aprovados; sem frontend, fitting, incerteza nova, confirmação ou promoção. Ganho real da candidate-1 continua não demonstrado. Incremento local sem push/CI próprio. Relatório: `docs/operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md`; benefícios e condições: `docs/planejamento/reference-candidate-1/beneficios-esperados-candidate-1.md` (raiz). Este estado supera os bloqueios antigos de ausência total de CSV 2026/reconciliação de Belém, mas não a falta de dados atuais/equivalência instrumental.

## Preparação vigente da Frente 2 — 28/10/2026

Entregues verificação cadastral das três estações, diagnóstico observacional de 2024 conhecido, calendário desativado com rodadas explícitas, partições/allowlist e critérios conservadores por delegação. **826 testes backend completos**, mypy Linux em **86 módulos** e Ruff aprovados. Fonte atual do catálogo marca as três operantes; consultas de observações recentes retornaram 204 e não validam qualidade atual. A201 tem divergência de coordenadas entre catálogo e CSV histórico. Calendário de piloto 29/10–11/11, 18 UTC/15h Brasília, 210 jobs planejados; nenhuma rotina ativada. Partições de seleção/confirmação são condicionais e exigem congelamento antes das emissões; allowlist é classificação lógica, não movimentação ou bloqueio de arquivos no sistema operacional. Suporte efetivo e bloco temporal final continuam dependentes de dados antes da confirmação. Sem fitting, outcomes reservados novos, promoção, commit/push ou CI do incremento local. Ler `docs/operacoes/preparacao-frente-2-etapas-1-a-4-2026-10-28.md` (raiz). Preparação fechada; não declarar prontidão científica enquanto persistirem esses bloqueios. Registros abaixo são checkpoints anteriores onde conflitarem.

## Aceite delegado — 28/10/2026

Usuário delegou aceite de parâmetros fundamentados. Desenho aceito com condições: três estações iniciais, piloto técnico de 14 dias, referência de planejamento confirmatório de 12 meses após congelamento, confiança reportada de 95%, separação de dados e D+7 secundário exploratório. Metadados, calendário/rodadas, suporte, cobertura mínima e validade estatística ainda dependem de dados; margem de 0,5 mm, tolerâncias de cinco pontos percentuais e blocos de sete dias não são critérios confirmatórios validados. Não repetir pedidos rotineiros de aceite; documentar decisões e evidências. Sem ativação de campanha ou promoção e sem ampliar o escopo além das ordens 1 a 4. Registro: `docs/planejamento/reference-candidate-1/aceite-delegado-parametros-2026-10-28.md` (raiz). Este estado supera a pendência de aceite individual nos checkpoints abaixo, não suas limitações técnicas.

## Frente 2 — ordens 1 a 4 em 28/10/2026

Protocolo estruturado para revisão, contrato de chuva integrado ao pareamento, controle por estrato explícito (incluindo ausência da baseline em D+7) e avaliador diagnóstico de critérios sem limites padrão implementados. Critérios sem evidência suficiente retornam inconclusivo; não calculam intervalos nem autorizam promoção. Parâmetros científicos, instrumentação/antecedência e demais variáveis continuam pendentes. **815 testes backend completos**, mypy Linux em **85 módulos** e Ruff aprovados. Sem alteração do frontend, campanha, fitting ou promoção; reference-v1 ativa. Incremento local sem commit/push/CI próprio; 6576dd6 segue a base publicada aprovada. Rodada encerrada na ordem 4; ordens 5 a 9 não iniciadas por esta autorização. Relatório: `docs/operacoes/frente-2-ordens-1-a-4-2026-10-28.md` (raiz).

## Frente 2 iniciada — 27/10/2026

Protocolo consolidado para revisão e contratos de variáveis preparados em `docs/planejamento/reference-candidate-1/frente-2-protocolo-revisao-2026-10-27.md` (raiz). Novo diagnóstico isolado `experimental_equivalence` rejeita semântica, unidades, intervalos e valores incompatíveis. Ainda não ligado aos coletores/comparador, sem validar instrumentação, representatividade ou antecedência. 21 testes novos, Ruff e mypy do módulo aprovados; suíte integral histórica permanece checkpoint separado. Parâmetros e controle D+7 continuam propostas, campanha desativada e reference-v1 ativa. Incremento local sem commit/push. CI/Security publicados de `6576dd6` já aprovados; essa aprovação não cobre o novo diff.

## Qualificação remota e Actions — 27/10/2026

CI e Security do commit publicado `7b09fe6` concluídos com sucesso. A pendência de qualificação desse SHA está encerrada. Build do frontend reexecutada com Node.js 22.23.2 e aprovada; artefatos em frontend/dist. Avisos de Node 20 referem-se às ações do CI: atualização local de checkout/setup-node/upload-artifact para releases oficiais com node24 e runner fixado em Ubuntu 24.04. Atualização dos workflows incluída no envio autorizado para develop; conferir CI e Security do novo SHA antes de encerrar sua qualificação. Ver `docs/operacoes/atualizacao-actions-2026-10-27.md` a partir da raiz. Demais pendências científicas e de acessibilidade permanecem.

Atualização consolidada de 27/10: complemento de cobertura operacional qualificado com **757 testes backend**, mypy em **83 módulos** e Ruff; frontend com **48 testes**, lint/build e auditoria sem vulnerabilidades. Lote inicial publicado em `4525202`, Security gates aprovado; resultado remoto do complemento deve ser conferido no seu próprio SHA. Sem campanha ativa, promoção, merge em main ou deploy. Parâmetros continuam em revisão por escolha expressa do usuário. Registros numéricos anteriores são checkpoints históricos.

## Complemento de cobertura operacional — 27/10/2026

Lote consolidado publicado em `4525202`; CI e Security em acompanhamento, sem aprovação remota presumida. Adicionado diagnóstico somente leitura de jobs contra calendário explícito, inclusive slots inteiros ausentes e reservas vencidas; planos inativos não contam como falha. 43 testes direcionados, mypy do módulo e Ruff aprovados. Cobertura por alvo meteorológico/variável continua pendente. Usuário escolheu revisar parâmetros antes de aprovar; campanha segue desativada. Ver `docs/operacoes/consolidacao-2026-10-27.md` e `docs/planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md` (caminhos a partir da raiz).

## Consolidação em 27/10/2026

Regressão integral local aprovada: **748 testes backend** (warnings como erros), mypy em **82 módulos**, Ruff e hardening local. O lote inclui coleta/comparação experimental, regressões dos avisos e melhoria da mensagem acessível de limite de requisições. Lockfile do frontend atualizado para corrigir os dois achados moderados do Vitest; auditoria após correção sem vulnerabilidades. Publicação e qualificação remota serão registradas no relatório desta consolidação.

Permanecem pendentes: teste auditivo real PT/EN; aceite dos parâmetros/calendário científicos e controle D+7; pareamento das demais variáveis; cobertura do calendário e incerteza estatística; coleta recorrente após aceite; refinamento e integração condicionados à evidência. Reference-v1 permanece ativa, sem campanha confirmatória iniciada ou ganho comprovado da candidate-1. Horizonte de 14 dias e hospedagem adiados.

## Comparador exploratório e elegibilidade — 26/10/2026

Entrada da baseline diária, pareamento v2 com tempos explícitos e comparação consolidada de chuva implementados. Interseção justa de casos, cobertura/exclusões, métricas numéricas e detecção diagnóstica, estratos por estação/dia após coleta e D+7 sem controle explicitamente indefinido. [Relatório](../operacoes/comparacao-experimental-2026-10-26.md). 75 testes direcionados, mypy dos três módulos e Ruff aprovados; sem nova suite completa, resultados sobre dados reais ou push. Padrão exige rodada informada; modo de coleta/retrospectivo requer opção explícita. Nenhuma aprovação científica ou promoção automática. Controle científico de D+7 e parâmetros finais continuam pendentes.

## Verificação dos avisos — 26/10/2026

Confirmada a entrega de chuva, vento, calor/frio e condições simultâneas em cenários controlados, do caso de uso à rota e nos componentes Vue. Corrigida exibição de `celsius`/`fahrenheit` para °C/°F no resumo, sem alterar cálculo. **32 testes backend selecionados e 48 frontend, lint/tipagem/build aprovados.** [Relatório e alcance](../operacoes/verificacao-avisos-2026-10-26.md). Sem consulta INMET ao vivo ou diagnóstico da consulta original. Sem novo push; a regressão completa anterior de 714 backend continua identificada como checkpoint separado.

## Incremento vigente — 26/10/2026

Baseline pelo adaptador e política atuais arquivável, seleção automática preservada como origem desconhecida, Single Runs com inicialização explícita, manifestos com versões de pipeline, ledger SQLite com cotas/deduplicação entre executores locais e runner por slot desativado por padrão. Pareamento exploratório de chuva por estação/intervalo implementado e exercitado em dados já conhecidos de 2024. [Relatório de implementação](../../RELATORIO-IMPLEMENTACAO-2026-10-26.md).

Qualificação local final: **714 testes backend, 33 frontend, mypy Linux em 81 módulos, Ruff e hardening local aprovados**. Baseline/rodadas GFS e IFS verificadas pontualmente ao vivo. Replay exploratório A201: 28 datas, nove pares completos, 19 incompletos; coleta retrospectiva, sem métrica de ganho ou aceite confirmatório. Sem novos outcomes reservados ou fitting.

Base publicada permanece `5a6fc9c`; novos incrementos sem commit/push ou CI remoto. Reference-v1 e janela pública preservadas. A baseline cobre adaptador/política, sem cache/alertas, e não fornece D+7 fora da janela pública. Rodada solicitada não é primeira publicação comprovada. Pareamento de outras variáveis, parâmetros finais e acionador da campanha continuam pendentes; nenhum agendamento recorrente foi criado. Registros anteriores de ausência desses componentes são históricos.

## Coletores e normalização experimental — 23/10/2026

Implementados coletores pontuais GFS/IFS025/ICON e MET Norway com HTTP limitado e sem retries, junto de medições UTC/unidades/intervalos e soma de chuva por cobertura exata, sem sobreposição/prorrateio. Independentes da API pública. [Execução e limites](../operacoes/coleta-experimental-2026-10-23.md).

Preflight Docker nos três pontos municipais: 11 de 12 combinações aceitas; IFS/Porto Alegre rejeitado por chuva negativa. GFS/IFS válidos cobrem os dias após coleta D+1/D+3/D+7; ICON D+7 e MET D+3/D+7 incompletos nesta amostra, explicitamente sem totais elegíveis. Rodada de inicialização desconhecida; não declarar essas etiquetas como antecedências científicas comprovadas. TLS ativo. 57 testes selecionados, mypy dos três módulos e Ruff no host aprovados. Sem suíte completa ou CI remoto do novo lote.

Permanecem pendentes baseline automática, identificação comprovada de rodada, pareamento observacional, orçamento compartilhado/agendamento e parâmetros finais da campanha. Sem coleta recorrente, fitting ou promoção; alterações locais sem commit/push. Os registros abaixo de "sem HTTP/normalização" descrevem o incremento anterior, agora superado por este protótipo.

## Preparação da coleta experimental — 23/10/2026

[Catálogo de fontes e sequência de coleta](../planejamento/reference-candidate-1/fontes-e-coleta-2026-10-23.md): GFS/IFS/ICON explícitos priorizados e MET Norway exploratório, com restrições de origem, horizonte e acesso verificadas documentalmente. Preflight ao vivo e integração dos novos adaptadores ainda pendentes.

Implementado `tools/experimental_archive.py`: envelope de JSON bruto com origem/local, horário UTC de coleta/rodada/validade, hashes, escrita sem sobrescrita e flags para rodada desconhecida/coleta tardia. Separado da aplicação pública, sem HTTP, normalização meteorológica ou agendamento. Docker: 34 testes selecionados e mypy do módulo aprovados; Ruff dos arquivos novos aprovado. Não representa execução integral de regressões ou ganho de previsão. Alterações locais sem commit/push.

[Parâmetros de campanha propostos](../planejamento/reference-candidate-1/parametros-campanha-propostos-2026-10-23.md) preparados para revisão: três estações, ensaio técnico de 14 dias e teste de um ciclo anual, com margens físicas/estatísticas explicitamente não aprovadas. O ensaio técnico não amplia o horizonte público. Coleta confirmatória e promoção aguardam fechamento do desenho.

## Direção científica aprovada — 23/10/2026

Usuário aprovou a direção após esclarecer o escopo multivariável: chuva diária D+1 como objetivo inicial, D+3/D+7 e temperatura/vento/umidade/risco como avaliações complementares, meta inicial de 5% de redução de MAE com evidência favorável, teste independente e proteção de extremos. [Registro de aceite e limites](../planejamento/reference-candidate-1/aprovacao-direcao-2026-10-23.md). Campanha, equivalência instrumental, margens, suporte e desenho estatístico ainda precisam ser fechados antes do teste confirmatório. Não equivale a aprovação final do experimento ou da candidata; reference-v1 preservada. Registro local sem commit/push nesta atualização.

## Continuação vigente — 21/10/2026

Base publicada: `5a6fc9c`, CI [39645243749](https://github.com/0SunnyBoy/climaprev/actions/runs/39645243749) e Security gates [39645243757](https://github.com/0SunnyBoy/climaprev/actions/runs/39645243757) aprovados. Os registros de qualificação abaixo preservam o histórico das tentativas anteriores.

Incremento local posterior: aviso 429 estabilizado para impedir alteração da região de alerta a cada segundo; contador visual separado e mensagem de liberação preservados. Regressão no App, 33 testes frontend, lint, tipagem e build aprovados. Ensaio auditivo ainda pendente; sem commit/push deste incremento e sem nova qualificação remota. [Execução e roteiro](../operacoes/acessibilidade-continuacao-2026-10-21.md).

Usuário escolheu revisar a proposta científica detalhada antes de aprovar. [Proposta para revisão](../planejamento/reference-candidate-1/proposta-cientifica-para-revisao-2026-10-21.md): objetivo, comparadores, semântica das variáveis, dados prospectivos, métricas e condições de promoção. Status proposto/não aprovado, sem objetivo primário escolhido, fitting ou nova leitura de outcomes reservados. Reference-v1 preservada.

## Qualificação do lote refatorado — 21/10/2026

Refatoração publicada na develop em `e448afc`. A primeira execução remota aprovou a integração independente por HTTPS, mas bloqueou a auditoria de dependências (Vite) e a varredura histórica (hash público do contrato OpenAPI). Correção: Vite 6.4.5 e exceção Gitleaks restrita ao valor exato do SHA256 público, sem desativar regras. Verificações locais da correção: 32 testes frontend, lint, build/tipagem, auditoria sem vulnerabilidades, política sintética de segredos e histórico de 53 commits sem achados. A aprovação remota da correção deve ser consultada nos Actions do novo commit.

Lote de responsividade, refatoração transversal e redução de linhas preparado para publicação na develop por solicitação do usuário. Validação local mais recente: 659 testes backend, 32 frontend, build/lint/tipagem e contrato preservados. O estado Git/SHA e a aprovação remota devem ser conferidos no commit e nos Actions correspondentes; resultados locais não substituem os checks desse SHA. Os registros de 20/10 abaixo descrevem o checkpoint anterior ao envio e não devem ser interpretados como confirmação de alterações ainda não commitadas após a publicação.

Na execução de `432294a`, o CI completo passou; o Security gates avançou até a imagem de runtime e identificou GHSA-6q48-6c7w-9gw2 em certifi. Atualizados os locks de produção, desenvolvimento e carga para certifi 2026.10.19, com hashes dos dois artefatos oficiais do PyPI. Referência: https://github.com/advisories/GHSA-6q48-6c7w-9gw2. A confirmação final de segurança depende da nova execução sobre o commit dessa correção.

## Estado vigente — 20/10/2026

- **Versão/Git:** backend e frontend 0.1.0 em desenvolvimento; develop, HEAD e referência local origin/develop em `451d845`. Esse lote INMET/busca foi enviado anteriormente. Responsividade e refatoração posteriores locais, sem commit/push, merge em main, release ou deploy. CI desse diff não executado remotamente; aprovação antiga não cobre o novo código.
- **Aplicação:** API FastAPI, frontend Vue/TypeScript/Vite e Redis. Builds e Composes distintos, CORS/CSP e gate HTTPS local existentes; monorepo preservado. Sem hospedagem definida.
- **Datas/prazos:** hoje UTC até +6, até sete dias por consulta. Orçamento cooperativo do serviço 7 s, máximo configurável 8 s; cliente 10 s, busca de cidades 5 s após debounce. Transporte/validação anteriores ao serviço e cleanup limitam a interpretação do orçamento. Cancelamento encerra a espera mesmo se o transporte ignorar abort, com isolamento de resposta tardia.
- **Alertas:** filtro temporal/geográfico conservador, cache/expiração na entrega, Polygon/MultiPolygon com furos. INMET ao vivo verificado em amostra controlada, inclusive Docker; não é garantia de cobertura/uptime. Política reference-v1 preservada.
- **Responsividade:** etapa 1 concluída localmente; telas 320/375/768/1280 px, PT/EN, consulta real de sete dias e foco do resultado verificados. Medição isolada de três cidades: frias 1,20–2,16 s e repetidas 3,57–4,21 ms; falha e travamento injetados tratados. Não é capacidade de produção. [Evidências e limites](../operacoes/responsividade-2026-10-20.md).
- **Refatoração:** utilitário de prazo compartilhado; DTOs/conversões em query_result, codecs em cache_codec e schemas/mapper HTTP em risk_response. Resolução de local, cache/lock/heartbeat e consulta de avisos em serviços próprios; tratamento de erros/saúde fora do main. Validadores frontend separados, configuração ESLint consolidada, flags de código sem uso e gate de hardening efetivo ativos. Doubles de testes em suporte próprio, exceções canônicas na aplicação e shim redundante removido. Serviço e rota menores; removidos imports e alias Any dispensáveis. OpenAPI canônico idêntico ao HEAD anterior; sem alteração de política, cache ou algoritmos científicos. [Execução](../operacoes/refatoracao-2026-10-20.md).
- **Validação:** 32 testes frontend, build/tipagem/ESLint/Ruff e mypy Linux (75 módulos) aprovados. Suíte completa mais recente de **659 testes backend aprovada em 55,18 s**, com warnings tratados como erros, incluindo as oito regressões do gate de hardening. Tentativa Windows interrompida não é aprovação.
- **Acessibilidade:** teclado/ARIA/contraste/layout e inspeção interativa realizados; ensaio auditivo com leitor de tela ainda pendente por indisponibilidade informada pelo usuário. Não declarar certificação WCAG.
- **Ciência:** CSVs oficiais, baseline, comparação espacial e catálogo preparados; resultados mistos, sem superioridade substancial comprovada. Reservas com independência não demonstrada. Usuário responsável pelo aceite; critérios/fontes/protocolo aguardam decisão. Nenhuma calibração, combinação de modelos ou promoção implementada.
- **Múltiplas fontes:** planejadas comparação e normalização por modelo/rodada/antecedência e avaliação com INMET; pesquisar Open-Meteo explícita e MET Norway. APIs distintas podem repetir o modelo de origem. Código aberto e possível serviço comercial exigem licença, atribuições e acesso compatíveis; endpoint gratuito não é autorização comercial automática.
- **Operação:** exporter privado por worker/Redis e templates existentes; Prometheus/Grafana/Alertmanager não instalados. Carga sintética anterior: 3.000 requisições, zero falhas e maior p95 580 ms, sem certificação de capacidade. develop sem proteção/checks obrigatórios registrados; nenhuma regra administrativa alterada.

## Revisão de linhas e abstrações

Redução desta revisão: 109 linhas físicas (18.408 → 18.299), sem apagar testes. Saldo contra o commit: +195, dos quais +168 testes/gates e +27 código executável; a contagem anterior misturava essas categorias. Mapeamento HTTP, wrappers e tipo duplicado simplificados; contrato preservado em 24 cenários JSON e OpenAPI. [Análise e método](../operacoes/reducao-linhas-2026-10-20.md).

## Próximos trabalhos

Seguir [RDP](../../RELATORIO-PENDENCIAS-2026-10-20.md): concluir acessibilidade quando possível, fechar protocolo científico, selecionar fontes, coletar/normalizar, comparar, refinar e integrar candidata qualificada. Serviços de cache/locks/avisos já separados nesta refatoração; identidade de modelo e cache antecede integração operacional de múltiplas fontes. Não bloquear o desenho científico com reorganização cosmética.

Adiadas: hospedagem/monitoramento no ambiente definitivo, horizonte de 14 dias (somente planejado) e separação de repositórios. PDF acadêmico fora do escopo. Documentos correntes consolidados sem apagar protocolos, resultados ou evidências históricas.

## Histórico e evidências

[Arquivo histórico](STATE-HISTORICO-ATE-2026-10-20.md) · [frentes 1–4](../operacoes/frentes-1-a-4-2026-10-20.md) · [frentes 1–7](../operacoes/execucao-frentes-1-a-7-2026-10-20.md) · [estado dos protocolos](../planejamento/reference-candidate-1/estado-dos-protocolos-2026-10-20.md). Esses relatórios registram checkpoints; não redefinem o estado vigente acima.
