# Frente 2 — Protocolo para revisão

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

**Estado em 28/10:** [aceite delegado registrado](aceite-delegado-parametros-2026-10-28.md). Escolhas de desenho aceitas com condições; margens e suporte dependentes dos dados não foram declarados validados. As referências a espera de aceite abaixo descrevem a proposta anterior e são superadas nos limites do novo registro.

Data: 27/10/2026. **Proposta em revisão; sem aprovação dos parâmetros finais ou início de campanha.** O usuário aprovou a direção científica e depois solicitou revisar os parâmetros antes de aceitá-los. Este documento organiza essa revisão, sem substituir protocolos ou resultados históricos congelados.

## Decisão que o estudo deve sustentar

Verificar se uma candidata congelada melhora a previsão de chuva diária D+1 em comparação com a baseline operacional nos mesmos casos, com utilidade prática e proteção de extremos. A direção inicial aceita busca pelo menos 5% de redução no MAE, acompanhada de evidência favorável. Isso é um objetivo, não resultado alcançado.

Previsão de temperatura, vento/rajada, umidade e outros horizontes entram como avaliações secundárias, cada qual com semântica e critérios próprios. Classificação de risco e precisão meteorológica serão avaliadas separadamente. A reference-v1 permanece ativa até eventual aceite e integração qualificada.

## Separação das etapas

| Etapa | Finalidade | Dados e condições | O que não pode concluir |
|---|---|---|---|
| Piloto técnico | Verificar horários, campos, rodadas, disponibilidade e cobertura | Proposta de 14 dias nas estações propostas; exige aceite e calendário | Não prova superioridade ou robustez sazonal; não amplia o horizonte público |
| Desenvolvimento | Testar correções, combinações e diagnosticar dependência temporal | Dados exploratórios conhecidos ou janelas de desenvolvimento declaradas antes do uso | Não serve como teste final independente |
| Validação de seleção | Escolher uma alternativa segundo regra registrada | Partição separada do ajuste e da confirmação | Não autoriza continuar alterando pesos após consultar confirmação |
| Confirmação | Avaliar uma candidata já congelada | Proposta de 12 meses posteriores ao congelamento; calendário e suporte ainda pendentes | Não garante eventos extremos suficientes ou representatividade nacional |
| Integração | Disponibilizar uma versão aprovada | Depende de resultados, aceite e testes da aplicação | Aprovação de infraestrutura não equivale a aprovação científica |

Os 12 meses propostos são para a confirmação; não significam que toda melhoria do ClimaPrev dependa de um ano de espera. Faltando suporte, o resultado é inconclusivo, sem prolongar seletivamente a avaliação até conseguir ganho.

## Parâmetros para decisão do usuário

| Tema | Proposta vigente | Estado e ajuste necessário |
|---|---|---|
| Pontos | A201 Belém, A001 Brasília, A801 Porto Alegre | Não aprovados; confirmar operação e metadados antes de ativar. Três locais não representam todo o país |
| Datas e duração | Piloto de 14 dias; confirmação de 12 meses | Não aprovados; fixar datas depois da viabilidade e do congelamento exigido em cada etapa |
| Antecedência | Chuva D+1 principal; D+3/D+7 secundários | Direção aceita; definir rodada-alvo, disponibilidade e antecedência em horas. Dia após coleta não prova antecedência da rodada |
| Ganho | 5% de MAE como direção; 0,5 mm/dia como margem física proposta | A margem física não está aprovada nem justificada para todos os regimes; revisar utilidade por contexto |
| Extremos | Propostas de margens de cinco pontos percentuais em detecção e falsos alarmes | Não aprovadas; discutir custo de omissão e falso alarme e avaliar incerteza. Não são autorização para degradar extremos |
| Cobertura | Dias completos por alvo, com exclusões e denominador planejado | Método técnico pode avançar; cobertura mínima e suporte de eventos ainda precisam de definição |
| Incerteza | Proposta de 95% e blocos iniciais de sete dias | Não aprovada; comprimento requer diagnóstico em desenvolvimento. Congelar método e tratamento de múltiplas análises antes da confirmação |
| Rodada desconhecida | Baseline automática e algumas fontes têm limitações de identificação | Separar comparação por disponibilidade de comparação em rodada equivalente; não declarar equivalência de antecedência sem evidência |

Não é necessário aprovar os valores acima como um pacote único. Recomenda-se revisar primeiro locais e piloto; após o diagnóstico técnico, fechar critérios estatísticos e desenho confirmatório antes de sua execução.

## Controle de D+7: recomendação para revisão

Manter D+1 como comparação principal com baseline operacional. Em D+7, registrar explicitamente a ausência da baseline pública atual e comparar apenas modelos meteorológicos com dados e antecedências elegíveis, como avaliação secundária exploratória. Não produzir uma baseline D+7 por extrapolação nem ampliar o endpoint público para resolver a lacuna.

Essa opção não comprova superioridade sobre a reference-v1 em D+7. Se o objetivo for uma alegação desse tipo, será necessário aprovar e versionar outro controle experimental, separado do produto atual. A recomendação ainda não é decisão aprovada.

## Contratos de medição para a Frente 1

| Alvo | Comparação compatível no contrato | Lacuna atual / ação necessária |
|---|---|---|
| Chuva acumulada | Mesma quantidade em mm, no mesmo intervalo exato, com cobertura completa | Pareamento diário exploratório existe; intervalos de 6/12 h não podem ser divididos silenciosamente para fabricar horas |
| Rajada máxima horária | Máximos do mesmo intervalo horário em km/h | Contrato de semântica implementado para diagnóstico; falta ligação ao pareamento prospectivo e confirmação instrumental |
| Temperatura extrema horária | Máxima com máxima ou mínima com mínima no mesmo intervalo | Normalizador experimental atual fornece temperatura instantânea; não tratar isso como extrema horária |
| Temperatura instantânea | Mesmo instante e unidade °C, com significado observacional confirmado | Importador INMET atual usado na campanha experimental não entrega esse alvo instantâneo |
| Umidade instantânea | Mesmo instante, porcentagem válida e semântica confirmada | Falta incorporar e validar a coluna observacional correspondente; não usar extrema horária como instantânea |
| Vento sustentado | Exige altura e período de média compatíveis | Sem contrato habilitado; vento instantâneo não substitui rajada e apenas converter m/s para km/h não resolve a semântica |

O verificador `experimental_equivalence.check_equivalence` apenas verifica os valores, unidades, semântica declarada e intervalo de um par. Não autentica a fonte, não valida distância estação/grade, instrumentação, altura ou antecedência, não agrega dias e não calcula ganho. Uma saída compatível não é aprovação científica nem elegibilidade completa para a campanha.

Os contratos instantâneos e de extremos são interfaces para preparação; não alegam que os adaptadores já forneçam todas essas medições. Diagnósticos históricos de temperatura/rajada existentes permanecem exploratórios e preservados, sem reclassificação como confirmação.

## Próxima entrega técnica

Receber decisões sobre o piloto, preparar o pareamento das variáveis com contratos documentados e fechar cobertura científica e incerteza segundo o desenho que vier a ser aceito. Nenhuma coleta recorrente, fitting, abertura de novos resultados reservados ou promoção foi iniciada nesta revisão.

## Evidências e fontes

- [Parâmetros detalhados ainda propostos](parametros-campanha-propostos-2026-10-23.md).
- [Revisão solicitada pelo usuário](revisao-parametros-2026-10-27.md).
- [Direção aprovada e limites](aprovacao-direcao-2026-10-23.md).
- [Open-Meteo — documentação das variáveis](https://open-meteo.com/en/docs): distinção de instantâneos, somas e máximos da hora anterior.
- [MET Norway — formato temporal](https://docs.api.met.no/doc/ForecastJSON.html): valores instantâneos e precipitação em períodos seguintes.
- Código local: `experimental_normalization.py`, `inmet_observations.py`, `experimental_pairing.py` e `compare_station_variables.py`. Regras propostas aqui não alteram essas fontes históricas.

## Atualização técnica de 28/10/2026

O contrato passou a ser consultado pelo pareamento de chuva; demais alvos continuam sem pareamento prospectivo completo. Controle por estrato e avaliador diagnóstico de critérios foram implementados, sem cálculo de incerteza ou aprovação automática. Ver [execução até a ordem 4](../../operacoes/frente-2-ordens-1-a-4-2026-10-28.md) e [parâmetros estruturados para revisão](frente-2-protocolo-proposto-2026-10-28.json). Valores propostos continuam não aprovados.

## Fechamento da preparação em 28/10/2026

[Verificação das estações, calendário, partições e critérios](../../operacoes/preparacao-frente-2-etapas-1-a-4-2026-10-28.md). Aplicado aceite delegado a um desenho conservador: cobertura comum de 90% como regra operacional, sem tolerância automática à piora dos extremos e requisito explícito de precisão. Não são valores empiricamente validados ou norma externa. Limite de 0,5 mm e antigas margens de cinco pontos percentuais permanecem exploratórios. As três estações estão operantes no catálogo; dados recentes consultados retornaram 204 e Belém tem divergência cadastral com o CSV histórico. Não declarar observações atuais prontas ou campanha confirmatória liberada. Bloco temporal final ainda depende do diagnóstico dos erros em desenvolvimento.
