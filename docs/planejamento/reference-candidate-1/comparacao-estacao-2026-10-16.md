# Comparação com estação e fechamento da fronteira — 16/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Avanço executado

Implementado `climaprev.tools.compare_station`, que cruza chuva diária de uma estação CSV com GFS e ERA5 pelos mesmos intervalos civis. A comparação usa apenas dias completos nas três fontes. Viés é modelo menos estação; MAE e RMSE usam os mesmos casos pareados. Ausências e endpoints faltantes ficam explícitos, e ausência de casos gera métricas nulas.

O relatório informa coordenadas da estação, configuração do experimento, distância da estação a cada grade, hashes da entrada, do CSV, do importador, do auditor e do comparador. A distância é informação para revisão, não aprovação automática da representatividade. Temperatura e rajada não são comparadas por este comando. Ele não ajusta coeficientes, não produz novos rótulos de risco e não promove política.

## Fronteira real completada em D+1

Foram coletadas duas respostas adicionais das APIs Open-Meteo para **01/02/2025**, GFS global D+1 e ERA5, nas mesmas coordenadas e timezone do piloto. Entradas e relatório nominal estão em `.historical-reports/candidate-1-pilot/belem-2025-02-01-lead-1.*.json`.

A junção derivada exige que a entrada complementar contenha exatamente o dia seguinte e confira horizonte, modelos, localização, timezone, cobertura, política de referência, fingerprints dos algoritmos, campos, unidades e metadados espaciais das respostas. Não modifica as entradas e registra hashes dos dois pais. O normalizador continua rejeitando duplicações ou timestamps desalinhados.

Resultado da auditoria com fronteira completa:

| Fonte | Dias com chuva civil completa | Total de janeiro |
|---|---:|---:|
| GFS D+1 | 31 | 353,8 mm |
| ERA5 | 31 | 351,7 mm |

Em 31/01, os valores civis são 9,6 mm no GFS e 11,7 mm no ERA5. A auditoria anterior não tinha o endpoint de 01/02 à meia-noite local e corretamente deixava esse dia incompleto. A soma nominal ERA5 original de 351,1 mm permanece preservada; não foi reescrita como soma civil.

Evidência: [auditoria-fronteira-completa-d1.json](evidence/auditoria-fronteira-completa-d1.json). A evidência inclui a proveniência das duas entradas. Isso completa a auditoria temporal D+1, sem constituir validação por estação.

## Comando para cruzamento quando houver CSV oficial

```powershell
$env:PYTHONPATH='src'
.venv/Scripts/python.exe -m climaprev.tools.compare_station --input .historical-reports/candidate-1-pilot/belem-2025-01-lead-1.inputs.json --boundary-input .historical-reports/candidate-1-pilot/belem-2025-02-01-lead-1.inputs.json --station-csv .historical-reports/inmet/A201-2025.csv --station A201 --output .historical-reports/inmet/belem-2025-01-station-comparison-d1.json
```

O caminho de CSV é proposto; o arquivo oficial ainda não está disponível localmente. O CLI recusa sobrescrever um relatório existente. Não usar fixtures sintéticas como substituto da observação real.

## Estado da validação

- **310 testes passaram, 1 foi excluído**, na regressão portátil de unitários, contratos e integração de provedores. A exclusão é a dependência anterior de AF_UNIX no Windows.
- Ruff passou, com EXE002 ignorado; mypy passou para 52 arquivos de origem, plataforma linux.
- Novos testes cobrem pareamento, direção do viés, ausência em qualquer fonte, recuperação do último dia, preservação dos pais e rejeição de fronteiras incompatíveis.
- Novo teste limitado de acesso ao ZIP oficial de 2025 retornou novamente `RemoteProtocolError`; nenhuma série de estação foi obtida.
- Redis, navegador, Docker e gates de homologação não foram executados.

## Pendências em ordem

1. Obter o CSV oficial, confirmar A201 e validar o parser com seus cabeçalhos e metadados reais.
2. Executar comparação de chuva por estação e revisar qualidade/representatividade; a discrepância documental com o boletim ainda não pode virar coeficiente.
3. Completar as fronteiras D+3/D+7 e repetir a comparação com a mesma estação e as mesmas datas.
4. Resolver comparabilidade de temperatura e rajada, ampliar a amostra e congelar o protocolo científico antes dos ajustes A/B.

Reference-v1 e snapshots originais preservados. Alterações locais em develop, sem commit/push; nenhuma candidata científica aprovada.
