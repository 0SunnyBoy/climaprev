# Comparação civil dos horizontes — 16/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

Concluída a coleta das fronteiras de 01/02/2025 para D+3 e D+7, com duas respostas públicas por horizonte. A fronteira D+1 já estava disponível. Janeiro/2025 em Belém agora possui 31 datas completas nos três horizontes, sob a convenção civil da hora precedente. Os snapshots originais foram preservados.

Implementado o comando offline `climaprev.tools.compare_rain_horizons`. Ele combina cada snapshot com a sua fronteira, exige configuração e metadados de referência compatíveis, rejeita horizontes duplicados e alvos observados conflitantes. Uma data incompleta em qualquer fonte é excluída de todos os horizontes, garantindo comparação pareada. O relatório registra hashes das entradas derivadas e dos dois pais de cada junção.

## Resultado diagnóstico

Referência provisória: ERA5; previsão: GFS global. Unidade das métricas: mm de chuva diária. Viés é previsão menos referência.

| Horizonte | Datas | Viés | MAE | RMSE |
|---|---:|---:|---:|---:|
| D+1 | 31 | +0,068 | 6,165 | 7,587 |
| D+3 | 31 | -1,652 | 6,839 | 9,838 |
| D+7 | 31 | -5,916 | 9,568 | 13,318 |

Neste recorte, o erro cresce com a antecedência, e D+7 subestima a chuva na média em relação ao ERA5. O viés quase nulo D+1 não significa ausência de erro diário: erros positivos e negativos podem se compensar. Esses resultados não representam desempenho nacional, observação de estação ou melhoria de uma nova candidata.

As métricas usam a convenção civil, enquanto o piloto original usava a data do timestamp. Os relatórios anteriores permanecem válidos como registro daquele experimento; não comparar suas métricas diretamente como se a diferença fosse uma melhoria de previsão. Há somente 31 datas independentes do número de horizontes; não interpretar o conjunto como 93 dias distintos.

Evidência completa: [chuva-civil-horizontes.json](evidence/chuva-civil-horizontes.json).

## Reprodução

```powershell
$env:PYTHONPATH='src'
.venv/Scripts/python.exe -m climaprev.tools.compare_rain_horizons --input .historical-reports/candidate-1-pilot/belem-2025-01-lead-1.inputs.json .historical-reports/candidate-1-pilot/belem-2025-01-lead-3.inputs.json .historical-reports/candidate-1-pilot/belem-2025-01-lead-7.inputs.json --boundary-input .historical-reports/candidate-1-pilot/belem-2025-02-01-lead-1.inputs.json .historical-reports/candidate-1-pilot/belem-2025-02-01-lead-3.inputs.json .historical-reports/candidate-1-pilot/belem-2025-02-01-lead-7.inputs.json --output .historical-reports/candidate-1-pilot/chuva-civil-horizontes-reproducao.json
```

O CLI exige um par original/fronteira por horizonte, na mesma ordem, e não sobrescreve evidência existente. As entradas locais são verificadas por hash pelo carregador. Os arquivos brutos permanecem em `.historical-reports/`, ignorado pelo Git.

## Verificação e estado

Regressão portátil: **313 passed, 1 deselected**; exclusão anterior por AF_UNIX no Windows. Ruff passou com EXE002 ignorado, e mypy passou para 53 arquivos de origem com plataforma linux. Não foram executados gates com Redis, Docker ou navegador.

A pendência de fronteiras dos três horizontes está encerrada para este piloto. Continuam pendentes: CSV oficial real do INMET e validação do parser; comparação com estação; alinhamento de temperatura/rajada; ampliação sazonal e espacial; critérios científicos e ajuste A/B. Nenhum limiar ou coeficiente foi estimado nesta etapa. Reference-v1 preservada; alterações locais em develop, sem commit/push.
