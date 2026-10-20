# Reconciliação observacional e suporte — continuação de 19/10/2026

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../../RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Resultado

A divergência de chuva de Belém foi reconciliada numericamente sem alterar os CSVs.
O agrupamento por dia de observação encerrado às 12 UTC da data rotulada, incluindo
a fronteira de dezembro/2024, reproduz três valores do boletim oficial:

| Verificação | CSV reagrupado | Publicação |
| --- | ---: | ---: |
| Total de janeiro/2025 | 417,0 mm | 417,0 mm no texto |
| Acumulado até 30/01/2025 | 384,4 mm | 384,4 mm no gráfico, cujo último rótulo é 30/01 |
| Chuva atribuída a 09/01/2025 | 56,2 mm | 56,2 mm |

Há 744 endpoints horários esperados e completos no mês observacional. Os CSVs
anuais A201/2024 e A201/2025 foram preservados, com hashes e metadados separados.
As pequenas diferenças de coordenadas dos cabeçalhos continuam explicitadas.

Fontes primárias: [boletim de Belém](https://portal.inmet.gov.br/uploads/Balan%C3%A7o_Janeiro25_Bel%C3%A9m.pdf),
[notícia do INMET de 05/02/2025](https://portal.inmet.gov.br/noticias/balan%C3%A7o-em-janeiro-chuvas-foram-acima-da-m%C3%A9dia-em-bel%C3%A9m)
e [Normais Climatológicas, seção Cálculo do valor diário, página impressa 23](https://portal.inmet.gov.br/uploads/normais/NORMAISCLIMATOLOGICAS.pdf).
A metodologia das Normais descreve a acumulação entre as 12 UTC anteriores e as
12 UTC da data de observação, no contexto das observações convencionais. Sua
aplicação específica ao boletim automático de Belém é uma inferência fortemente
sustentada pelas três coincidências, não uma confirmação adicional enviada pelo INMET.

## Por que os diagnósticos anteriores não coincidiam

As quatro primeiras janelas começavam no próprio primeiro dia do mês. O teste
com corte às 12 UTC estava rotulado pela data inicial, indo de 01/01 às 12 UTC a
01/02 às 12 UTC. A janela que reproduz o boletim vai de **31/12/2024 às 12 UTC,
exclusive, a 31/01/2025 às 12 UTC, inclusive**. O endpoint de cada registro representa
a chuva da hora anterior; por isso, o primeiro endpoint utilizado é 31/12 às 13 UTC.

O valor de 56,2 mm aparece no dia iniciado em 08/01 às 12 UTC e encerrado em 09/01
às 12 UTC. Confundir a data de início com o rótulo de encerramento deslocava esse
evento. O fim do gráfico em 30/01 também explica por que seu acumulado final não
precisa coincidir com o total de 31 dias do texto. Não se concluiu erro do boletim.

O total civil de Belém continua sendo 427,6 mm e o agrupamento por timestamps UTC
continua sendo 427,0 mm. São perguntas temporais diferentes; esses resultados
anteriores não devem ser sobrescritos nem usados para ajustar o CSV a 417,0 mm.

Evidências: [conclusão e hashes](evidence/conclusao-reconciliacao-a201-2026-10-19.json)
e [janelas observacionais completas](evidence/reconciliacao-a201-dia-observacional-2026-10-19.json).
O comando `climaprev.tools.reconcile_station` passou a aceitar
`--previous-station-csv`; os testes rejeitam pais sobrepostos e mês sem a fronteira.

## Suporte observado nas janelas de 2024

O novo módulo `climaprev.tools.observation_support` conta suporte diagnóstico com
os limiares atuais da reference-v1, apenas nas datas completas comuns aos três
horizontes de cada variável. Não escolhe limiares, não congela alvos científicos
e não transforma níveis meteorológicos em registros de desastre ou impacto.

| Evento | Baixo | Moderado | Alto | Unidades local/data elegíveis |
| --- | ---: | ---: | ---: | ---: |
| Chuva horária | 243 | 7 | 2 | 252 |
| Chuva diária | 238 | 10 | 4 | 252 |
| Rajada | 231 | 15 | 3 | 249 |
| Calor | 219 | 29 | 0 | 248 |
| Frio | 246 | 2 | 0 | 248 |

Os nove registros altos somados por evento correspondem a seis pares local/data;
alguns dias têm mais de um evento alto. Eles não são nove ocorrências independentes,
e os três horizontes não multiplicam o suporte observacional. Não é possível avaliar
detecção de alto calor/frio neste recorte. Para chuva/rajada há suporte presente,
mas a suficiência depende dos requisitos de precisão previamente aprovados.

O diagnóstico anterior com ERA5 tinha contagens diferentes; reanálise e estação
não são fontes intercambiáveis. O CSV oficial melhora a evidência observacional,
mas diferenças de medição, qualidade instrumental e representatividade espacial
continuam precisando de revisão.

Evidência por local/mês/evento, datas altas, política e hashes:
[suporte-observacional-2024-2026-10-19.json](evidence/suporte-observacional-2024-2026-10-19.json).
Script reproduzível: `scripts/diagnose_station_support_2024.py`, executado da raiz
com `PYTHONPATH=src`. Duplicatas ou observações incompletas não viram suporte baixo.

## Próximas dependências

1. Aprovar adequação da fonte e semântica das variáveis, preservando a distinção
   entre dia civil do produto e dia de observação do boletim.
2. Definir evento/métrica principal, precisão e suporte necessários. Especificar
   ampliação adicional antes de selecionar novas janelas; preservar as reservas.
3. Somente após esses aceites, congelar os alvos e consolidar a baseline com
   incerteza e estratos. A reconciliação numérica não autoriza mudar convenções
   dos experimentos congelados ou substituir silenciosamente seus alvos.

Reference-v1 ativa; nenhum limiar ou coeficiente ajustado, candidata promovida,
commit/push ou alteração no PDF acadêmico.
