# Candidate-1 — Frente 2: Ciência, precisão e integração

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

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

## Continuidade vigente — observações e comparação em 28/10/2026

[Relatório da rodada](../operacoes/continuidade-frente-2-etapas-1-a-4-2026-10-28.md) · [qualificação do piloto](../planejamento/reference-candidate-1/evidence/qualificacao-observacoes-piloto-2026-10-28.json) · [benefícios esperados](../planejamento/reference-candidate-1/beneficios-esperados-candidate-1.md).

- **Observações:** três CSVs públicos de 2026 obtidos pela versão oficial até setembro, com CRC/hashes; janela publicada conferida com cobertura de 100% nos quatro alvos importados. Não são dados atuais de outubro. A interface oficial de dados recentes exige reCAPTCHA e mostrou cota excedida; nenhum controle foi contornado.
- **Belém:** coordenadas do CSV 2026 coincidem com o catálogo atual; reconciliação resolvida por versão para essa fonte, preservando o CSV 2024. Ainda não há prova de mudança física ou equivalência instrumental integral.
- **Piloto:** preflight pontual 15/15 concluído (cinco braços, três estações), com arquivos e ledger próprios. D+7 de ICON e D+3/D+7 de MET sem cobertura diária completa. Piloto recorrente permanece desativado por falta de observações atuais verificadas e condições instrumentais; não houve ativação silenciosa.
- **Comparação:** novos parser/pareamento/comparador experimentais para temperatura amostrada, umidade e rajada; contratos de extrema térmica não fabricam máximas/mínimas a partir de instantâneos. Comparação na mesma janela/caso, fonte observacional e slot de meia hora, com denominador planejado incluindo omissões de todos os modelos. Vento sustentado bloqueado por semântica de média não comprovada.

**Qualificação:** 845 testes backend completos, mypy Linux em 88 módulos, Ruff e whitespace aprovados. Frontend e reference-v1 sem alteração; sem ajuste da candidata, incerteza nova, confirmação ou ganho real de precisão. Incremento local sem commit/push/CI próprio. Calendários anteriores precisam de nova versão deliberada após mudanças de pipeline; não modificar seus hashes para habilitar execução.

**Retomada:** obter dados oficiais de outubro por fluxo legítimo, verificar instrumento/altura/período, requalificar prontidão e só então decidir ativação de calendário atualizado. Análise estatística e refinamento seguem para etapas posteriores. Os estados abaixo são históricos quando conflitarem.

## Retomada vigente — preparação das etapas 1 a 4 em 28/10/2026

[Relatório detalhado](../operacoes/preparacao-frente-2-etapas-1-a-4-2026-10-28.md), [evidências](../planejamento/reference-candidate-1/evidence/preparacao-frente-2-2026-10-28.json), [partições](../planejamento/reference-candidate-1/particoes-temporais-2026-10-28.json) e [critérios preparados](../planejamento/reference-candidate-1/criterios-preparados-2026-10-28.json).

1. **Estações:** catálogo oficial atual validado; A201/A001/A801 operantes. Diagnóstico dos CSVs de 2024 já conhecidos: chuva completa em 365/342/349 de 366 dias, respectivamente; 8/2/9 dias de pelo menos 50 mm, sem alegar independência. Observações recentes retornaram 204 nos acessos tentados; qualidade atual não comprovada. Belém exige reconciliação entre coordenadas históricas e atuais, sem alterar o CSV congelado.
2. **Calendário/rodadas:** piloto desativado de 29/10 a 11/11/2026, às 18 UTC (15h Brasília), 210 jobs planejados; rodada 00 UTC para modelos explícitos, baseline/MET com identidade desconhecida preservada. Preflight GFS/IFS/ICON em Belém normalizado; ICON D+7 incompleto. Slot perdido não é preenchido retroativamente.
3. **Partições:** allowlist de desenvolvimento conhecido, demais arquivos em quarentena. Seleção planejada para alvos 03–31/12/2026; confirmação condicional 15/01/2027–14/01/2028. Congelamentos antes das primeiras emissões D+7 e embargo também sobre emissões, sem alegar independência comprovada ou congelamento já efetuado. Datas precisam ser invalidadas e pré-registradas novamente se os marcos forem perdidos.
4. **Critérios:** desenho conservador registrado por delegação, com cobertura operacional mínima de 90%, meta relativa de 5%, proteção sem tolerância automática à piora de extremos e exigência de precisão dos intervalos. Limites não são evidência de suficiência dos dados. Cálculo de incerteza e bloco final permanecem para validação na etapa estatística; avaliador segue apenas diagnóstico e não promove.

**Ponto de retomada:** obter observações oficiais atuais com dados/unidades e reconciliar Belém; satisfazer esses bloqueios antes de ativar coleta/pareamento científico. Suporte efetivo e bloco temporal dependem de desenvolvimento, não de nova aprovação rotineira. Preparação entregue, sem declarar as quatro etapas empiricamente encerradas. Campanha desativada, sem fitting, abertura de resultados reservados ou promoção. Alterações locais sem push; reference-v1 ativa. Checkpoints abaixo são históricos onde conflitarem com este estado.

## Aceite delegado — 28/10/2026

Usuário delegou aceite de parâmetros fundamentados. Desenho aceito com condições: três estações iniciais, piloto técnico de 14 dias, referência de planejamento confirmatório de 12 meses após congelamento, confiança reportada de 95%, separação de dados e D+7 secundário exploratório. Metadados, calendário/rodadas, suporte, cobertura mínima e validade estatística ainda dependem de dados; margem de 0,5 mm, tolerâncias de cinco pontos percentuais e blocos de sete dias não são critérios confirmatórios validados. Não repetir pedidos rotineiros de aceite; documentar decisões e evidências. Sem ativação de campanha ou promoção e sem ampliar o escopo além das ordens 1 a 4. Registro: `docs/planejamento/reference-candidate-1/aceite-delegado-parametros-2026-10-28.md` (raiz). Este estado supera a pendência de aceite individual nos checkpoints abaixo, não suas limitações técnicas.

Atualizado em 28/10/2026. Este relatório distribui responsabilidades de implementação; os parâmetros finais continuam em revisão por escolha expressa do usuário.

## Execução autorizada até a ordem 4 — 28/10/2026

[Relatório desta rodada](../operacoes/frente-2-ordens-1-a-4-2026-10-28.md) e [quadro estruturado de parâmetros para revisão](../planejamento/reference-candidate-1/frente-2-protocolo-proposto-2026-10-28.json).

- **F2-01:** protocolo organizado em direção aceita, propostas e decisões ausentes. Fechamento científico ainda depende de revisão/aceite; o JSON não inicia coleta.
- **F2-02:** verificador ligado ao pareamento de chuva; contratos inválidos geram exclusões explícitas. Observações de horas reais podem ser somadas no intervalo exato de uma previsão de seis horas, sem prorrateio. Instrumentação/representatividade/antecedência e demais variáveis continuam pendentes. O fingerprint do pipeline inclui a dependência de equivalência; não alterar manifestos antigos para contornar divergência.
- **F2-03:** comparador identifica controle operacional ou referência experimental e sinaliza ausência do controle por estrato. Sem baseline em D+7, não há comparação de ganho contra a v1. Recomendação científica ainda proposta.
- **F2-04:** `experimental_criteria.py` avalia limites explícitos e evidências declaradas, com estados `met`, `not_met` e `inconclusive`. Sem intervalos/suporte/independência/cobertura suficientes não há sucesso aparente; nenhum estado autoriza promoção. Limites finais continuam pendentes. Cálculo dos intervalos não foi implementado nesta ordem.

**Qualificação local:** 815 testes backend completos aprovados (58,96 s), warnings como erros; mypy Linux em 85 módulos e Ruff aprovados. Frontend sem alteração nesta rodada. Incremento local sem commit/push ou CI próprio. Não houve coleta de campanha, fitting, novos resultados reservados, promoção ou merge em main.

**Limite da rodada:** não avançar às ordens 5 a 9 nesta autorização. As ordens 1 a 4 têm entregas técnicas, mas não estão cientificamente encerradas enquanto faltarem decisões. Próxima retomada: revisar/aceitar parâmetros pendentes e verificar os dados/contratos com a Frente 1.

## Pendências para retomada — 28/10/2026

Este é o ponto de retomada solicitado pelo usuário. A lista abaixo descreve trabalho ainda necessário; não registra aceite dos parâmetros nem autoriza ativação da campanha.

- [ ] **F2-01 — Fechar o protocolo:** revisar com o usuário e registrar decisões sobre estações, calendário, duração, cobertura mínima, suporte e partições de desenvolvimento, validação de seleção e confirmação.
- [ ] **F2-02 — Concluir equivalência e elegibilidade:** concluir a ligação aos demais alvos/comparador (chuva já integrada) e validar significado instrumental, ponto de previsão/estação, alturas/períodos pertinentes, qualidade e antecedência. O verificador atual não comprova essas condições externas.
- [ ] **F2-03 — Definir controle de D+7:** deliberar sobre a proposta secundária exploratória; manter a ausência da baseline pública explícita e não extrapolar valores para fabricar uma comparação com reference-v1.
- [ ] **F2-04 — Fechar critérios de aprovação:** justificar relevância física, proteção dos extremos, suporte e critérios próprios de temperatura, vento/rajada e umidade. A direção de 5% de redução no MAE da chuva D+1 não aprova os demais valores propostos.
- [ ] **F2-05 — Completar comparação científica:** ampliar o comparador para variáveis e horizontes elegíveis, ligar cobertura aos alvos planejados e expor casos ausentes, exclusões e indisponibilidade por modelo. Coordenar dados/pareamento com a Frente 1.
- [ ] **F2-06 — Implementar incerteza:** integrar e verificar o método estatístico escolhido, com dependência temporal, agrupamento, estratos, suporte e tratamento de múltiplas análises quando aplicável. Existe utilitário histórico de bootstrap; sua existência não significa integração ou aprovação do desenho atual.
- [ ] **F2-07 — Desenvolver refinamento:** testar correções e combinações somente em desenvolvimento/seleção, comparando com baseline e modelos individuais; congelar versão e parâmetros antes da confirmação.
- [ ] **F2-08 — Validar independentemente:** executar o calendário confirmatório aprovado com candidata congelada; avaliar ganho, extremos e indisponibilidade, registrar limitações e obter aceite final do usuário.
- [ ] **F2-09 — Integrar a versão aprovada:** implementar versionamento, rastreabilidade, dados parciais/divergências, contrato, desempenho, regressão e retorno à versão anterior. Somente após evidência e aceite.

### Estado preservado

- Reference-v1 ativa; sem superioridade comprovada, promoção ou integração pública da candidate-1.
- Protocolo consolidado pronto para revisão: [documento de trabalho](../planejamento/reference-candidate-1/frente-2-protocolo-revisao-2026-10-27.md).
- Verificador `src/climaprev/tools/experimental_equivalence.py` e testes em `tests/unit/tools/test_experimental_equivalence.py` preparados localmente: **21 testes novos, Ruff e mypy do módulo aprovados em 27/10**; checkpoint superado pela regressão integral de 815 testes na rodada de 28/10 descrita acima.
- Verificador integrado ao pareamento experimental de chuva nesta rodada; demais alvos ainda isolados, sem pareamento multivariável completo e sem autorização científica.
- Incremento da Frente 2 e seus documentos ainda locais, sem commit/push. Não descartar arquivos novos ao retomar. A aprovação remota do commit publicado `6576dd6` não cobre esse incremento local.
- Parâmetros quantitativos continuam propostos; campanha recorrente não iniciada, sem fitting ou nova leitura de resultados reservados.

### Primeiro passo na retomada

Ler este registro e o protocolo consolidado; conferir `git status` para preservar o incremento local. Retomar a revisão F2-01/F2-04 e a decisão F2-03 com o usuário. Enquanto o aceite estiver pendente, avançar apenas na preparação técnica de F2-02/F2-05 que não dependa dessas escolhas. Planejar dados e contratos com a Frente 1 sem iniciar a campanha ou promover a candidata.

## Checkpoint histórico — início da execução em 27/10/2026

Preparado o [protocolo consolidado para revisão](../planejamento/reference-candidate-1/frente-2-protocolo-revisao-2026-10-27.md), com etapas separadas, decisões pendentes, recomendação de controle D+7 e contratos de observações para a Frente 1. F2-01 e F2-03 seguem aguardando decisões; a proposta não foi considerada aprovada.

F2-02 avançou com `experimental_equivalence.check_equivalence`: diagnóstico de valores, unidades, intervalo e semântica declarada de pares de chuva, rajada e temperatura/umidade. Não integrado aos coletores/comparador, sem pareamento multivariável completo. Temperatura instantânea contra extrema horária e chuva de seis horas contra observação de uma hora são rejeitadas. Aprovação científica, representatividade, instrumento e antecedência continuam fora do diagnóstico. Verificação local: 21 testes novos, Ruff e mypy do módulo aprovados; não equivale a nova execução da suíte integral.

Alterações desta etapa locais, sem commit/push, fitting, novos outcomes reservados, coleta recorrente ou promoção. A reference-v1 permanece ativa.

## Objetivo

Definir e executar uma avaliação que permita desenvolver o refinamento da candidate-1 e decidir, com evidência independente, se ela pode substituir a reference-v1. Melhorar a previsão meteorológica e melhorar a classificação de risco são resultados distintos e precisam de verificações próprias.

## Implementações sob responsabilidade desta frente

| ID | Implementação | Estado atual | Entrega necessária para conclusão |
|---|---|---|---|
| F2-01 | Fechar protocolo, localidades e calendário | Direção aprovada; protocolo consolidado para revisão preparado, sem aceite final | Definir estações, datas, duração, suporte e separação entre desenvolvimento, validação de seleção e confirmação. Registrar aceite do usuário antes de iniciar a campanha correspondente |
| F2-02 | Definir equivalência instrumental e elegibilidade | Chuva possui pareamento exploratório; verificador integrado à chuva; pareamento multivariável pendente | Especificar alvos, intervalos, unidades, qualidade e representatividade da estação frente à grade. Não equiparar automaticamente temperatura instantânea a extrema horária nem vento sustentado a rajada |
| F2-03 | Definir o controle científico de D+7 | Controle por estrato explícito; recomendação documentada, sem aceite | Aprovar comparador e interpretação para D+7. A baseline pública atual cobre hoje UTC até +6; não inventar seu valor em D+7. Comparar outros modelos entre si não demonstra ganho contra a baseline ausente |
| F2-04 | Fixar métricas e critérios de aprovação | Direção inicial aceita; avaliador diagnóstico implementado, limites finais pendentes | Chuva diária D+1 como objetivo inicial e meta direcional de redução de pelo menos 5% no MAE. Fechar relevância física, cobertura mínima, proteção dos extremos, suporte e critérios próprios das demais variáveis |
| F2-05 | Completar o comparador de modelos e baseline | Comparadores experimentais de chuva e variáveis adicionais implementados; integração/estratos finais pendentes | Ampliar a análise para demais variáveis e horizontes elegíveis; manter casos comuns, exclusões, cobertura por braço e limitações explícitas. Valores ausentes não viram zero |
| F2-06 | Implementar incerteza e avaliação independente | Pendente; comparador atual fornece estimativas pontuais | Fechar e implementar método pareado, dependência temporal, agrupamento entre locais, estratos e comparações múltiplas quando aplicável. Verificar suporte e registrar resultados inconclusivos sem promoção |
| F2-07 | Desenvolver correções e combinações da candidata | Pendente | Testar alternativas somente em desenvolvimento e seleção, comparando com baseline e modelos individuais. Congelar parâmetros e versão antes do teste confirmatório; concordância entre fontes não vira probabilidade calibrada automaticamente |
| F2-08 | Executar confirmação e obter aceite final | Não iniciada; sem superioridade comprovada | Avaliar a candidata congelada nos dados independentes do calendário aprovado, incluindo extremos e indisponibilidade. Produzir relatório de ganho, regressões e limitações para decisão do usuário |
| F2-09 | Integrar a candidata qualificada à aplicação | Condicionada à evidência e ao aceite | Versionar modelo/política e proveniência; tratar divergências e dados parciais; validar contrato, latência, regressão e retorno à versão anterior. Preservar distinção entre risco calculado e avisos oficiais |

## O que já existe

O módulo `src/climaprev/tools/experimental_comparison.py` compara chuva em casos elegíveis comuns, com MAE, RMSE, viés, ganho relativo quando definido e diagnóstico de detecção/falsos alarmes. Expõe exclusões e estratos por estação e antecedência em dias de coleta. Essa etiqueta não comprova igualdade de antecedência da rodada meteorológica.

O comparador é exploratório: não fornece intervalos de incerteza ou aprovação automática. Os coletores e a auditoria operacional da Frente 1 apoiam a avaliação, mas não constituem evidência de ganho de precisão.

## Decisões ainda não aprovadas

- Estações A201 Belém, A001 Brasília e A801 Porto Alegre como conjunto inicial.
- Piloto técnico de 14 dias e confirmação de 12 meses após congelar o desenho e a candidata. São propostas; o piloto não amplia o horizonte público e um ano não garante suporte suficiente para extremos.
- Margem física de 0,5 mm/dia de MAE, tolerâncias de cinco pontos percentuais para detecção/falsos alarmes e demais critérios quantitativos.
- Intervalo de 95%, blocos inicialmente propostos de sete dias, cobertura mínima, limiares dos estratos e calendário exato.
- Comparador e interpretação final de D+7.

Essas propostas não devem ser aplicadas como regras aprovadas. Os valores de chuva também não se transferem automaticamente para temperatura, vento ou umidade.

## Sequência de execução

1. Revisar os parâmetros com o usuário e especificar o que o piloto precisa demonstrar.
2. Entregar à Frente 1 os contratos científicos de observações, alvos e elegibilidade.
3. Analisar a viabilidade operacional do piloto autorizado e fechar os parâmetros pendentes sem usar resultados reservados para escolher critérios.
4. Completar comparador, cobertura científica e métodos de incerteza.
5. Desenvolver e selecionar refinamentos em partições próprias.
6. Congelar candidata, desenho, versões e calendário antes da confirmação.
7. Executar avaliação independente e apresentar resultados para aceite.
8. Integrar a versão aprovada e validar comportamento da aplicação antes de qualquer promoção.

## Dependências e fronteira de responsabilidade

A Frente 1 entrega fontes, proveniência, coletas e observações pareadas com cobertura explícita. A Frente 2 estabelece como esses dados podem ser comparados e se sustentam uma conclusão de qualidade. Falhas identificadas na avaliação retornam à Frente 1 para correção, preservando versões e registros anteriores.

As frentes podem avançar em paralelo na preparação. O teste confirmatório exige desenho aprovado e candidata congelada. Nenhum resultado reservado deve orientar ajuste de pesos ou escolha posterior do período de avaliação.

## Critério de conclusão

Protocolo aprovado, avaliação independente reproduzível, desempenho e proteção dos extremos demonstrados conforme critérios aceitos, decisão final registrada e integração validada se houver aprovação. Se a evidência for insuficiente ou desfavorável, a entrega é um relatório conclusivo sobre essa limitação; a reference-v1 permanece ativa.

## Referências

- [Frente 1 — Dados e integrações](RELATORIO-CANDIDATE-1-FRENTE-1-DADOS-E-INTEGRACOES.md).
- [RDP geral](RELATORIO-PENDENCIAS-2026-10-20.md).
- [Direção aprovada e seus limites](../planejamento/reference-candidate-1/aprovacao-direcao-2026-10-23.md).
- [Parâmetros propostos](../planejamento/reference-candidate-1/parametros-campanha-propostos-2026-10-23.md).
- [Revisão solicitada pelo usuário](../planejamento/reference-candidate-1/revisao-parametros-2026-10-27.md).
- [Comparador exploratório de chuva](../operacoes/comparacao-experimental-2026-10-26.md).
