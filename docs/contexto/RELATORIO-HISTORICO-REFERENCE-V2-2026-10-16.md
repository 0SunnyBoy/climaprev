# Planejamento histórico da evolução para reference-v2

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Consulta: 16/10/2026, America/Sao_Paulo. Referência local e HEAD remoto confirmado: `23bf4cee997bc825e76028f99eefd6160f699ee5`, branch develop.

## Conclusão validada

Existe um planejamento histórico consistente para evoluir a política de risco, mas não foi encontrada uma especificação aprovada ou implementação denominada `reference-v2` nas fontes examinadas. O nome utilizado pelo plano é “política candidata”, com o exemplo `reference-candidate-1`.

Assim, reference-v2 é o nome que estamos usando nesta conversa para uma possível sucessora. Não há evidência de que uma v2 já tenha sido definida e esteja apenas aguardando conclusão. O planejamento permite inclusive concluir que a reference-v1 deve ser mantida, caso a candidata não demonstre melhoria suficiente.

As bases técnicas foram implementadas parcialmente. A validação científica e a decisão de promover uma nova política continuam pendentes. O commit mais recente melhora reprodução de dependências, sem alterar regras ou coeficientes de risco.

## Escopo e método da pesquisa

Foram cruzados:

- Documentação versionada, código e testes da develop atual.
- Os 17 commits alcançáveis pelas referências Git locais, incluindo o histórico integrado de develop.
- Histórico de alterações dos planos, política, CLI, avaliador histórico e calibração.
- Textos e índices do ZIP `C:/Users/sunny/Downloads/climaprev-dev-context-2026-10-15.zip`.
- Relatórios locais de 15 e 16/10, que são análises posteriores, não decisões originais de arquitetura.
- HEAD remoto develop pelo conector GitHub.
- Documentação oficial Open-Meteo sobre as fontes citadas no plano.

A busca literal de `reference-v2` não retornou ocorrências no histórico Git examinado nem nos textos MD/TSV/JSON do ZIP. A busca por termos relacionados encontrou planejamento de candidatas, validação histórica, regionalização e calibração. Não foi feita auditoria do conteúdo de todas as outras branches, issues ou conversas externas; conclusões de ausência se restringem a essas fontes.

Nenhum teste, coleta meteorológica, ajuste de limiar ou ativação de calibração foi realizado nesta pesquisa. Instruções dentro do ZIP foram analisadas como documentos, sem executá-las como solicitações do usuário.

### Verificação ampliada do nome literal

Após a pergunta específica sobre o histórico do nome, foram buscadas também as referências remotas main e old-develop, sem mudar o checkout develop. O universo local passou de 17 para 56 commits alcançáveis. Foram pesquisados nomes/mensagens de commit, diffs históricos (inclusive conteúdo removido) e os arquivos nos HEADs de main, old-develop e develop, sem distinção de maiúsculas/minúsculas e considerando variantes com espaço, hífen e sublinhado.

Não foram encontradas ocorrências de `reference-v2` nem dessas variantes no material Git pesquisado. Nesta conversa, porém, o nome foi explicitamente utilizado pelo usuário na pergunta “Como estra a preparação pro reference-v2?” e nas mensagens posteriores. Isso comprova o uso conversacional aqui, sem demonstrar uma especificação antiga versionada. Outras conversas, arquivos locais externos e materiais não versionados nas máquinas anteriores continuam fora dessa verificação.

## Linha do tempo comprovada

| Data / marco | Registro | O que demonstra |
| --- | --- | --- |
| 17/09/2026 — dee8f38 | Entrada de `src/climaprev/domain/risk_policy.py` no histórico disponível | A reference-v1 e seus limiares já estavam no baseline inicial examinado. Isso não prova que tenham sido concebidos nessa data. |
| 18/09/2026 — 0a4654e | Plano de continuação, plano geral, catálogo e especificações entram no Git | Evolução por replay histórico, eventos observados, métricas, região/estação, incerteza e políticas versionadas. O plano específico já descrevia etapas 0–6 e candidata com fallback. |
| 18/09/2026 — catálogo P2.2 no mesmo commit | Revisão de reference-v1, sem alteração dos limiares | Motivo registrado: falta de dados históricos rotulados e avaliação especializada. Não era uma aprovação científica dos limiares existentes. |
| 23/09/2026 — 0f17809 e roadmap datado de 23/09 | Consolidação do ciclo e backlog condicionado | Validação/ampliação de previsão permanece fora das 25 tarefas concluídas; dependia de dataset reproduzível, baseline, revisão e rollback. |
| Registro documental de 25/09/2026 | `docs/projeto/STATE.md` | Relata piloto real de três dias em Belém, antecedência de um dia, três classificações corretas e nenhum falso positivo/negativo; sem ativar calibração. |
| 26/09/2026 — 0fb7fcd | Código de coleta/avaliação/calibração e documentação entram no Git | Adicionados CLI histórico, avaliador básico e ForecastCalibration; avaliação diária e picos ampliados. O registro do piloto datado de 25/09 foi incorporado por esse commit de 26/09. |
| 05/10/2026 — 7190797 | Baseline do pacote de contexto | Não promove uma política nova; mantém reference-v1. |
| 15/10/2026 — revisão do ZIP | CURRENT-PROBLEM F02/F03 | Reconhece componentes existentes e concentra o restante em cobertura, proveniência, métricas, amostra e validação científica. |
| 15/10/2026 — 23bf4ce | Locks dev/load e separação de ferramentas de carga | Melhora ambiente de desenvolvimento; não muda política, piloto, calibração ou critérios científicos. |
| 16/10/2026 — conversa atual | Usuário propõe priorizar reference-v2 | Direcionamento atual de prioridade. Não é uma especificação histórica de escopo ou decisão de promoção. |

Os commits marcam quando o material entrou no Git. As datas escritas dentro dos documentos marcam o relato dos autores; não foram confundidas com novas execuções independentes nesta pesquisa.

Fontes Git: [0a4654e](https://github.com/0SunnyBoy/climaprev/commit/0a4654e096ab01130ac6bafafa2e5d4a8b28ccf6), [0fb7fcd](https://github.com/0SunnyBoy/climaprev/commit/0fb7fcd0c9a507cc48bd87d01628e82b3091c90f), [23bf4ce](https://github.com/0SunnyBoy/climaprev/commit/23bf4cee997bc825e76028f99eefd6160f699ee5).

## O que o planejamento original pretendia

O plano específico pretendia avaliar a viabilidade de ampliar cobertura/localidades, horizonte além de sete dias e limiares por região/estação. Cada expansão dependia de evidências e decisão própria. Nenhuma era uma funcionalidade automaticamente prometida para uma “v2”.

O plano geral acrescentava como direções: replay histórico, comparação com eventos observados, falsos positivos/negativos, calibração regional/sazonal, confiança ou incerteza e versionamento das políticas. Não definia a fórmula de um índice de confiança nem novos limiares aprovados.

O ciclo base preservava reference-v1. Sua spec excluía alteração de limiares e introdução de ML por ausência de validação científica nova. A evolução deveria ocorrer como estudo separado, mantendo a aplicação funcionando.

Fontes: [plano específico](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md:5), [plano geral, item 17](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/projeto/PossivelPlanoDeEvolução.md:221), [limites do ciclo](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/planejamento/evolucao-climaprev/spec.md:23).

## Sequência histórica de execução

| Etapa original | Entrega prevista | Situação verificada hoje |
| --- | --- | --- |
| 0 — Definir experimento | Regiões/localidades, eventos, antecedências, período, fonte observada, métrica de aceite e revisor meteorológico | Há roteiro; não foi localizado um protocolo completo aprovado para reference-v2. |
| 1 — Montar base offline | Local/coordenadas, emissão e validade, horizonte, previsto/observado, fonte/modelo, unidade/fuso e qualidade | CLI existe, mas não entrega toda a proveniência, cobertura e exclusões previstas; faltam entradas reproduzíveis completas. |
| 2 — Reproduzir v1 | Baseline usando chuva horária/diária, rajada e extremos de temperatura | Avaliador e piloto mínimo existem; baseline representativo ainda não demonstrado. |
| 3 — Medir desempenho | Precisão, recall, F1, matriz, falsos positivos/negativos por evento/região/horizonte e estabilidade sazonal | Implementados apenas casos/acertos/erros direcionais/acurácia; faltam matriz e estratificação. |
| 4 — Avaliar candidata | Limiares alternativos/regras regionais identificados separadamente; teste em período não usado no ajuste | Não foi localizada candidata versionada, conjunto de regras novo ou comparação concluída. |
| 5 — Revisão especializada | Revisão de eventos, observações, representatividade, limiares, custos de erro e comunicação | Não foi localizada aprovação especializada de candidata. |
| 6 — Decisão de escopo | Cobertura suficiente, melhoria consistente, ausência de regressão grave, contratos, monitoramento e rollback | Não foi localizada decisão de promover v2 ou ampliar o horizonte. |

Fonte primária das etapas: [processo de execução](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md:51).

## Componentes existentes e seus limites

### Política e avaliador

`RiskPolicy` contém limiares de chuva, rajada, calor e frio; `RiskEvaluator` recebe uma política e produz classificação diária, condições e picos. A API compõe `RiskPolicy()` como padrão.

Entretanto, `policy_version` permanece fixo em reference-v1 com `init=False`. Mudar os limiares pelo construtor não gera uma versão nova. Portanto, há flexibilidade de parâmetros, mas falta um contrato explícito de identidade/seleção de candidatas para comparações rastreáveis e promoção operacional.

Fontes: [RiskPolicy](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/src/climaprev/domain/risk_policy.py:5), [avaliador](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/src/climaprev/domain/risk_evaluator.py:26), [composição](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/src/climaprev/main.py:107).

### Coleta e avaliação histórica

O CLI consulta a rede, usa Previous Runs e Historical Weather, aceita antecedências de 1–7 dias e limita cada coleta a 31 dias. O avaliador de casos fornecidos pode operar offline. “Offline” no plano significa fora do fluxo público da aplicação; não significa que o CLI de coleta funcione sem internet.

Lacunas confirmadas: nulos descartados sem cobertura mínima, somas de precipitação sobre horas disponíveis, interseção de dias sem relatório de exclusões e `missing_fields=()` na normalização histórica. Há métricas agregadas básicas, sem os detalhamentos previstos na etapa 3.

Hoje o CLI usa a mesma reference-v1 para classificar tanto previsão quanto histórico/reanálise. Isso mede concordância dessas classificações. Não substitui rótulos independentes de impacto real. Para comparar futuras candidatas, a referência observada precisa permanecer fixa e explicitada; não deve mudar silenciosamente conforme a política testada. Esta última observação é uma conclusão técnica desta pesquisa, não um entregável já implementado.

Fontes: [coleta e criação de casos](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/src/climaprev/tools/validate_historical.py:72), [relatório de validação](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/src/climaprev/domain/risk_validation.py:26).

### Calibração dos valores meteorológicos

`ForecastCalibration` permite offset de temperatura e multiplicadores de precipitação/vento. Está integrada ao serviço; a identidade do perfil participa da chave de cache. O padrão é disabled.

Não foi encontrado perfil aprovado, coeficientes estimados com amostra representativa ou comparação científica que demonstre ganho. Calibração de valores e alteração da política de classificação são frentes distintas; uma eventual reference-v2 precisa declarar quais inclui. `normalization-v2` e `forecast:v2` no cache são versões técnicas existentes, não prova de uma política reference-v2.

Fontes: [camada de calibração](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/src/climaprev/domain/bias_correction.py:15), [serviço/cache](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/src/climaprev/application/services/forecast_query.py:461), [protocolo](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/arquitetura/validacao-e-calibracao.md:84).

## Qual é o valor da evidência de Belém

O STATE relata três dias, uma localidade e antecedência de um dia, com 3/3 classificações corretas. O próprio documento ressalva que a amostra não basta para decisões científicas ou calibração.

O resultado é evidência documental de um piloto inicial; não foi reproduzido nesta pesquisa. Não foi localizado no material versionado/ZIP um dataset bruto completo com identidade e relatório suficientes para reproduzir independentemente aquela execução. O CLI grava relatórios em diretório ignorado pelo Git, e o ZIP exclui dados meteorológicos coletados. Isso limita a verificação, sem provar que os dados não existam fora das fontes consultadas.

Não se deve converter 3/3 em alegação de acurácia geral de 100%, ganho sobre v1 ou prontidão da v2.

Fontes: [relato do piloto](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/projeto/STATE.md:19), [ressalva do projeto](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/projeto/STATE.md:168).

## Fontes meteorológicas: validação externa do catálogo

A documentação oficial consultada confirma que Previous Runs fornece variáveis em antecedências fixas de 1–7 dias, adequadas à avaliação por horizonte. Isso sustenta o caminho escolhido pelo CLI. [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api).

Historical Weather usa reanálise baseada em observações e modelagem para reconstruir condições passadas. Seu uso não equivale a um catálogo de desastres ou impactos locais observados. [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

Há uma precisão a acrescentar ao catálogo do projeto: Historical Forecast monta uma série contínua com as primeiras horas de execuções sucessivas; não preserva automaticamente uma previsão completa emitida em um instante. Para estudar uma antecedência fixa, utilizar Previous Runs; para reproduzir uma execução específica completa, avaliar Single Runs. A escolha deve ser registrada no protocolo antes da coleta. [Comparação oficial dos datasets](https://open-meteo.com/en/docs/historical-forecast-api).

Não foram consultados endpoints meteorológicos de coleta nem validados dados de uma amostra nova.

## Regras de promoção originalmente registradas

O plano determina preservar reference-v1, testar candidatas fora da produção, manter policy_version nas respostas/relatórios, guardar dados e resultados, promover por mudança explícita e permitir rollback. A documentação de calibração exige amostra suficiente, comparação e atenção à redução de falsos negativos sem aumento injustificado de falsos positivos.

Aumento do horizonte tem condições adicionais: suporte do provedor, cobertura completa do período, testes de datas, orçamento/cache, qualidade apresentada e avaliação separada por horizonte. Assim, uma política nova não implica automaticamente previsão superior a sete dias.

Fonte: [fallback, rollback e horizonte](C:/Users/sunny/OneDrive/Documentos/climaprev-develop/docs/planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md:145).

## Decisões ainda não localizadas

Não foram encontradas, para uma reference-v2 concreta:

1. Especificação de regras novas, limiares, regiões e estações de aplicação.
2. Protocolo aprovado com amostra mínima, cobertura exigida e períodos de ajuste/teste.
3. Fonte/definição independente dos rótulos observados e tratamento dos impactos reais.
4. Metas quantitativas de aceite e tolerâncias de regressão por evento/severidade.
5. Dataset reproduzível e relatório completo de comparação v1/candidata.
6. Perfil calibrado aprovado e autoria/revisão meteorológica identificadas.
7. Contrato operacional implementado para seleção, promoção e rollback da política.
8. Cronograma fechado, responsável pela entrega e decisão formal de promoção.

Essas ausências são o restante a definir/validar, não afirmações de que esses entregáveis nunca possam ter existido em fontes externas.

## Catálogo principal para continuidade

| Fonte | Papel |
| --- | --- |
| `docs/planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md` | Plano histórico central: etapas 0–6, dataset, métricas, candidata, revisão e rollback |
| `docs/projeto/PossivelPlanoDeEvolução.md`, item 17 | Direção de evolução: regionalização, sazonalidade, incerteza e políticas versionadas |
| `docs/projeto/ImplementationsAndRefactoring.md`, P2.2 | Decisão de preservar limiares por falta de validação |
| `docs/planejamento/evolucao-climaprev/spec.md` e `tasks.md` | Limites do ciclo concluído e backlog condicionado |
| `docs/arquitetura/validacao-e-calibracao.md` | Protocolo e componentes efetivamente implementados |
| `docs/projeto/STATE.md` | Relato do piloto e ressalvas de suficiência |
| `src/climaprev/domain/risk_policy.py`, `risk_validation.py`, `bias_correction.py` | Contratos e capacidades atuais |
| `src/climaprev/tools/validate_historical.py` | Coleta/normalização/avaliação histórica atuais |
| ZIP de 15/10, CURRENT-PROBLEM F02/F03 | Recorte posterior das lacunas restantes |

## Encaminhamento derivado da pesquisa

Para respeitar o planejamento histórico e a prioridade indicada agora pelo usuário, o próximo marco é transformar a intenção de reference-v2 em uma especificação de experimento/candidata verificável. Depois: completar qualidade dos dados e métricas, produzir baseline, implementar candidata rastreável, comparar em dados separados, obter revisão e decidir promoção.

Essa é uma proposta de continuidade desta análise. O histórico comprovado entrega o roteiro e ferramentas iniciais; não entrega uma v2 pronta ou uma decisão científica de substituir a v1.
