# Pareamento de chuva horária — 19/10/2026

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../../RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Entrega

O comparador `climaprev.tools.compare_hourly_rain` calcula o máximo dos acumulados
horários no dia civil completo de cada fonte: estação INMET, GFS e ERA5. Foram
executados 36 relatórios usando os snapshots e CSVs já preservados, sem nova coleta,
mudança de datas, ajuste de limiar ou alteração dos pais.

A auditoria existente ganhou um campo aditivo de máximo horário. Ela continua
considerando intervalos da hora anterior, com endpoints de 01h do dia até 00h do
dia seguinte, no fuso da localidade. A quantidade esperada segue o intervalo UTC
do dia civil, inclusive suas eventuais diferenças por fuso. Não se usa o acumulado
diário como proxy, uma taxa instantânea ou extremos móveis de duração sub-horária.

Mesmo que os dados disponíveis mostrem chuva forte, uma hora ausente em qualquer
fonte impede publicar o máximo pareado. Os testes verificam a meia-noite seguinte,
a exclusão da meia-noite inicial, horas ausentes em estação/modelo, valores nulos
de métricas quando não há casos e preservação do snapshot.

## Resultados diagnósticos

Foi mantida a interseção de datas da comparação de chuva anterior: **252 unidades
local/data por horizonte**. São dias com alguma hora acima do limiar, não contagem
de horas independentes ou de desastres.

| Horizonte | Dias altos na estação | Dias detectados altos pelo GFS | Falsos alarmes altos |
| --- | ---: | ---: | ---: |
| D+1 | 2 | 0 | 0 |
| D+3 | 2 | 0 | 0 |
| D+7 | 2 | 0 | 0 |

Os mesmos dois dias são reutilizados nos horizontes; não equivalem a seis
observações independentes. O recall alto nesse recorte é zero, enquanto a proporção
de falsos alarmes altos fica indefinida porque o GFS não emitiu nenhuma classificação
alta. Isso não caracteriza boa detecção nem comprova desempenho fora deste recorte.

A interpretação permanece limitada por suporte raro, representatividade espacial
e natureza dos valores de grade versus estação. Não se recomenda baixar limiares
automaticamente para encaixar esses dois eventos.

## Baseline e preflight completos

A baseline diagnóstica passou de quatro para cinco eventos: chuva horária, chuva
diária, rajada, calor e frio. A nova versão reúne **15 agregações por evento/horizonte
e 180 estratos** por evento/local/mês/horizonte. Os resultados anteriores foram
preservados como pai identificado por hash; os novos resultados horários têm
proveniência própria, incluindo código, auditor, importador e pais da campanha.

Não é reprodução integral da normalização/contrato da API ou de sua prioridade de
alertas. Não houve congelamento científico de alvos, inferência confirmatória,
ajuste, calibração ou promoção. As regras de falta de suporte, segmentos de três
dias em janeiro e critérios não aprovados continuam no preflight dos cinco eventos.

Evidências atuais:

- [Baseline dos cinco eventos](evidence/baseline-cinco-eventos-2024-2026-10-19.json).
- [Preflight dos cinco eventos](evidence/preflight-cinco-eventos-2024-2026-10-19.json).
- Os 36 relatórios detalhados estão em `.historical-reports/inmet/hourly-rain-2024-2026-10-19/`,
  ignorados pelo Git; caminhos e hashes constam na baseline.
- Script: `scripts/evaluate_hourly_rain_2024.py`, executado da raiz com `PYTHONPATH=src`;
  as saídas recusam sobrescrita e os snapshots são conferidos contra os pais originais.
- `scripts/check_station_readiness_2024.py` aceita `--baseline` e `--output` e passa
  a apontar, por padrão, para as versões dos cinco eventos, preservando as anteriores.

## Próxima dependência

Verificação técnica: 13 testes dirigidos aprovados, Ruff aprovado com EXE002
ignorado, mypy aprovado nos 61 arquivos de origem e regressão final de 574 testes
aprovada em 47,58 s. A primeira regressão teve um timeout Redis; a repetição na
imagem construída passou sem exclusões. O resultado operacional completo está
em `docs/operacoes/validacao-local-2026-10-19.md`.

Investigar representatividade espacial e semântica em experimento complementar,
preservando o recorte atual. A escolha de novas janelas, requisitos de suporte,
evento/métrica principal e critérios de ganho deve preceder os resultados de
candidatas. Reference-v1 continua ativa, sem autorização de ajuste ou promoção.
