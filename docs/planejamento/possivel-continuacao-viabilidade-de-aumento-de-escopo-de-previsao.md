# Possível continuação — viabilidade de aumento de escopo de previsão

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Documentação de referência: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

**Status:** etapa preparada para execução offline; `reference-v1` continua ativa.

## Objetivo

Avaliar se o ClimaPrev pode ampliar o escopo de previsão com base em dados
históricos, sem adicionar inteligência artificial ao produto e sem alterar o
comportamento atual antes de haver evidência suficiente.

A ampliação pode envolver:

- maior cobertura geográfica;
- mais localidades ou regiões;
- horizonte superior aos sete dias atuais, se o contrato do provedor permitir;
- limiares de risco específicos por região ou estação.

Nenhuma dessas ampliações é ativada automaticamente por esta tarefa.

## Limites da tarefa

Esta tarefa não inclui:

- IA, machine learning ou treinamento de modelos;
- alteração imediata dos limiares em produção;
- aumento automático do período aceito pela API;
- chamada de dados históricos durante uma consulta normal;
- substituição de alertas oficiais por uma heurística;
- remoção da política `reference-v1`.

A aplicação atual permanece funcionando com a política e o contrato já
validados. A análise histórica acontece em um processo offline separado.

## Fontes de dados e uso correto

| Fonte | Uso | Limitação |
| --- | --- | --- |
| Historical Weather API | Climatologia, frequência, sazonalidade e plausibilidade dos limiares. | Usa reanálise; não representa exatamente as previsões emitidas no passado. |
| Historical Forecast API | Comparação entre previsões históricas e condições posteriores. | A cobertura histórica é mais recente e depende do modelo disponível. |
| Previous Runs API | Avaliação por horizonte fixo, como 1, 2, 3 e 7 dias. | Exige alinhamento correto entre data de emissão e data válida. |
| Observações oficiais | Referência para o que realmente ocorreu no local. | Cobertura de estações, qualidade e representatividade precisam ser verificadas. |

A documentação oficial do Open-Meteo indica que a Historical Weather API
oferece reanálise desde 1940, enquanto os arquivos de previsão histórica e
Previous Runs são mais adequados para avaliar a qualidade da previsão:

- [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api);
- [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api);
- [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api).

## Processo de execução

### Etapa 0 — Definir o experimento

Registrar antes da coleta:

- região e localidades do piloto;
- eventos: chuva horária, chuva diária, rajada e temperatura extrema;
- horizontes: por exemplo, 1, 3 e 7 dias;
- período histórico;
- fonte de observação;
- métrica de aceitação;
- responsável pela revisão meteorológica.

O experimento deve começar pequeno. Uma expansão nacional só deve ser
considerada depois que o piloto apresentar cobertura e resultados estáveis.

### Etapa 1 — Montar a base offline

Criar um conjunto versionado contendo, no mínimo:

- local e coordenadas;
- data de emissão da previsão;
- data e hora válidas;
- horizonte da previsão;
- valores previstos;
- valores observados;
- fonte, modelo, unidade e fuso;
- indicador de dado ausente ou inválido.

A aplicação não deve armazenar localização de usuário para formar essa base.
A coleta deve usar localidades e coordenadas do experimento, fora do fluxo
normal da API.

### Etapa 2 — Reproduzir `reference-v1`

Aplicar offline os mesmos campos usados pelo `RiskEvaluator` atual:

- `precipitation_max_hourly_mm`;
- `precipitation_sum_mm`;
- `wind_gust_max_kmh`;
- `temperature_max_c`;
- `temperature_min_c`.

O primeiro resultado deve ser um baseline da política atual. Sem esse
baseline, não é possível afirmar que uma futura política melhorou.

### Etapa 3 — Medir desempenho

Separar os dados por tempo, sem embaralhar períodos futuros no conjunto de
calibração. Medir, por evento, região e horizonte:

- precisão;
- recall;
- F1-score;
- falsos positivos;
- falsos negativos;
- matriz de confusão;
- estabilidade por estação e período.

Para risco climático, falsos negativos devem receber atenção especial. Uma
melhora de precisão que aumente omissões perigosas não deve ser aceita.

### Etapa 4 — Avaliar uma candidata

Somente depois do baseline, testar limiares alternativos ou regras regionais
em uma política candidata. A candidata deve ser identificada separadamente,
por exemplo `reference-candidate-1`, e nunca substituir `reference-v1` durante
a análise.

A avaliação deve usar um período de teste que não participou da escolha dos
limiares. O resultado deve mostrar a comparação direta entre as políticas.

### Etapa 5 — Revisão especializada

Um profissional de meteorologia ou risco climático deve revisar:

- definição dos eventos;
- qualidade e representatividade das observações;
- limiares por região e estação;
- custo relativo de falsos positivos e negativos;
- coerência entre o texto exibido e a evidência.

### Etapa 6 — Decisão de escopo

A expansão só é aprovada se houver:

- cobertura de dados suficiente;
- melhoria consistente no conjunto de teste;
- ausência de regressão grave em eventos de alta severidade;
- revisão especializada registrada;
- contrato atualizado para datas, regiões e respostas;
- plano de observabilidade e rollback.

## Fallback e rollback

A proteção mínima obrigatória é:

1. manter `reference-v1` como política ativa e padrão;
2. executar candidatas somente offline antes da promoção;
3. preservar `policy_version` na resposta e nos relatórios;
4. não substituir limiares por edição manual sem teste e revisão;
5. guardar o relatório e os dados de entrada usados para a decisão;
6. promover uma nova versão somente por mudança explícita e revisável;
7. retornar à `reference-v1` se houver regressão, indisponibilidade ou dúvida.

O rollback deve ser uma troca explícita de versão seguida de testes de
contrato. A política anterior não deve ser apagada quando uma candidata for
promovida.

## Critério para aumento do horizonte

O limite atual de sete dias só pode aumentar se:

- o provedor suportar o novo horizonte com estabilidade;
- a resposta tiver dados completos para o período adicional;
- os testes validarem datas além do contrato atual;
- o cache e o orçamento externo suportarem o volume extra;
- a qualidade do dado for apresentada ao usuário;
- a política de risco for avaliada separadamente para cada horizonte.

A existência de dados históricos não prova, por si só, que um horizonte
maior seja confiável.

## Entregáveis da task

- especificação do experimento;
- dataset offline versionado ou identificador reproduzível;
- script de preparação e validação;
- relatório do baseline `reference-v1`;
- comparação com políticas candidatas;
- revisão especializada;
- decisão de manter, alterar ou ampliar o escopo;
- plano de promoção e rollback.

## Viabilidade atual

| Dimensão | Avaliação |
| --- | --- |
| Execução offline sem IA | Alta |
| Validação de limiares | Alta, se houver observações adequadas |
| Avaliação de precisão da previsão | Média; depende do arquivo de previsões históricas |
| Expansão imediata do horizonte | Não recomendada sem validação |
| Mudança no backend atual | Não necessária na fase de estudo |

A próxima continuação recomendada é um piloto offline pequeno. A política
`reference-v1` permanece o fallback até que todos os entregáveis e critérios
sejam aprovados.
