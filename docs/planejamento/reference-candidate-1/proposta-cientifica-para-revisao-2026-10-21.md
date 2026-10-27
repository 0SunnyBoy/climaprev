# Proposta científica para revisão da candidate-1

**Atualização de 23/10/2026:** [direção aprovada pelo usuário](aprovacao-direcao-2026-10-23.md), incluindo objetivo inicial de chuva D+1, meta inicial de 5% e avaliações de outras variáveis. O texto abaixo preserva a proposta submetida em 21/10; suas afirmações de ausência de aprovação descrevem aquele momento. O registro de aprovação delimita o que foi aceito e os parâmetros ainda pendentes.

Data: 21/10/2026. **Status: proposta não aprovada.** Responsável pelo aceite: usuário solicitante. Nesta continuação, o usuário pediu revisar a proposta detalhada antes de aprovar. Não foram escolhidos objetivo primário, margens nem conjunto confirmatório. Não foram lidos novos outcomes reservados, ajustados pesos ou alterada a reference-v1.

## 1. O que queremos demonstrar

A evolução deve reduzir o erro dos valores meteorológicos retornados pelo ClimaPrev e preservar a detecção de condições perigosas. São duas perguntas distintas: prever chuva/temperatura/vento com menor erro e classificar risco de modo útil. Uma candidata pode melhorar a média e piorar os extremos; isso impede promoção automática.

Primeiro comparar cada modelo individual com a previsão operacional congelada. Só depois avaliar correção de viés ou combinação. A previsão fornecida pela API e a política de classificação devem ter identidades separadas: reference-v1 é uma política de risco, não um modelo meteorológico como GFS/ICON/IFS. Para avaliar valores físicos, o comparador é a previsão atual arquivada; para avaliar a política, usar a mesma entrada meteorológica entre políticas. A avaliação ponta a ponta é uma terceira comparação, identificada como tal.

## 2. Escolha do objetivo primário

Escolher uma opção **antes de examinar os resultados do novo teste**. As demais passam a análises secundárias; não mudar o objetivo depois de descobrir qual variável melhorou.

| Opção | Alvo | Benefício | Condição necessária |
|---|---|---|---|
| A — recomendação inicial de produto | Chuva acumulada no dia civil local em D+1 | Ataca um componente relevante do risco e permite avaliar volume e episódios de chuva | Observação com cobertura completa e mesmo intervalo; dias secos podem dominar MAE, exigindo proteção para extremos |
| B | Temperatura máxima em D+1 | Resultado simples de comunicar e medir em °C | Resolver extremos instrumentais de intervalo versus amostras horárias do modelo; a equivalência ainda não está aprovada |
| C | Classificação de evento/risco em D+1 | Aproxima a avaliação da decisão do usuário | Definir alvo observacional válido e obter suporte positivo suficiente; classificação heurística não equivale a impacto observado |

D+3 e D+7 devem ser reportados separadamente como secundários, sem transformar os três horizontes em três amostras independentes. Nenhuma opção está aprovada. A recomendação A é uma escolha proposta para este produto, não uma exigência WMO.

## 3. Variáveis e referência observacional

| Variável | Unidade | Alvo proposto | Restrição |
|---|---|---|---|
| Chuva diária | mm por intervalo | Soma horária no dia civil da estação | Exigir horas válidas, definir fronteiras e não misturar com boletim encerrado às 12 UTC |
| Temperatura | °C | Extremo ou média com definição instrumental explícita | Não corrigir automaticamente diferença entre extremo de intervalo e amostra instantânea |
| Rajada/vento | km/h | Medida e intervalo compatíveis com o campo previsto | Rajada, vento sustentado e amostra instantânea não são intercambiáveis |
| Umidade | % | Agregação horária definida | Cobertura e unidade verificadas; não inferir valor ausente |
| Probabilidade de chuva | % | Evento binário observável, limiar e período fixados | Não chamar concordância entre modelos de probabilidade calibrada |

INMET instrumental é referência observacional dos valores compatíveis. ERA5 é controle de reanálise, identificado separadamente. Alertas oficiais são comunicação de perigo e não são rótulos automáticos de chuva ocorrida ou impacto. Estação verifica o ponto/instrumento, não toda a cidade; registrar distância, altitude quando disponível, coordenadas da estação e da grade.

Os dados de 2024 e o piloto Belém janeiro/2025 já examinados continuam exploratórios. O encerramento às 12 UTC reconciliado anteriormente deve continuar como controle separado. Não converter reconciliação numérica em aprovação de equivalência dos intervalos.

## 4. Separação dos dados e coleta prospectiva

1. Inventariar origem, período, uso anterior e hashes sem abrir outcomes para decidir inclusão. Reservas antigas permanecem com independência não demonstrada.
2. Definir calendário, estações e estratos por necessidade de cobertura, sem selecionar datas/local pelo desempenho observado. A201, A001 e A801 são bases exploratórias existentes, não amostra representativa aprovada para todo o Brasil.
3. Se não for possível demonstrar independência histórica, iniciar campanha prospectiva **após** aprovar e congelar este desenho. Data de início, duração e frequência ainda precisam ser definidas.
4. Separar desenvolvimento, validação e teste final por tempo. Todos os horizontes e estações ligados ao mesmo episódio/data devem permanecer no mesmo grupo; não fazer divisão aleatória de linhas correlacionadas.
5. Guardar previsões antes de sua validade e registrar horário real de emissão, coleta e disponibilidade. Uma previsão publicada após o início do período-alvo não verifica honestamente D+1.
6. Congelar configuração antes da abertura do teste; não ajustar pesos, selecionar modelo nem decidir interrupção com base nesse resultado. Mudança posterior cria nova versão e novo teste independente.

Para D+1/D+3/D+7, definir validade como dia local alvo e registrar também a antecedência real em horas a partir da emissão/disponibilidade. APIs com nomes iguais de "previous runs" podem ter convenções distintas; o rótulo do endpoint não basta.

## 5. Casos elegíveis e indisponibilidade

Cada par previsão/observação precisa ter local, intervalo, unidade e horizonte compatíveis e passar pelos controles de qualidade. Observação ausente não vira zero nem recebe preenchimento silencioso. Para chuva diária, a proposta inicial é cobertura horária completa; outra tolerância exige justificativa e aprovação anteriores ao teste.

Comparar modelos nos mesmos pares elegíveis, publicando também cobertura de cada um, exclusões e motivo. A interseção dos casos pode favorecer fornecedores que falham justamente nos extremos; portanto, reportar indisponibilidade por local, data, horizonte e evento. O relatório operacional ponta a ponta deve mostrar falhas de entrega e fallback separadamente, sem atribuir ao modelo ausente a previsão de outro como se fosse sua.

## 6. Métricas e incerteza

Para valores físicos, erro = previsão − observado. Reportar MAE = média do erro absoluto, RMSE = raiz da média do erro quadrático e viés = média do erro, nas unidades da variável. Não somar diretamente erros em mm, °C e km/h.

Para o alvo principal, calcular diferença pareada MAE_candidata − MAE_baseline e ganho relativo = 1 − MAE_candidata/MAE_baseline. Se a baseline tiver MAE zero, o ganho relativo é indefinido; reportar diferença absoluta sem criar divisão artificial.

Por evento, publicar hits, misses, falsos alarmes e rejeições corretas. Detecção = hits/(hits+misses); precisão = hits/(hits+falsos alarmes); razão de falsos alarmes = falsos alarmes/(hits+falsos alarmes). Não confundir essa razão com taxa de falso positivo, que usa falsos alarmes + rejeições corretas no denominador. Denominador zero resulta em indefinido, não desempenho perfeito.

Separar dias secos/chuvosos, intensidades, local, estação sazonal e horizonte; fixar os limiares antes do teste. MAE de todos os dias pode esconder perda em chuva intensa. Para probabilidade, Brier score e calibração só devem ser usados quando o produto probabilístico e o evento observado estiverem definidos.

Intervalos propostos de 95% com reamostragem pareada por blocos temporais que preservem dependência e agrupamento por data. A duração do bloco deve ser definida com dados de desenvolvimento e justificada antes do teste. O segmento conhecido de três dias não sustenta automaticamente bloco de sete; não excluir janeiro retroativamente para melhorar intervalo. Se não houver suporte, o resultado é inconclusivo.

Um contraste primário previamente declarado evita escolher vencedor entre dezenas de comparações. Se vários candidatos ou objetivos forem confirmatórios, definir correção de multiplicidade e seleção em validação antes de abrir o teste. Não declarar todos confirmatórios sem essa regra.

## 7. Aprovação proposta

| Critério | Proposta para discussão | Situação |
|---|---|---|
| Ganho principal | Redução relativa de MAE de pelo menos 5%, com intervalo da diferença pareada favorável, no alvo aprovado | 5% é proposta de produto, não um limite científico já validado |
| Relevância física | Definir também redução mínima em mm ou °C conforme objetivo e uso | Valor pendente; não inventar benefício a partir de porcentagem pequena |
| Extremos | Não aceitar perda operacionalmente relevante de detecção; avaliar junto falsos alarmes e incerteza | Margem, limiares e custos de omissão/falso alarme pendentes |
| Estratos críticos | Não esconder degradação regional/sazonal em média agregada | Estratos e tolerâncias pendentes |
| Amostra | Duração/cobertura planejadas pela precisão desejada, dependência e frequência de eventos | Sem número universal de dias; suporte positivo para extremos ainda insuficiente |
| Operação | Cobertura, atraso, fallback e latência compatíveis com a aplicação | Valores-alvo e ambiente de medição devem ser fixados antes da integração |

Se faltar um critério, a saída é "inconclusivo" ou "não aprovado", e não promoção automática. Aprovar o protocolo autoriza somente o desenho explicitamente aceito; promoção para a aplicação é outra decisão após os resultados.

## 8. Sequência após sua revisão

1. Registrar suas escolhas e justificativas em nova versão, preservando protocolos e resultados antigos.
2. Fechar catálogo de fornecedores/modelos e condições de uso, com identidade de modelo para evitar duplicações.
3. Implementar coleta, manifesto e normalização experimental, sem aumentar a latência da consulta pública.
4. Formar a campanha e verificar qualidade/proveniência. Não escolher a amostra pela melhoria observada.
5. Comparar modelos individuais com a baseline arquivada; selecionar hipóteses apenas em desenvolvimento/validação.
6. Avaliar correção/combinação em braço separado; congelar, testar e gerar relatório com todos os resultados, inclusive negativos.
7. Só integrar candidata qualificada com fallback v1, identificação das fontes e novos checks de contrato, acessibilidade e desempenho.

## 9. Decisões solicitadas ao responsável

- Escolher A, B ou C para o objetivo principal e confirmar D+1; D+3/D+7 como secundários.
- Aceitar ou ajustar a convenção de dia civil e a exigência de cobertura, após validar a semântica da observação.
- Definir se novas reservas serão prospectivas quando não houver prova da independência das antigas.
- Aprovar/alterar os 5% propostos, a diferença absoluta relevante e as margens para extremos/estratos.
- Definir localidades/cobertura sazonal, precisão desejada e orçamento de campanha; duração deve decorrer disso.

Essas decisões ainda não foram tomadas. É possível revisar em partes; uma aprovação parcial deve identificar os campos aceitos, mantendo os restantes pendentes.

## Referências e relação com o projeto

- [Conceitos de verificação determinística ECMWF](https://confluence.ecmwf.int/spaces/FUG/pages/673551834/Section+12.A+Statistical+Concepts+-+Deterministic+Data): distinção entre acurácia, skill e utilidade; métricas de erro. Não prescreve o ganho de 5% deste projeto.
- [Verificação espacial e de precipitação ECMWF](https://www.ecmwf.int/en/about/media-centre/science-blog/2023/verifying-high-resolution-forecasts): alcance e limitações de comparações pontuais de precipitação.
- [Representatividade na verificação ECMWF](https://www.ecmwf.int/en/elibrary/81173-accounting-representativeness-verification-ensemble-forecasts): erro de representatividade na comparação de modelos com observações.
- [Revisão preparatória local](revisao-preparatoria-2026-10-20.md), [critérios anteriores](criterios-para-aceite-2026-10-20.md) e [RDP](../../../RELATORIO-PENDENCIAS-2026-10-20.md).

A recomendação de sequência e os critérios quantitativos são uma proposta específica para o ClimaPrev. As referências sustentam os conceitos de verificação, não aprovam a amostra, os limiares ou a candidata do projeto.
