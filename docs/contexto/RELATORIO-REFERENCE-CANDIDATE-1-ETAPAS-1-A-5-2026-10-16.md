# Reference-candidate-1 — relatório das etapas 1 a 5

> **Revisão contextual — 30/10/2026.** [Estado vigente](../projeto/STATE.md) · [RDP vigente](RELATORIO-PENDENCIAS-2026-10-20.md) · [Índice contextual](README.md). Versão 0.1.0; janela pública 14/7 implementada; reference-v1 ativa; piloto v5 agendado até a cota, sem ganho científico comprovado. Resultados, bloqueios e decisões datados neste documento descrevem sua época; o estado consolidado prevalece sobre checkpoints superados.

## Encerramento das pendências históricas — 20/10/2026

Além das entregas originais, foram concluídos comparações dos CSVs de três estações, suporte/bootstrapping técnico, baseline de cinco eventos, 72 snapshots espaciais, catálogo de 3.747 casos e diagnóstico horário. Restam revisão científica/proveniência/critério de aceite. Sem fitting/calibração/promoção; evolução de qualidade/precisão adiada para o final.

O restante preserva o registro do lote original. O RDP e o STATE vigentes definem a ordem atual.

<!-- estado-vigente-2026-10-20 -->
> **Sincronização documental — 20/10/2026.** Registro histórico/plano datado: o [STATE vigente](../projeto/STATE.md) e o [RDP atualizado](RELATORIO-PENDENCIAS-2026-10-20.md) definem versão, implementações, prioridades e pendências atuais. Contagens, prioridades e afirmações datadas anteriores permanecem históricas; não comprovam o estado atual nem autorização de ajuste/publicação.

> Estado consolidado mais recente: [revisão das implementações com CSV oficial](RELATORIO-REVISAO-IMPLEMENTACOES-COM-CSV-2026-10-16.md). As pendências de obtenção, compatibilidade do importador e execução observacional no piloto foram encerradas tecnicamente; as limitações científicas estão atualizadas nesse relatório.

> Atualização posterior: o CSV oficial A201 foi obtido e as comparações reais D+1/D+3/D+7 foram executadas. As pendências de acesso descritas abaixo representam o estado anterior. Consulte [RELATORIO-ACESSO-INMET-2026-10-16.md](RELATORIO-ACESSO-INMET-2026-10-16.md) para o diagnóstico reproduzível, os resultados e a divergência ainda não reconciliada com o boletim.

Data: 16/10/2026. Branch local: `develop`. Escopo autorizado: executar preparação das etapas 1 a 5 e parar antes do experimento A, etapa 6.

## Resultado executivo

Foram implementadas as comparações diagnósticas de temperatura/rajada, ampliada a coleta histórica para três localidades e quatro janelas de 2024, e congelado o desenho técnico com hashes de protocolo, dados e código. A preparação técnica avançou; **não é correto declarar todas as cinco etapas cientificamente concluídas**. A série bruta oficial do INMET continua inacessível nesta execução, impedindo validar o importador contra arquivo real e executar as comparações observacionais. A revisão científica e os critérios finais de suficiência/aceitação também continuam pendentes.

**A etapa 6 não foi iniciada.** Não foram ajustados limiares ou coeficientes, nenhuma candidata foi promovida e a reference-v1 foi preservada.

| Etapa | Estado ao encerrar | Entrega / impedimento |
|---|---|---|
| 1. Validar importador com CSV oficial | Pendente de dado externo | Importador e testes disponíveis; acesso oficial falhou e não há CSV real local. |
| 2. Cruzar estação × ERA5 × GFS | Ferramenta pronta; execução real pendente | Comparador de chuva disponível; não foram fabricadas métricas de estação. |
| 3. Comparar temperatura e rajada | Implementação técnica concluída; validação real pendente | Novo comparador com janelas, cobertura e semântica específicas por fonte. |
| 4. Ampliar amostra | Ampliação inicial executada | 36 snapshots coletados; 261 combinações local/data completas e pareadas; suficiência científica não demonstrada. |
| 5. Congelar protocolo científico | Desenho técnico e evidências congelados; aceite científico pendente | Partições, métricas, plano de incerteza e bloqueio de execução registrados. Revisor, métrica principal e suficiência ainda não aprovados. |
| 6. Ajustar classificação de risco | **Não iniciada, fora desta autorização** | Nenhum ajuste executado. |

## 1 e 2 — observações oficiais e comparação por estação

Foram verificadas novamente as rotas oficiais de [históricos anuais](https://portal.inmet.gov.br/dadoshistoricos), [catálogo](https://portal.inmet.gov.br/paginas/catalogoaut) e a API pública do INMET. O catálogo JSON foi acessível pela ferramenta web, mas isso não forneceu a série bruta de A201 nem permitiu confirmar aqui todos os seus metadados. O ZIP anual não pôde ser obtido. Tentativas locais com HTTPX e com curl/Schannel retornaram encerramento/reset da conexão; limitar a versão TLS também não resolveu. Nenhum CSV foi encontrado nos nomes de arquivo pertinentes consultados em Downloads.

A falha é de acesso externo observado nesta execução; não houve rejeição de autorização nem pedido de pagamento. Não foi contornada com espelho não oficial, gráfico convertido em valores, CSV inventado ou dados sintéticos apresentados como observação.

O que permanece disponível:

- `climaprev.tools.inmet_observations`: importação de CSV anual automático, identidade explícita, unidades, sentinelas, horários e qualidade por variável.
- `climaprev.tools.compare_station`: comparação de chuva por intervalos civis completos, métricas pareadas, distâncias e proveniência.
- Fronteiras D+1/D+3/D+7 do piloto Belém janeiro/2025 já completas.

**Para fechar essas duas etapas:** obter o arquivo oficial real, confirmar código/posição/metadados da estação, validar seus cabeçalhos no importador e executar os comparadores. A disponibilidade do código não substitui essa validação.

## 3 — temperatura e rajadas

Novo módulo: `src/climaprev/tools/compare_station_variables.py`.

| Variável/fonte | Janela aplicada | Limitação explícita |
|---|---|---|
| Rajada GFS | Endpoints posteriores à meia-noite inicial e até a próxima meia-noite, inclusive | Máximo da hora precedente. |
| Rajada ERA5 | Amostras da meia-noite inicial até antes da próxima meia-noite | Documentada como instantânea; não presumir equivalência ao máximo horário. |
| Temperatura GFS/ERA5 | Amostras instantâneas dentro do dia civil | Extremo das amostras pode perder extremos entre horários. |
| Temperatura/rajada INMET | Extremos da hora precedente encerrados dentro do dia civil | Requer cobertura integral dos intervalos e validação do sensor. |

As diferenças seguem as definições publicadas para [GFS](https://open-meteo.com/en/docs/gfs-api), [ERA5 na API histórica](https://open-meteo.com/en/docs/historical-weather-api) e [observações INMET](https://portal.inmet.gov.br/glossario/nublado). A convenção civil da chuva não deve ser aplicada indistintamente a variáveis instantâneas.

O comando calcula viés, MAE e RMSE, com os mesmos dias completos por variável nas três fontes. Informa exclusões, metadados, distâncias e hashes. Restringe a comparação aos modelos GFS global/ERA5 atualmente documentados, recusa sobrescrita e marca `calibration_ready=false`. Os testes usam fixtures sintéticas e incluem meia-noite, unidades, nulos, duplicações e DST de 23/25 horas. Não há comparação observacional real concluída sem o CSV oficial.

Exemplo de execução futura, usando os caminhos já preparados:

```powershell
$env:PYTHONPATH='src'
.venv/Scripts/python.exe -m climaprev.tools.compare_station_variables --input .historical-reports/candidate-1-pilot/belem-2025-01-lead-1.inputs.json --boundary-input .historical-reports/candidate-1-pilot/belem-2025-02-01-lead-1.inputs.json --station-csv .historical-reports/inmet/A201-2025.csv --station A201 --output .historical-reports/inmet/belem-2025-01-variables-d1.json
```

O caminho de CSV é proposto, não um arquivo existente.

## 4 — ampliação histórica executada

Novo módulo: `src/climaprev/tools/collect_campaign.py`.

O coletor usa no máximo duas coletas simultâneas, verifica e reaproveita entradas existentes, registra falhas e não ajusta candidatos. A configuração impede sair do período de ajuste, inclusive para a fronteira, e rejeita uma autorização que habilite ajuste de limiares ou calibração.

### Desenho fixado antes da coleta

- Locais: Belém, Brasília e Porto Alegre; coordenadas municipais experimentais, **não posições de estação confirmadas**.
- Ano: 2024.
- Janelas: janeiro, abril, julho e outubro; dias 1 a 28 para avaliação, dia 29 apenas como fronteira.
- Horizontes: D+1, D+3 e D+7.
- Fontes: GFS global e ERA5 via Open-Meteo; 100% de cobertura exigida para o pareamento diário da chuva.
- Não foram coletados os períodos reservados de validação e teste.

### Cobertura efetiva

| Item | Quantidade |
|---|---:|
| Snapshots previstos e obtidos | 36 / 36 |
| Respostas preservadas nesses snapshots | 72, duas por snapshot |
| Grupos local/mês | 12 |
| Combinações local/data previstas | 336 |
| Combinações local/data completas nos três horizontes | **261** |
| Combinações local/data excluídas | **75** |
| Casos de previsão pareados, contando três horizontes | **783** |

Houve cinco falhas transitórias na primeira execução. A segunda execução reaproveitou as entradas válidas e completou as cinco faltantes. As tentativas adicionais não equivalem a novos dias de avaliação.

Janeiro só forneceu três dias pareados por local, **26 a 28/01/2024**; os demais meses forneceram 28 dias por local. A cobertura parcial está documentada, sem preenchimento artificial nem substituição retrospectiva por períodos com resultados mais favoráveis.

Os 783 casos compartilham datas e horizontes: não são 783 observações independentes. A expansão soma 261 unidades local/data a partir de 87 datas de calendário, em três locais. O piloto de janeiro/2025 permanece separado.

### Suporte diagnóstico de eventos

Contagem sobre o ERA5 das 261 unidades local/data pareadas, aplicando os limiares congelados da reference-v1. Chuva usa intervalos civis; temperatura e rajada ERA5 usam extremos das amostras instantâneas. São rótulos heurísticos meteorológicos, **não observações de desastre ou impacto**.

| Evento | Baixo | Moderado | Alto |
|---|---:|---:|---:|
| Chuva horária | 261 | 0 | 0 |
| Chuva diária | 254 | 5 | 2 |
| Rajada | 225 | 36 | 0 |
| Calor | 258 | 3 | 0 |
| Frio | 259 | 2 | 0 |

**Conclusão de suficiência:** a expansão melhora a diversidade do diagnóstico, mas não demonstra amostra suficiente para otimizar detecção de risco alto nos cinco eventos. Zero suporte alto não significa bom desempenho; significa impossibilidade de avaliar esse tipo de detecção nesse recorte. Não foram estimados coeficientes a partir dessas contagens.

Evidências:

- [Primeira execução](../planejamento/reference-candidate-1/evidence/campanha-2024-etapas-1-a-5.json).
- [Execução completada e métricas por local/mês/horizonte](../planejamento/reference-candidate-1/evidence/campanha-2024-etapas-1-a-5-reexecucao.json).
- [Cobertura e suporte por evento](../planejamento/reference-candidate-1/evidence/suficiencia-diagnostica-2024.json).
- Entradas brutas preservadas em `.historical-reports/candidate-1-expansion-2024/`, ignorado pelo Git.

## 5 — congelamento técnico e protocolo

Documentos criados:

- [Protocolo legível](../planejamento/reference-candidate-1/protocolo-etapas-1-a-5.md).
- [Protocolo estruturado](../planejamento/reference-candidate-1/protocolo-etapas-1-a-5.json).

Partições documentadas: ajuste em 2024; validação julho–dezembro/2025; teste janeiro–junho/2026. O piloto Belém janeiro/2025 já inspecionado é apenas diagnóstico. A fronteira de 01/02/2025 também já foi acessada como dado auxiliar e não deve ser tratada como inteiramente inédita.

O protocolo especifica comparação pareada, estratos, métricas, tratamento de ausência de suporte e plano de bootstrap por blocos de datas, preservando a dependência entre locais/horizontes. **O bootstrap foi especificado, não implementado ou executado.**

O novo módulo `climaprev.tools.freeze_preparation` verificou os 36 pais, identidade do protocolo e unicidade do hash da política de referência. Registrou hashes dos dados e dos 56 arquivos de código de origem. A saída mantém `stage_6_authorized=false` e lista as pendências; não transforma congelamento técnico em aprovação científica.

O [manifesto de congelamento](../planejamento/reference-candidate-1/evidence/congelamento-preparacao-etapas-1-a-5.json) contém os hashes canônicos usados pelos verificadores. O hash canônico de um objeto JSON e o hash dos bytes do arquivo são conceitos diferentes e aparecem com nomes distintos.

A [auditoria dos períodos locais](../planejamento/reference-candidate-1/evidence/auditoria-periodos-locais.json) examinou 42 snapshots em `.historical-reports/` e não encontrou entradas sobrepostas aos períodos reservados. Essa conclusão se limita aos arquivos atualmente presentes; não prova ausência de acessos antigos ou em outros sistemas.

Ainda faltam para aceite científico: revisor identificado, evento/métrica principal previamente definido, ganho mínimo e tradeoffs aprovados, requisitos de suporte/precisão e observações oficiais validadas. Esses campos não foram preenchidos com metas arbitrárias para aparentar conclusão. A autorização de executar preparação não substitui a revisão científica.

## Verificação técnica

- Regressão portátil: **340 passed, 1 deselected**, cobrindo unitários, contratos e integração de provedores.
- Exclusão: teste anterior dependente de socket AF_UNIX indisponível no runtime Windows.
- Ruff: passou, com EXE002 ignorado.
- Mypy: passou, 56 arquivos de origem, plataforma linux.
- Testes novos cobrem semântica por variável/fonte, fronteiras, exclusões, restrição de períodos e rejeição de alterações no protocolo/pais.
- Testes com Redis, Docker, navegador e gates completos de homologação não foram executados neste lote.

## Estado final e próxima decisão

O trabalho para nesta entrega **antes da etapa 6**, conforme solicitado. Não houve ajuste científico, promoção, commit ou push. Alterações anteriores e arquivos de outros trabalhos locais foram preservados.

Para fechar as pendências das etapas 1 a 5, a próxima dependência é a série oficial do INMET e sua validação; em seguida, executar as comparações observacionais e aprovar os critérios científicos. Mesmo com essas pendências resolvidas, iniciar ajuste de risco exige nova autorização, pois está fora do escopo atual.
