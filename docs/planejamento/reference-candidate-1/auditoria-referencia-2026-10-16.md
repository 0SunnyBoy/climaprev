# Auditoria da referência e dos intervalos — 16/10/2026

> **Revisão contextual — 30/10/2026.** [Estado vigente](../../projeto/STATE.md) · [RDP](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) · [Refatoração e D+7](../../operacoes/refatoracao-controle-d7-2026-10-30.md). Versão 0.1.0, janela 14/7, reference-v1 ativa; infraestrutura D+7 separada implementada e desativada. Piloto v5 preservado. Resultados e decisões anteriores neste documento são registros históricos e não qualificam automaticamente novos commits.

## Encerramento das pendências históricas — 20/10/2026

As pendências históricas de CSV/importação foram superadas: CSVs oficiais de 2024 de três estações obtidos e comparados, com diagnósticos posteriores. Permanecem adequação científica, amostra rara, critérios e proveniência das reservas. As falhas de rede deste registro descrevem tentativas anteriores, não ausência atual de CSV.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../../projeto/STATE.md) e o [RDP atualizado](../../contexto/RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

## Resultado e decisão de execução

A infraestrutura experimental está operacional, mas a referência observada ainda precisa ser consolidada antes de estimar coeficientes ou modificar limiares. Esta etapa acrescenta uma auditoria offline reproduzível; não altera a reference-v1, os snapshots ou os rótulos já publicados no piloto. Não há candidata científica aprovada.

O achado principal é sensibilidade do próprio rótulo à convenção temporal: no ERA5 de Belém, em 18/01/2025, o agrupamento pela data do timestamp resulta em **31,1 mm**; o agrupamento dos intervalos da hora anterior dentro do dia civil resulta em **29,1 mm**. O limiar moderado atual é 30 mm. Assim, parte do diagnóstico inicial de subestimação depende de como definimos o alvo. Isso exige resolver a semântica antes da otimização.

## Evidências locais reproduzidas

Entrada: `.historical-reports/candidate-1-pilot/belem-2025-01-lead-1.inputs.json`, com integridade verificada pelo carregador existente. Dados coletados em 16/10/2026, janeiro/2025, GFS global D+1 e ERA5; timezone America/Belem.

| Item | Resultado |
|---|---|
| Coordenadas solicitadas | -1,4558; -48,5044 |
| Grade GFS retornada | -1,4643631; -48,515625 |
| Grade ERA5 retornada | -1,5; -48,5 |
| Chuva ERA5, soma dos timestamps de janeiro | 351,1 mm |
| ERA5 em 09/01, timestamp / intervalo civil | 8,6 / 8,8 mm |
| ERA5 em 18/01, timestamp / intervalo civil | 31,1 / 29,1 mm |
| ERA5 em 31/01, intervalo civil | Indisponível: falta endpoint de 01/02 às 00h local |

A auditoria não apresenta total mensal civil incompleto como total válido. Para cada dia informa a contagem esperada e os endpoints ausentes. As precipitações são acumuladas na hora precedente; para um dia civil de Belém, os endpoints abrangem 01h do dia até 00h do próximo dia. Em UTC, 04h até 03h do próximo dia.

Evidência completa: [auditoria-intervalos-d1.json](evidence/auditoria-intervalos-d1.json). Ferramenta: `src/climaprev/tools/audit_historical.py`.

```powershell
$env:PYTHONPATH='src'
.venv/Scripts/python.exe -m climaprev.tools.audit_historical --input .historical-reports/candidate-1-pilot/belem-2025-01-lead-1.inputs.json --output docs/planejamento/reference-candidate-1/evidence/auditoria-intervalos-d1.json
```

## Cruzamento com fontes oficiais

O [boletim INMET de janeiro/2025 para Belém](https://portal.inmet.gov.br/uploads/Balan%C3%A7o_Janeiro25_Bel%C3%A9m.pdf) informa 417,0 mm na automática, 401,4 mm na convencional e máximo em 24 horas de 56,2 mm em 09/01. A diferença aritmética entre a soma nominal ERA5 e a automática é -65,9 mm, cerca de -15,8% do total da estação. Isso é uma discrepância documental, não uma estimativa validada de viés: faltam equivalência espacial, convenção temporal e série bruta com qualidade verificada. Não foi criado um rótulo diário a partir do máximo do boletim. O texto também contém referências editoriais inconsistentes ao mês e ao ano; as médias térmicas não serão usadas para calibração sem conferência.

A [documentação Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) identifica precipitação horária como soma da hora anterior, coordenadas de retorno como centro da célula e ajuste de elevação. Valores de grade não são observações pontuais. Ela também documenta offset fixo nas respostas ISO, com limitação em transições de horário de verão. Belém não apresenta essa transição no piloto; ampliar para outros fusos exige resolver a compatibilidade temporal do coletor/normalizador.

A fonte de observação proposta é a rede automática do [INMET](https://portal.inmet.gov.br/dadoshistoricos/). A estação A201 deve ter identificação, coordenadas e metadados confirmados no catálogo e no cabeçalho do arquivo antes de entrar na comparação. Não presumimos independência estatística da estação em relação à assimilação da reanálise.

## Acesso à série bruta

O teste limitado de leitura HTTP Range do ZIP oficial de 2025 terminou em `RemoteProtocolError: Server disconnected without sending a response`. O teste não baixou o arquivo nacional e não produziu CSV de estação. A série INMET continua pendente; não atribuir cobertura nem métricas a dados que não foram obtidos. O script de diagnóstico está em `.report-work/check_inmet_range.py`.

## Ordem atualizada das próximas implementações

1. **Definir e versionar a convenção temporal do alvo.** Separar a comparação nominal compatível com o piloto da comparação por intervalos civis. Registrar timezone, natureza de cada variável e endpoints necessários.
2. **Obter e validar a série bruta automática do INMET.** Confirmar estação, posição, período operacional, unidades, sentinelas, duplicações e cobertura. Converter rajadas de m/s para km/h conforme cabeçalho; distinguir temperatura instantânea de extrema do intervalo.
3. **Coletar fronteiras adicionais e cruzar estação × ERA5 × GFS.** Preservar os snapshots originais; criar entradas derivadas/versionadas com proveniência. Não reaproveitar rótulos mudados sob o mesmo identificador.
4. **Congelar protocolo e ampliar a amostra.** Incluir sazonalidade, locais e eventos severos; manter os horizontes pareados. Os 93 casos atuais representam somente 31 datas em um local, sem alvos altos no agrupamento original.
5. **Executar A: classificação de risco.** Ajustar limiares somente no conjunto de ajuste, com alvo fixo e critérios de detecção/alarme definidos; avaliar validação sem reajuste.
6. **Executar B: calibração meteorológica.** Comparar chuva, rajada e temperatura com observação validada; congelar os coeficientes. A temperatura mínima negativa em viés frente ao ERA5 não basta para definir correção.
7. **Combinar AB e testar uma vez no período reservado.** Comparar R0/A/B/AB sobre os mesmos casos; tratar dependência entre horizontes e incerteza. Revisão científica antes de promoção e atualização coordenada dos contratos/documentos.

Os exemplos de splits no protocolo continuam ilustrativos: não constituem reserva de teste nem aprovação científica. A falha de acesso ao INMET limita essa validação externa, mas não impede preparar importador, regras de qualidade e coleta de fronteiras.

## Verificação técnica desta etapa

- Regressão portátil: **287 passed, 1 deselected**; a exclusão continua sendo o teste anterior dependente de socket AF_UNIX neste Windows.
- Ruff passou (`--ignore EXE002 --no-cache`).
- Mypy passou para os 50 arquivos de origem, usando `--platform linux`.
- Testes novos verificam passagem pela meia-noite, endpoint UTC ausente, chuva nula e preservação da entrada.
- Integração com Redis, navegador, Docker e demais gates de homologação não foram executados nesta etapa.

As mudanças permanecem locais, sem commit/push. O trabalho científico completo continua em execução; esta entrega conclui a auditoria inicial da referência, sem promover a candidata.

### Continuação: importação observacional

A preparação do importador CSV e a convenção de intervalos foram implementadas em seguida. Consulte [importacao-inmet-2026-10-16.md](importacao-inmet-2026-10-16.md) para regras, limites e resultado da regressão atualizada. A validação com CSV oficial real continua pendente.
