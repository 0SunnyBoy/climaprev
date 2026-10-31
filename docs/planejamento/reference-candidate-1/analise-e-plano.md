# reference-candidate-1 — análise e plano de evolução

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Encerramento das pendências históricas — 20/10/2026

O plano evoluiu para dados oficiais de três estações, bootstrap técnico, baseline de cinco eventos, coleta espacial e catálogo/diagnóstico horário. A evolução da candidata ficou por último, focada em qualidade/precisão; não há demonstração de superioridade sobre v1. Revisão científica e critérios seguem como preparação.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Data: 16/10/2026, America/Sao_Paulo. Baseline de código: develop@23bf4cee997bc825e76028f99eefd6160f699ee5.

Estado: proposta de planejamento para discussão. A candidata ainda não foi implementada; novos limiares, dados e promoção não estão aprovados. Este documento organiza a evolução solicitada, sem ativar política ou calibração.

Atualização de execução em 16/10: a infraestrutura experimental e um piloto diagnóstico real foram implementados/executados depois desta proposta. O estado e os limites estão em `execucao-2026-10-16.md`. Declarações de ausência de implementação neste plano descrevem seu momento inicial; continuam sem aprovação novos limiares, coeficientes e promoção.

## Objetivo e escolha de foco

O plano histórico usa reference-candidate-1 como exemplo de política experimental. Propõe estudar limiares/regras alternativas e decidir, com evidência, se uma sucessora deve ser promovida.

Recomendação inicial: tratar reference-candidate-1 como experimento de classificação de risco, mantendo os valores meteorológicos originais e o perfil de calibração disabled. Medir separadamente se correções dos valores previstos são necessárias. Essa separação permite atribuir eventual ganho às regras ou à calibração.

Após discutir os experimentos separados, a sequência recomendada foi consolidada em `sequencia-e-impactos.md`: base de avaliação compartilhada, experimento de política e experimento de calibração distintos, combinação avaliada posteriormente. A ordem dos ajustes específicos será orientada pelo diagnóstico da baseline. Essa é a proposta de execução solicitada, sem representar aprovação de limiares, coeficientes ou promoção.

O resultado esperado não é simplesmente gerar um novo identificador. É produzir uma decisão reproduzível de promover, rejeitar ou manter em estudo, com limitações explícitas.

## O que existe e o que precisa evoluir

| Componente | Existente | Lacuna relevante |
| --- | --- | --- |
| RiskPolicy | Limiares configuráveis em dataclass imutável | policy_version fixo em reference-v1; parâmetros alternativos podem continuar identificados como v1; faltam validações de consistência dos limiares |
| RiskEvaluator | Avaliação diária, condições, agregação e picos | Resultados agrupam chuva horária/diária e calor/frio; avaliação experimental precisa preservar diagnósticos de cada evento |
| CLI histórico | Coleta Previous Runs e Historical Weather, 1–7 dias de antecedência, até 31 dias por chamada | Não salva todas as entradas/proveniência; agrega nulos sem cobertura mínima; usa interseção silenciosa dos dias |
| RiskValidationReport | Casos, acertos, erros direcionais e acurácia | Sem matriz 3x3, métricas por classe/evento/antecedência ou incerteza amostral |
| Rótulos históricos | CLI aplica v1 ao histórico/reanálise | Mede concordância com essa referência heurística; não valida impactos observados; referência deve ser congelada entre candidatas |
| Qualidade | Adaptador de produção já reconhece cobertura e linha temporal civil | Caminho histórico não aplica todas essas verificações; missing_fields vazio na normalização histórica |
| ForecastCalibration | Offset de temperatura, multiplicadores de chuva/vento, versão no cache | Não estima perfis, não há coeficientes aprovados nem evidência de ganho |
| Composição da API | Usa RiskPolicy() por padrão; avalia risco após obter forecast | Falta contrato de seleção/promover/reverter uma política experimental |
| Evidência | Piloto documental de três dias em Belém | Sem amostra representativa nem entradas completas versionadas desse piloto |

Fontes do código: `src/climaprev/domain/risk_policy.py`, `risk_evaluator.py`, `risk_validation.py`, `bias_correction.py`, `src/climaprev/tools/validate_historical.py`, `src/climaprev/infrastructure/providers/open_meteo.py` e `src/climaprev/main.py`.

## Baseline a preservar

Valores existentes no código; não representam aprovação científica ou classificação oficial:

| Variável | Moderado | Alto | Comparação atual |
| --- | ---: | ---: | --- |
| Chuva máxima horária | 20 mm/h | 30 mm/h | valor maior ou igual ao limite |
| Chuva acumulada diária | 30 mm | 50 mm | valor maior ou igual ao limite |
| Rajada máxima | 40 km/h | 61 km/h | valor maior ou igual ao limite |
| Temperatura máxima | 35 °C | 40 °C | valor maior ou igual ao limite |
| Temperatura mínima | 5 °C | 0 °C | valor menor ou igual ao limite |

A avaliação atual usa o maior nível detectado; alertas oficiais têm tratamento separado. O sinal de alagamento deriva da chuva e é um proxy, sem avaliação hidrológica local. Não contar chuva e esse proxy como duas observações independentes na avaliação científica.

## Escopo proposto do primeiro ciclo

1. Reproduzir a v1 e medir seus erros por evento antes de escolher alterações.
2. Estudar um grupo de regras por vez, priorizando o evento para o qual haja dados e justificativa mais fortes.
3. Usar chuvas horária/diária, rajadas, calor e frio como diagnósticos separados, ainda que a resposta atual agrupe algumas condições.
4. Manter o horizonte público de sete dias e os alertas oficiais separados.
5. Manter calibração disabled no experimento de política, salvo mudança explícita de foco.
6. Executar primeiro fora do fluxo público da API; reutilizar CLI e avaliador, evitando duplicação da aplicação.

Belém é uma proposta de localidade inicial por continuidade com o piloto existente. Regiões adicionais, período e sazonalidade devem ser escolhidos pela disponibilidade/representatividade das fontes e pelo objetivo do produto. Não inferir capacidade nacional a partir de Belém.

IA/ML, novas probabilidades de desastre, onda de calor, modelo hidrológico, expansão automática de horizonte e regionalização nacional não estão definidos como entregas deste primeiro experimento. Uma estimativa de incerteza das métricas do estudo não deve ser transformada em percentual de confiança individual para o usuário.

## Contrato do experimento a preencher antes do ajuste

| Decisão | Proposta / situação |
| --- | --- |
| Foco | Dois experimentos separados com base comum, conforme proposta em sequencia-e-impactos.md; classificação como escopo da política candidata |
| Regiões/localidades | Belém como início proposto; conjunto final pendente |
| Eventos | Diagnosticar os cinco sinais da baseline; selecionar a primeira alteração depois dos dados |
| Antecedências | Proposta inicial: 1, 3 e 7 dias, conforme cobertura real das variáveis |
| Período | Pendente de auditoria de disponibilidade; incluir sazonalidade relevante à localidade |
| Fonte de previsão | Previous Runs com modelo e parâmetros explícitos; registrar disponibilidade de cada variável |
| Referência observada | Fonte, regra de rótulo e versão pendentes; comparar reanálise separadamente de observações/impactos |
| Qualidade mínima | Definir por variável, antes de observar resultados de candidatas |
| Divisão dos dados | Blocos cronológicos de ajuste, validação e teste final; datas exatas pendentes |
| População e tamanho | Contagem por evento/classe/antecedência; suficiência a definir com revisor, incluindo eventos raros |
| Métrica principal | Redução de omissões relevantes com limite explícito para falsos alarmes; metas numéricas pendentes |
| Revisão | Profissional/revisor meteorológico e responsável de produto a identificar |

Os campos pendentes impedem concluir o aceite científico, mas não impedem preparar ferramentas ou auditar dados. Não inventar números de ganho ou amostra para preencher a tabela.

## Dados, normalização e referência observada

Cada caso deve identificar local, coordenadas, fuso, evento, unidade, data/hora válida, antecedência, modelo/provedor, parâmetros de requisição, coleta, fonte observada, regras de normalização, qualidade e motivo de exclusão. Registrar a emissão real quando disponível; se a API fornecer apenas offset fixo, registrar essa semântica sem inventar a emissão de uma execução específica.

Salvar as entradas permitidas pelas condições da fonte, com hashes e manifesto reproduzível. Dados coletados e relatórios podem permanecer no diretório já ignorado `.historical-reports/`; especificação, manifestos sem segredos e referências de proveniência podem ser versionados. Não coletar histórico pessoal de consultas.

O coletor poderá paginar períodos em janelas limitadas, respeitando cotas, retries e retomada; o limite atual de 31 dias por execução não é o tamanho máximo desejável do estudo. A análise deve conseguir reproduzir relatórios a partir das entradas já salvas, sem novas chamadas de rede.

Verificações mínimas:

- Coordenadas e números finitos; vento/chuva não negativos; unidades explícitas; mínima de temperatura não superior à máxima.
- Alinhamento por instante/fuso, janela de acumulação e validade; cálculo de horas esperadas pelo dia civil, incluindo dias de 23/25 horas quando aplicável.
- Horas ausentes, duplicações e ordem temporal tratadas explicitamente; evitar comparação entre a soma de poucas horas e um total diário completo.
- Cobertura mínima por evento, incluindo extremos de temperatura/rajada; nunca trocar ausência por zero ou conclusão segura de risco baixo.
- Total solicitado, recebido, elegível e excluído por motivo; mesma população elegível para v1/candidata na comparação principal.
- Compatibilidade entre a normalização histórica e a produção, documentando diferenças de campos diários do provedor versus agregados horários.

A referência observada deve ser congelada antes de ajustar a candidata. Alternativas a registrar separadamente:

1. Rótulos meteorológicos revisados sobre observações, com definição fixa de evento/severidade.
2. Rótulos de impacto revisados, quando se desejar validar alegações de dano ou risco real e houver dados adequados.
3. Concordância com v1 aplicada à reanálise, como diagnóstico inicial explicitamente heurístico; não substitui as referências anteriores nem comprova impacto.

Uma candidata não pode redefinir seu próprio alvo observado durante a comparação. Ausência de alerta INMET também não pode ser usada automaticamente como rótulo negativo de evento. Os alertas podem ser contexto adicional, com sua cobertura/validade documentadas.

## Métricas e avaliação

Definir a unidade principal como caso local/data/evento/antecedência; não contar horas correlacionadas como dias independentes. Apresentar separadamente nível diário geral, cada evento e erro de localização temporal dos picos quando aplicável.

Para classificação: matriz 3x3 low/moderate/high; precisão, recall e F1 por classe; resumo macro e suporte de cada classe; acurácia apenas como complemento. Acrescentar tabelas binárias para “moderado ou alto” e “alto”, com hits, misses, false alarms e correct negatives. Distinguir explicitamente proporção de falsos alarmes entre avisos emitidos de taxa de falsos positivos entre negativos observados.

Relatar por região/localidade, sazonalidade e antecedência. Para classe sem amostra ou denominador zero, registrar métrica indefinida e suporte insuficiente, sem fabricar zero/100%. Manter os contadores direcionais existentes como histórico, sem apresentá-los como métricas binárias convencionais.

Separar ajuste, validação de opções e teste final cronologicamente. Previsões de diferentes antecedências para o mesmo episódio/localidade precisam respeitar a divisão por validade/episódio para evitar vazamento. Se forem usados diferentes locais do mesmo evento meteorológico, considerar o agrupamento do episódio na análise e na incerteza. Após abrir o teste final, qualquer nova escolha de limiar exige nova avaliação reservada.

A comparação deve ser pareada nos mesmos casos e conter quantidade de eventos, deltas v1/candidata e incerteza amostral adequada, com método registrado. Ganho agregado não compensa automaticamente regressão importante em eventos severos ou em uma região do escopo proposto. Estratos insuficientes devem limitar a conclusão e o escopo de promoção.

Se o foco escolhido incluir correção dos valores previstos, criar trilha separada com viés, MAE/RMSE por variável/unidade/antecedência e diagnóstico de extremos. Comparações mínimas: dados originais+v1; originais+candidata; calibrados+v1; combinação somente depois das avaliações isoladas. Não misturar ganho de classificação com alegação de melhoria nos milímetros/graus previstos.

Fundamentação: tabelas de contingência e separação entre erro, habilidade relativa e utilidade são descritas no [guia ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=333775635). As antecedências fixas da fonte estão descritas na [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api). Essas fontes orientam método; não aprovam os limiares locais do ClimaPrev.

## Evolução técnica proposta

Preservar o avaliador e a baseline. Introduzir definição imutável de política com identidade explícita e vínculo ao conteúdo/configuração; diferenciar configuração experimental de baseline oficial. Validar finitude e ordem dos limiares: moderado menor que alto para chuva/vento/calor, ordem inversa para frio. Alterações de regras/coeficientes não podem reutilizar silenciosamente uma identidade já avaliada.

Separar no CLI as etapas de coleta, normalização/qualidade, montagem de casos, rótulos observados e comparação. Manter o comando existente compatível quando possível e acrescentar execução baseada em dados salvos. A escolha exata de arquivos/módulos novos deve ser definida durante implementação, sem impor uma arquitetura paralela.

Guardar resultado por caso, além dos agregados: ID, referência, previsão, política e razões de classificação/exclusão. Produzir relatório legível e saída estruturada com dataset/hash, versão do código, política/hash, configuração e critérios de decisão.

O cache atual guarda previsão normalizada, e o risco é avaliado depois da leitura. Portanto, uma mudança apenas de política não exige automaticamente invalidar esse cache por policy_version. O perfil de calibração já participa da chave porque altera os valores meteorológicos. Se houver cache de classificações no futuro, sua identidade deverá incluir a política. Testar esse comportamento antes da promoção.

Somente após aceite da candidata: implementar seleção explícita no backend, preservar v1 como fallback e registrar política em resposta/métricas. O frontend só precisa mudar quando houver alteração de contrato ou comunicação útil ao usuário. Não expor escolha experimental na consulta pública durante o estudo.

## Sequência de trabalho e critérios de saída

| ID | Entrega | Dependência | Critério de saída |
| --- | --- | --- | --- |
| C01 | Protocolo do experimento | Decisões de foco/escopo | Alvo, fontes, população, splits, metas e revisão registrados |
| C02 | Identidade e validação de políticas | Definição técnica mínima de C01 | V1 preservada; parâmetros inválidos rejeitados; candidata inequivocamente versionada |
| C03 | Qualidade/proveniência e execução offline | Fontes/variáveis de C01 | Casos reproduzíveis, horas/cobertura verificadas, entradas e exclusões rastreáveis |
| C04 | Referência observada congelada | C01/C03 | Rótulos e sua origem/versionamento independentes da política testada |
| C05 | Métricas e comparador | C04 | Matrizes e relatórios corretos, estratos e denominadores explícitos, comparação pareada |
| C06 | Baseline representativo da v1 | C03–C05 | Perfil de erros e suficiência da amostra por evento/antecedência documentados |
| C07 | Definição/ajuste da candidata | C02/C06 | Justificativa de cada alteração; busca de opções restrita ao ajuste/validação |
| C08 | Teste final reservado | C07 e protocolo congelado | Resultado fora do ajuste, incerteza e regressões estratificadas registrados |
| C09 | Revisão e decisão | C08 | Promover, rejeitar ou ampliar estudo, com parecer e limites |
| C10 | Integração e rollout/rollback | Promoção aprovada em C09 | Contratos/testes/gates aprovados e retorno à v1 demonstrado |

C02 e partes de C03/C05 podem avançar em paralelo após definição dos contratos. C01 não exige resolver toda a observabilidade pública; C10 depende de gates funcionais/operacionais aplicáveis, incluindo a falha de navegador já registrada em F09. Documentação e decisões acompanham todas as entregas.

## Testes necessários durante implementação

- Política: identidade correta, baseline sem mudanças, limiares finitos/ordenados, valores exatamente nos limites e None.
- Dados: cobertura parcial, horários civis, dias de 23/25 horas, séries desalinhadas, unidades, inválidos e exclusões.
- Alvos: mesmos rótulos para todas as candidatas e separação entre meteorologia/reanálise/impacto.
- Métricas: matrizes com contagens conhecidas, confusão entre classes, denominadores zero, classes raras e estratificação.
- Reprodutibilidade: mesmas entradas/configuração produzem as mesmas classificações e métricas; timestamps de execução ficam em metadados separados.
- Integração: perfil disabled preservado, calibração/caches coerentes, policy_version correto, prioridade INMET preservada e rollback funcional.

Os testes devem verificar comportamentos e resultados, não apenas a presença de strings ou funções. Avaliação com fixtures não substitui o estudo real.

## Gate de promoção e resultados possíveis

Antes de avaliar a candidata, preencher e registrar as metas numéricas de ganho, limite de falsos alarmes, tolerâncias por estrato, qualidade e suficiência amostral. O teste final não deve servir para escolher essas metas.

Promoção exige: dados reproduzíveis e elegíveis; comparação com referência fixa e v1; metas satisfeitas no teste reservado; limitações/regressões aceitas explicitamente pela revisão; artefatos/versionamento completos; integração e rollback verificados. Dados insuficientes resultam em “inconclusivo”, não em aprovação automática.

O nome reference-candidate-1 permanece experimental. A versão pública de eventual sucessora será uma decisão posterior, sem renomear retroativamente experimentos para encobrir mudanças. Se os resultados não justificarem ganho, manter v1 e registrar o aprendizado é uma conclusão válida.

## Decisões ainda abertas

1. Primeiro evento/variável a ajustar, orientado pelo diagnóstico da baseline; dois experimentos separados com base comum são a proposta de sequência.
2. Público/localidades e primeiro evento prioritário, condicionados ao diagnóstico da baseline.
3. Fonte dos rótulos, disponibilidade/licença das entradas e revisor.
4. Períodos, suficiência amostral, cobertura e metas de promoção.
5. Inclusão posterior de regras regionais/sazonais, conforme dados disponíveis.

## Referências internas

- `docs/planejamento/possivel-continuacao-viabilidade-de-aumento-de-escopo-de-previsao.md`, etapas 0–6.
- `docs/arquitetura/validacao-e-calibracao.md`.
- `docs/projeto/PossivelPlanoDeEvolução.md`, item 17.
- `docs/projeto/STATE.md`, relato do piloto e ressalvas.
- `docs/contexto/RELATORIO-HISTORICO-REFERENCE-V2-2026-10-16.md`, reconstrução histórica e limites.

Esta entrega contém análise e planejamento. Nenhuma implementação de candidata, coleta nova, mudança de limiar ou promoção foi realizada.
