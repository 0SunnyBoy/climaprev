# Baseline observacional e critérios propostos — 19/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP vigente](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](../../contexto/README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Encerramento das pendências históricas — 20/10/2026

Baseline ampliada para cinco eventos e 180 estratos; pareamento de chuva horária, coleta espacial, catálogo e diagnóstico horário concluídos em documentos posteriores. Critérios propostos continuam sem aprovação científica; nenhuma aprovação pode ser inferida das métricas descritivas.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

**Continuação posterior:** o [pareamento de chuva horária](chuva-horaria-2026-10-19.md)
foi implementado, completando cinco eventos, 15 agregações e 180 estratos. Usar
as novas versões da baseline e do preflight referenciadas nessa continuação.
O registro abaixo preserva o diagnóstico anterior de quatro eventos; a omissão
de chuva horária nele descrita foi resolvida tecnicamente.

## Escopo do diagnóstico

Foram avaliados os limiares atuais da reference-v1 sobre os agregados experimentais
de chuva diária, rajada, calor e frio, comparados à estação nas mesmas datas de
D+1/D+3/D+7. O relatório contém 12 agregações por evento/horizonte e 144 estratos
por evento/local/mês/horizonte, com matriz de confusão, precisão, recall, F1 e
detecção de níveis pelo menos moderado e alto. GFS é a previsão; ERA5 é controle
diagnóstico, não observação de estação.

Não é reprodução integral da API: sua normalização operacional, agregação entre
eventos, picos e prioridade de alertas não foram reexecutados aqui. Não houve
congelamento científico de alvos, ajuste, candidata ou promoção. O diagnóstico é
retrospectivo/descritivo, não um teste confirmatório pré-especificado.

Chuva horária foi explicitamente omitida da classificação: os relatórios pareados
atuais não contêm máximos horários de modelo suficientes para esse cruzamento.
A contagem observacional horária anterior permanece válida como suporte; não foi
substituída por chuva diária ou outro proxy para aparentar avaliação completa.

## Resultados altos do GFS no recorte

| Evento | Horizonte | Casos pareados | Altos na estação | Detectados altos | Falsos alarmes altos |
| --- | --- | ---: | ---: | ---: | ---: |
| Chuva diária | D+1 | 252 | 4 | 0 | 1 |
| Chuva diária | D+3 | 252 | 4 | 0 | 1 |
| Chuva diária | D+7 | 252 | 4 | 0 | 0 |
| Rajada | D+1 | 249 | 3 | 0 | 0 |
| Rajada | D+3 | 249 | 3 | 0 | 0 |
| Rajada | D+7 | 249 | 3 | 0 | 1 |
| Calor | Cada horizonte | 248 | 0 | Indefinido para detecção | 0 |
| Frio | Cada horizonte | 248 | 0 | Indefinido para detecção | 0 |

Os horizontes compartilham as mesmas ocorrências: quatro dias de chuva não viram
12 observações independentes. Zero eventos altos de calor/frio não significa
detecção perfeita. Mesmo nos eventos com suporte, quantidade pequena não recebe
aprovação automática de suficiência.

Exemplo do efeito do desbalanceamento: em D+1, a chuva diária tem acurácia de
92,46%, mas nenhum dos quatro altos foi detectado; a detecção de pelo menos
moderado acertou 1 de 14 casos. A acurácia agregada sozinha esconderia a falha
nos casos de maior interesse. O ERA5 também não detectou esses quatro altos,
reforçando a necessidade de investigar representatividade e semântica, sem
atribuir automaticamente toda a discrepância a um coeficiente corrigível.

Esses resultados não justificam baixar limiares diretamente: uma mudança de
classificação pode aumentar falsos alarmes sem melhorar os valores meteorológicos.
Temperatura e rajada ainda misturam amostragem instantânea e extremos de intervalo.

## Preflight de suficiência

As datas elegíveis agrupadas têm 87 datas de calendário em quatro segmentos de
3, 28, 28 e 28 dias. O segmento de janeiro tem três dias, menos que o bloco primário
de sete dias previsto no protocolo. A implementação atual de bootstrap suprime
o intervalo nessa situação; não foi executada inferência para contornar o bloqueio.

Não excluir janeiro depois de olhar os resultados para produzir um intervalo
favorável. Uma eventual revisão deve manter o resultado original visível, justificar
novo desenho e identificar as análises exploratórias, inclusive sensibilidades
de três e 14 dias. As escolhas não são automaticamente aceitas por estarem implementadas.

## Critérios técnicos propostos para a próxima revisão

| Decisão | Proposta de procedimento | Estado |
| --- | --- | --- |
| Referência | Aprovar qualidade instrumental, posições, unidades e convenções; preservar dia civil do produto e dia observacional do boletim separados. | Revisão pendente |
| Objetivo principal | Escolher evento/métrica pela necessidade do produto, antes dos resultados de qualquer candidata; não escolher agora o indicador mais favorável. | Evento/métrica continuam sem aprovação |
| Suporte | Definir precisão desejada e suporte por evento, região e horizonte, considerando dependência temporal e espacial. Não adotar número mínimo arbitrário. | Requisitos numéricos pendentes |
| Ausência de evento | Manter recall/ganho de detecção indefinidos; impedir conclusão de melhora nesse estrato. | Regra diagnóstica aplicada |
| Incerteza | Avaliar segmentos adequados, blocos, réplicas indefinidas e degeneração; registrar sensibilidades sem promover análise exploratória a confirmatória. | Infraestrutura disponível; inferência pendente |
| Ganho e falsos alarmes | Aprovar ganho mínimo relevante, tolerância a perdas e custo de falsos alarmes, aplicados a todos os estratos críticos. | Valores/tradeoffs pendentes |
| Reservas | Auditar acessos anteriores e independência da validação/teste antes de nova avaliação; nenhum acesso novo a esses períodos neste lote. | Revisão pendente |
| Congelamento | Versionar dados, alvos, código e critérios após os aceites, preservando os protocolos anteriores. | Não realizado cientificamente |

Esta proposta não altera o protocolo congelado nem define limiares numéricos de
aprovação retroativamente. A etapa de ajuste continua fora da autorização atual.

## Evidências e reprodução

- [Baseline final](evidence/baseline-observacional-2024-final-2026-10-19.json).
- [Preflight e decisões ainda abertas](evidence/preflight-observacional-2024-2026-10-19.json).
- `scripts/evaluate_station_baseline_2024.py`, da raiz com `PYTHONPATH=src`; aceita
  `--output` e recusa sobrescrita. Verifica os hashes de todos os relatórios pais.
- `scripts/check_station_readiness_2024.py`, da raiz com `PYTHONPATH=src`.

O arquivo preliminar `baseline-observacional-2024-2026-10-19.json` preserva a primeira
execução deste lote. Usar o arquivo com `final` acima como referência atual; ele
acrescenta a limitação explícita sobre reprodução da API e os hashes do código final.

Próximas implementações: completar o pareamento de máximos de chuva horária sem
mudar a convenção, estudar o efeito espacial em experimento complementar e fechar
o desenho de ampliação. Esses passos podem avançar tecnicamente sem ajustar a v1.
