# Protocolo técnico — etapas 1 a 5

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

Versão: `reference-candidate-1-stages-1-5-2026-10-16-v1`. Data: 16/10/2026.

O JSON homônimo congela o desenho técnico deste ciclo. Não declara que os dados estão completos, que existe aprovação científica ou que uma candidata pode ser ajustada. A autorização vigente termina na etapa 5: **não iniciar a etapa 6, estimar novos limiares, ajustar calibração ou promover política**. Essa parada depende do escopo autorizado pelo usuário, mesmo que revisões futuras sejam favoráveis.

## Separação temporal e prevenção de vazamento

| Uso | Período | Regra |
| --- | --- | --- |
| Ajuste futuro e preparação atual | 2024 | Coleta inicial dos dias 1 a 28 de janeiro, abril, julho e outubro em Belém, Brasília e Porto Alegre, D+1/D+3/D+7, com dia 29 para fronteira; inspeção diagnóstica permitida. |
| Diagnóstico já consultado | Janeiro de 2025 | Piloto de Belém; excluído de qualquer alegação de validação ou teste inédito. |
| Intervalo não utilizado | Fevereiro a junho de 2025 | Não incorporar silenciosamente para escolher resultados favoráveis. |
| Validação reservada | Julho a dezembro de 2025 | Não consultar resultados nas etapas 1 a 5. |
| Teste final reservado | Janeiro a junho de 2026 | Abrir apenas em etapa posterior autorizada, após congelar parâmetros e decisão de validação. |

Os períodos substituem, para este ciclo, os exemplos do protocolo piloto anterior, que nunca representaram reserva aprovada. Reserva documental não prova ausência de acesso anterior: o manifesto deve auditar todas as evidências locais. Se houver consulta prévia, colocar os casos afetados em quarentena e versionar outra reserva antes do ajuste. As localidades e os meses são escolhas de cobertura sazonal, sem selecionar dias pelo desempenho do modelo. Três locais não sustentam conclusão nacional; esta é a amostra inicial, sem suficiência científica presumida.

## Referências e qualidade

Separar observações INMET de reanálise ERA5. A estação mede condições meteorológicas; não fornece automaticamente rótulos de impacto ou desastre. A regra v1 aplicada às observações produz um alvo meteorológico congelado, não uma classificação oficial. Registrar fonte, estação, coordenadas, unidades, hashes, fuso, convenção temporal e versão do algoritmo.

Usar `civil-day-preceding-hour-v1`, preservar os arquivos originais e exigir 100% de cobertura por variável. A chuva e os extremos da hora anterior são atribuídos ao intervalo correspondente, incluindo a fronteira do dia seguinte. Não substituir ausência por zero. Comparar as variantes sobre os mesmos casos elegíveis e registrar exclusões. Extremos horários INMET e temperaturas instantâneas do modelo têm semânticas diferentes; a diferença deve acompanhar qualquer métrica.

## Comparação futura e incerteza

R0 mantém v1 sem calibração; A muda apenas política; B muda apenas calibração; AB combina as duas. O alvo permanece idêntico em todas. Nesta autorização, executar somente a preparação e o diagnóstico R0.

Predefinir matriz de confusão, detecção de alto e de pelo menos moderado, falsos alarmes, precisão, macro-F1 e erros direcionais; para variáveis meteorológicas, viés, MAE e RMSE. Estratificar por evento, local, antecedência, mês e fonte. Ausência de eventos produz resultado indefinido ou inconclusivo, nunca sucesso artificial.

O plano de incerteza, ainda não implementado, usa bootstrap pareado em blocos de sete dias, 2.000 réplicas e intervalo percentil de 95%; sensibilidades de três e 14 dias. Manter todos os locais e horizontes de uma data juntos e reamostrar janelas descontínuas separadamente. Estes parâmetros são escolhas técnicas explícitas, pendentes de revisão científica, e não garantias de suficiência estatística.

## Critérios e pendências antes da etapa 6

Propõe-se não aceitar queda de detecção de alto risco nem aumento da proporção de falsos alarmes. Para calibração, MAE/RMSE não devem piorar; uma alegação de melhora exige intervalo pareado abaixo de zero para uma métrica principal predefinida. Reportar todos os estratos, inclusive os desfavoráveis. Falta de suporte em eventos críticos torna a conclusão inconclusiva.

Ainda devem ser definidos por revisão científica: evento e métrica principal, número mínimo de eventos, precisão desejada, ganho mínimo relevante e tolerância de produto a falsos alarmes. Não preencher esses valores arbitrariamente. A definição técnica acima não constitui aceite científico.

Antes de qualquer ajuste futuro, congelar também os dados reais, os alvos, o código e seus hashes em manifesto próprio. Alterações neste protocolo exigem novo identificador, justificativa e registro anterior à consulta dos resultados. A CLI histórica atual valida períodos cronológicos, mas **não aplica sozinha os campos de autorização e aceite científico**; não apresentar este documento como trava automática da aplicação. A parada na etapa 6 é uma restrição operacional explícita desta execução.
