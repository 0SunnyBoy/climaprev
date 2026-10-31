# Parâmetros propostos para a campanha

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

**Proposta para revisão, não aprovada.** Complementa a direção já aprovada; nenhuma campanha, fitting ou leitura de novos outcomes reservados foi iniciada. Valores abaixo são escolhas operacionais propostas, não normas meteorológicas.

## Plano concreto para deliberação

| Decisão | Proposta | Motivo e limite |
|---|---|---|
| Locais iniciais | Estações A201 Belém, A001 Brasília e A801 Porto Alegre | Continuidade dos diagnósticos existentes e contraste regional; não representa o Brasil inteiro. Confirmar atividade, metadados e qualidade antes de iniciar |
| Local da previsão principal | Coordenadas verificadas da estação | Reduz confusão entre consulta municipal e ponto instrumental; grade e estação continuam distintos |
| Objetivo primário | Chuva em mm no dia civil local, D+1 | Direção já aprovada; D+3/D+7 e demais variáveis secundários |
| Pré-campanha técnica | 14 dias de ensaio de coleta, explicitamente exploratórios | Verificar falhas, horários e cobertura; não é horizonte público de 14 dias nem teste de superioridade |
| Teste confirmatório | 12 meses consecutivos, iniciados depois de desenho e candidata congelados | Abrange um ciclo anual nos locais; não garante poder para eventos raros. Sem escolher início/fim pelo desempenho |
| Desenvolvimento/seleção | Dados exploratórios já conhecidos e novas janelas de desenvolvimento identificadas antes de coleta | Não usar outcomes confirmatórios para selecionar pesos/modelos. Validação de seleção e teste têm manifestos separados |
| Coleta | Uma rodada-alvo por dia e modelo, com antecedência auditada em horas | Horário UTC exato depende do preflight de disponibilidade; não usar o modelo "mais recente" sem registrar idade |
| Qualidade da chuva | Dia completo com todos os intervalos horários esperados válidos e sem sobreposição | Número esperado calculado pelo fuso e convenção, não fixo de 24 em dias de mudança de horário |
| Comparação principal | Uma candidata congelada contra baseline operacional arquivada, nos mesmos casos elegíveis | Outros modelos usados na seleção não viram comparações confirmatórias adicionais automaticamente |
| Relevância prática inicial | Além dos 5% aprovados como direção, discutir redução de pelo menos 0,5 mm/dia de MAE | Valor físico ainda não aprovado e precisa ser justificado pelo uso; pode ser inadequado para certos regimes |
| Proteção de extremos | Propor tolerância máxima de perda de detecção de 5 pontos percentuais e de aumento da razão de falsos alarmes de 5 pontos percentuais | Margens ainda não aprovadas; verificar também incerteza. Não aceitar só a estimativa pontual favorável |
| Estratos | Estação, horizonte, período sazonal e chuva seca/fraca/intensa com limites congelados | Não escolher cortes por desempenho. Limiares dos eventos e níveis ainda precisam ser fixados com a política e semântica observacional |
| Incerteza | Intervalo pareado de 95%, blocos temporais com proposta inicial de sete dias | Comprimento precisa de diagnóstico em desenvolvimento; respeitar agrupamento por data entre locais/horizontes. Sem bloco adequado, não alegar conclusão válida |
| Leitura do teste | Uma análise final no calendário congelado | Monitorar falhas/cobertura durante a coleta sem usar scores reservados para ajustes; qualquer acompanhamento confirmatório sequencial exige outro plano |

Uma margem de cinco pontos percentuais não é perda relativa de 5%. A proposta de tolerância operacional não autoriza degradar extremos: serve para definir um limite máximo mensurável a ser debatido. A decisão precisa considerar custo de omissão e falso alarme. Até o aceite dessas margens, continuam pendentes.

## Critério de decisão proposto

- Ganho relativo mínimo de 5% no MAE principal e ganho físico mínimo que vier a ser aprovado; intervalo pareado da diferença MAE_candidata − MAE_baseline favorável (limite superior abaixo de zero).
- Proteções de detecção/falsos alarmes avaliadas com limites de incerteza, não só médias. Estratos sem suporte ficam inconclusivos. A baseline com MAE zero torna o ganho relativo indefinido.
- Além de cobertura comum, reportar indisponibilidade de cada braço; não esconder falha em extremos na interseção dos casos completos.
- Não promover enquanto houver parâmetro crítico indefinido, comparabilidade instrumental não resolvida ou proteção sem suporte.

## O que precisa ser fechado antes de executar

Os locais, duração e valores quantitativos acima são uma proposta concreta para sua revisão. Após o aceite, ainda é necessário registrar datas exatas, metadados das estações, limiares dos eventos, versão/modelos, partições e protocolo estatístico executável. A precisão desejada e o suporte de positivos devem ser usados para verificar a viabilidade das margens; doze meses não garantem eventos suficientes. Se faltar suporte ao fim, registrar inconclusivo e propor outro estudo, sem prolongar seletivamente até conseguir resultado favorável.

Experimentos de temperatura/rajada/umidade terão alvos e tolerâncias próprios, após resolver equivalência instrumental. Não aplicar os 0,5 mm ou as margens de chuva como critério universal de todas as variáveis. Nada neste desenho muda a janela pública atual de sete dias.

[Fontes e sequência técnica](fontes-e-coleta-2026-10-23.md) · [Proposta científica completa](proposta-cientifica-para-revisao-2026-10-21.md) · [Aprovação da direção](aprovacao-direcao-2026-10-23.md).
